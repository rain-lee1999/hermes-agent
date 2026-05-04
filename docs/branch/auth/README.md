# auth 分支说明

最后更新：2026-05-04

## 一句话概括

这个分支维护 Hermes 的 Codex/OpenAI 账号选择、Menubar 排序同步、运行时粘性与额度刷新触发逻辑：同一会话应保持已绑定账号，Menubar 排名应同步到 Hermes auth pool，100% 且 5 小时窗口未启动的账号可用极小 Codex 请求触发一次刷新锚点。

## 为什么要做这个 branch

- Hermes 使用 `openai-codex` 时，账号状态分布在多个层面：`~/.codex/auth*.json`、`~/.hermes/auth.json` 的 `credential_pool.openai-codex`、以及 `providers.openai-codex.tokens` singleton。
- CodexMaintainerMenubar 已经负责观察多账号额度并生成排序后的 `last-menu-rows.json`，Hermes 需要跟随这个排序，而不是自己重新发明排序。
- 同一个 Hermes session 内，一旦绑定了可用账号，后续 turn / 辅助任务应复用该账号；只有新 session、`/new`、首次 delegate 或真实 failover 才应重新选择。
- 部分 Codex 账号在 5 小时额度仍为 100% 时，服务端显示的刷新时间会一直像“5 小时后”。需要发一个最小请求，让刷新窗口从该次使用后开始计时。
- 触发刷新必须非常保守：不能疯狂触发，也不能污染当前 Hermes 会话上下文或破坏 prompt/cache 语义。

## 关键概念

### Session 绑定的 runtime credential

- 一个 Hermes session 选中可用 pool entry 后，应把它视为该 session 的 runtime credential。
- 后续追加消息优先复用绑定结果，而不是每轮从磁盘重新加载 pool 并按 priority 选头部。
- 新 session 仍可按 Menubar/Hermes pool priority 选择当前最高优先级可用账号。

### 主路径 vs 辅助路径

- 主对话 turn 经过 `cli.py` 和 `run_agent.py`。
- 压缩、标题、记忆/技能等辅助调用经过 `agent/auxiliary_client.py`。
- auth 分支早期 bug 是：主路径看似粘住，但辅助路径仍可能重新 `load_pool().select()`，导致同 session 追加消息看起来“跳账号”。

### Menubar-first 排序同步

- `~/Library/Application Support/CodexMaintainerMenubar/last-menu-rows.json` 已经是 Menubar 排序后的真相。
- `scripts/reorder_codex_by_menubar_quota.py` 保留该文件顺序；第一行成为 Hermes `openai-codex` priority 0，并同步 provider singleton。
- 同步脚本还会把 entry 的 label/source/imported_from/account_id/token 材料与对应 `~/.codex/auth*.json` 文件重新对齐，避免“标签像 A，token 其实是 B”的假象。

### 5 小时 prime / 刷新锚点触发

- 当 Menubar row 满足：`usageState=ok`、`fiveHourRemainingPercent == 100`、`fiveHourResetAt`/trend 仍表现为完整 5 小时窗口时，说明这个账号可能还没有真正启动 5 小时刷新计时。
- `--prime-full-five-hour` 会对该账号发一个独立的极小 Codex Responses 请求：
  - `instructions`: `Reply with exactly: .`
  - `input`: `.`
  - `store`: `false`
- 请求不走当前 Hermes `AIAgent`，不会写入当前 session transcript，也不会改变当前会话上下文。
- 为防短时间重复触发，脚本有两层去重：
  - `row_id + fiveHourResetAt` 已 prime 则跳过。
  - 同 `row_id` 成功 prime 后 5 小时冷却，即使 `fiveHourResetAt` 短时间滑动也跳过。

### repo-local 代码 vs installed runtime

- 本文档描述的是 `/Users/rain/dev/-github/-worktree/hermes-agent-auth` 的 repo-local branch 状态。
- `~/.hermes` 是 installed/runtime profile；auth 文件、prime state、logs、LaunchAgent 安装态属于运行时状态，不自动等同于 repo diff。
- 当前代码改动不会直接把真实 token 写进文档；所有账号材料都应继续视为敏感运行时状态。

## 改动前的设计

- `_ensure_runtime_credentials()` / auxiliary client 某些路径可能在每个 turn 重新解析 runtime。
- `openai-codex` 辅助客户端路径可能重新从 pool 选择 priority 最高账号，破坏同 session 粘性。
- Menubar -> Hermes 同步早期只关心 pool 排序，不足以覆盖 provider singleton 漂移、entry token/label 不一致、重复 manual entry 等情况。
- `HermesCodexAccountSyncWatcher` 只运行 `reorder_codex_by_menubar_quota.py --apply --quiet`，不会处理 100% 五小时额度账号的刷新锚点。
- 如果 100% 账号的 `fiveHourResetAt` 看起来一直在未来 5 小时，Hermes 不会主动发最小请求启动刷新窗口。

## 改动后的设计

- CLI / run_agent / auxiliary 路径保留 session-bound runtime credential，辅助任务不应无故重选账号。
- Menubar 排序文件顺序被 Hermes 同步脚本原样保留，并写入 `credential_pool.openai-codex` priority。
- provider singleton 从 primary pool entry 同步，减少直接 reader 与 pool reader 不一致。
- watcher 现在调用：
  - `reorder_codex_by_menubar_quota.py --apply --prime-full-five-hour --quiet`
- sync 脚本新增 5 小时 prime：
  - 候选检测基于 `fiveHourRemainingPercent`、`fiveHourResetAt`、`fiveHourTrendPoints`。
  - 通过 Codex Responses endpoint 发最小非存储请求。
  - 状态写入 `~/.hermes/codex-five-hour-prime-state.json`。
  - 每账号成功 prime 后 5 小时冷却，防止 watcher 轮询导致疯狂触发。
- watcher 日志会输出 prime 摘要计数：
  - `five_hour_prime_candidates`
  - `five_hour_prime_triggered`
  - `five_hour_prime_failed`

## 主要行为 / 用户可见效果

- 同一 Hermes session 连续追加消息时，账号不会无缘无故切回权重最高账号。
- 新 session 仍按 Menubar 同步后的 pool priority 选择首个可用账号。
- Menubar 排序更新后，Hermes auth pool 与 provider singleton 会尽量收敛到同一个第一账号。
- 对 5 小时额度仍为 100% 且刷新时间像“永远 5 小时后”的账号，watcher 可自动发一个最小请求来启动刷新锚点。
- 该最小请求不加入当前 Hermes 对话历史，不改变当前 prompt 前缀；只会对目标 Codex 账号产生一次极小使用量。
- 若 Menubar 短时间内仍看不到额度变化，同账号 5 小时冷却会阻止重复触发。

## 相关文件

### 核心实现

- `cli.py` — CLI session runtime/credential 绑定与 `/new` 等边界。
- `run_agent.py` — 主 agent 与辅助任务之间的 runtime 传播。
- `hermes_cli/runtime_provider.py` — runtime dict 与 selected credential 元数据。
- `agent/auxiliary_client.py` — auxiliary LLM 路由与 Codex runtime credential 处理。
- `agent/credential_pool.py` — pool entry、provider singleton sync、credential refresh/failover。
- `scripts/reorder_codex_by_menubar_quota.py` — Menubar row -> Hermes auth pool 同步、provider singleton sync、5 小时 prime 逻辑。
- `scripts/HermesCodexAccountSyncWatcher` — 轮询 watcher，触发同步和 5 小时 prime。
- `scripts/install_codex_menubar_sync_watcher.py` — LaunchAgent 安装 helper。
- `scripts/macos-login-items.md` / `scripts/install_macos_login_items.sh` — repo-owned macOS background item manifest/install pattern。

### 回归测试

- `tests/cli/test_cli_provider_resolution.py`
- `tests/cli/test_cli_new_session.py`
- `tests/agent/test_auxiliary_main_first.py`
- `tests/agent/test_auxiliary_client.py`
- `tests/agent/test_codex_cloudflare_headers.py`
- `tests/agent/test_credential_pool_routing.py`
- `tests/run_agent/test_run_agent.py`
- `tests/scripts/test_reorder_codex_by_menubar_quota.py`
- `tests/scripts/test_codex_menubar_sync_watcher.py`
- `tests/scripts/test_setup_hermes_launchagent_install.py`

## 当前 scoped work（2026-05-04）

本轮未提交改动集中在 4 个文件：

- `scripts/reorder_codex_by_menubar_quota.py`
  - 新增 `--prime-full-five-hour` 与 `--prime-model`。
  - 新增候选检测、最小 Codex Responses 请求、prime state、每账号 5 小时冷却。
- `scripts/HermesCodexAccountSyncWatcher`
  - watcher 调用 sync 时带上 `--prime-full-five-hour`。
  - watcher 摘要中加入 prime candidates/triggered/failed 计数。
- `tests/scripts/test_reorder_codex_by_menubar_quota.py`
  - 覆盖候选检测、最小请求 payload/header、每账号冷却。
- `tests/scripts/test_codex_menubar_sync_watcher.py`
  - 覆盖 watcher 会启用 `--prime-full-five-hour` 并解析 prime 摘要。

## 验证状态

最近一次验证：

- `gitnexus analyze`：通过，重新索引当前 worktree。
- GitNexus pre-change impact：`main` / `sync_entries` 风险 LOW；改动集中在 sync 脚本流程。
- RED：新增 prime/cooldown 测试先失败，确认测试覆盖缺失行为。
- `scripts/run_tests.sh tests/scripts/test_reorder_codex_by_menubar_quota.py::test_five_hour_prime_candidates_require_full_quota_and_full_reset_window tests/scripts/test_reorder_codex_by_menubar_quota.py::test_prime_five_hour_row_posts_minimal_codex_response -q`：2 passed。
- `scripts/run_tests.sh tests/scripts/test_reorder_codex_by_menubar_quota.py::test_prime_full_five_hour_rows_respects_per_account_cooldown -q`：1 passed。
- `scripts/run_tests.sh tests/scripts/test_reorder_codex_by_menubar_quota.py tests/scripts/test_codex_menubar_sync_watcher.py -q`：9 passed。
- `python3 scripts/reorder_codex_by_menubar_quota.py --quiet`：dry-run JSON 正常，未 apply 时不触发 prime。
- `git diff --check`：通过。
- GitNexus detect-changes：risk medium；受影响流程集中在 `scripts/reorder_codex_by_menubar_quota.py` 的 main/load_json/label/quota 相关路径，符合预期。

注意：auth worktree 没有自己的 venv；测试时临时创建 `venv -> /Users/rain/hermes-agent/venv` symlink 以使用项目 wrapper，测试后已删除。

## base diff caveat

与 `upstream/main` 的三点 diff 包含本分支历史上其他主题的累计改动（Bark 插件、update 分支文档、API recovery 文档等）。本 README 聚焦 auth branch 语义和当前 scoped auth/Codex account work；不要把 `upstream/main...HEAD` 的所有文件都理解成本轮任务范围。

## 推荐阅读顺序

1. `docs/branch/auth/ai-brief.md`
2. `scripts/reorder_codex_by_menubar_quota.py`
3. `scripts/HermesCodexAccountSyncWatcher`
4. `agent/credential_pool.py`
5. `agent/auxiliary_client.py`
6. `run_agent.py`
7. 相关 tests/scripts 回归测试

## 后续维护说明

- 新增任何 auxiliary LLM 路由，都要确认它不会绕开 active session 的绑定 credential。
- 修改 Menubar/Hermes 同步时，必须同时考虑 pool order、provider singleton、entry token/label truth、运行时 reader 的真实选择。
- 5 小时 prime 必须保持保守：最小请求、非存储、成功后冷却、失败不锁死。
- 不要把 repo-local branch docs 与 `~/.hermes` installed runtime 状态混淆；真实 auth/token/prime state 不应进入 git 文档。
