# update 分支说明

最后更新：2026-05-02

## 一句话概括

这个分支把 `hermes update` 收敛成“默认优先从本地 source checkout 更新代码、尽量不自动改写 `~/.hermes` 用户数据”的更新流程，并让启动 banner / `hermes update --check` 使用同一套本地更新源判断。

## 为什么要做这个 branch

- 本机有多个 Hermes checkout，用户希望 `hermes update` 的默认来源明确、可控：优先从 `/Users/rain/dev/-github/hermes-agent/` 的 `main` 更新，而不是直接跟 GitHub fork/upstream 走。
- `/Users/rain/.hermes` 被视为外部持久化数据区；代码更新不应该顺手覆盖或迁移会话、记忆、凭据、历史任务、用户技能等状态。
- 旧的 update 流程把“拉代码”“同步 bundled skills”“配置迁移提示/交互”“更新检查”混在一起，容易让用户难以判断 update 到底会碰哪些数据。
- 启动 banner 的 update 检查如果仍看 `origin/main`，会和真正的 `hermes update` 来源不一致，造成“提示有更新但实际更新源不同”的错觉。

## 关键概念

### 本地 update source checkout

- 新 helper：`hermes_cli/update_source.py`。
- 解析顺序：
  1. `HERMES_UPDATE_SOURCE_REPO`，当它指向一个 git checkout 时优先使用。
  2. 当前 repo 名如果以 `-update` 结尾，则使用去掉后缀后的 sibling repo。
     - 对本 checkout：`/Users/rain/dev/-github/hermes-agent-update` → `/Users/rain/dev/-github/hermes-agent`。
  3. sibling `hermes-agent` checkout。
- helper 只负责“保守识别可用本地 checkout”；识别不到时调用方继续走原来的远程 fallback。

### 默认最少触碰 `~/.hermes`

- `hermes update` 的主目标是更新代码和依赖。
- update cache 仍可能被清理：`.update_check` 以及 profiles 下对应缓存。
- bundled skills 同步不再默认执行，改为 `--sync-skills` 显式开启。
- 配置迁移不再混入 update 主流程；update 只报告可迁移内容，并提示用户之后单独运行 `hermes config migrate`。
- zip 级 pre-update backup 默认关闭，可用 `--backup` 强制开启；`--no-backup` 可覆盖配置中的开启项。
- 注意：当前代码仍保留轻量 quick snapshot 保护逻辑，在发现有新 commit 并真正拉取前尝试创建 `create_quick_snapshot(label="pre-update")`；这不是完整 zip 备份，也不代表 update 会清空用户数据。

### Repo 分支 vs 已安装 runtime

- 本文档描述的是 repo `/Users/rain/dev/-github/hermes-agent-update` 的分支状态。
- 已安装的 `hermes` 命令可能来自另一个 checkout 或已安装 profile；除非这些改动被合并/安装到实际 runtime，否则 repo-only 修改不会自动改变已安装命令行为。

## 改动前的设计

- `hermes update` 在 git 模式下主要围绕 `origin/main` / fork upstream 同步逻辑运行。
- 当当前 repo 是 fork 时，流程会提示 fork，并在安全条件下考虑 upstream sync。
- `hermes update --check` 和启动 banner 的检查也主要按远程 `origin/main` 或 upstream 语义判断。
- update 成功后默认同步 bundled skills 到当前 profile 和其他 profiles，直接触碰 `~/.hermes/skills/` 与 profile 技能镜像。
- update 流程会把配置迁移/缺失配置处理放在主更新路径里，存在改写 `config.yaml` / `.env` 的风险或至少造成“update 会管理配置”的语义混淆。

## 改动后的设计

- `hermes_cli/update_source.py` 集中解析本地更新源。
- `hermes update --check`：
  - 如果找到本地 source checkout，则执行 `git fetch --quiet <source> main`。
  - 用 `HEAD..FETCH_HEAD` 计算落后 commit 数。
  - 找不到本地 source 时才回退到原远程检查。
- `hermes update`：
  - 如果找到本地 source checkout，则显示 `Updating from local source checkout`。
  - fetch/pull 使用 `<source> main`。
  - 比较使用 `FETCH_HEAD`。
  - fast-forward 不可用时，reset 目标也改为 `FETCH_HEAD`。
  - 找不到本地 source 时保留原 fork/origin/upstream fallback。
- `hermes_cli/banner.py`：
  - 启动 update 检查也调用 `resolve_local_update_source_repo(...)`。
  - 缓存加入 `repo_dir` 与 `source_repo` 字段，避免不同 repo/source 共用旧 `.update_check` 结果。
- `hermes update` 对 `~/.hermes` 的默认触碰被收窄：
  - bundled skills 默认跳过，提示 `use --sync-skills to enable`。
  - config drift 只报告，不自动迁移。
  - zip backup 维持显式/配置控制，不默认创建。

## 主要行为 / 用户可见效果

- 在本 checkout 中，`hermes update` 现在应优先指向：
  - `/Users/rain/dev/-github/hermes-agent/` 的 `main`
- 只有本地 source 不存在或不可识别时，才走远程 fallback。
- `hermes update --check` 与启动 banner 的 update 检查不再和主 update 来源分裂。
- `hermes update` 成功后默认会打印 bundled skills sync skipped，而不是自动同步 bundled skills。
- 如果检测到配置版本或缺失配置，update 会提示之后运行 `hermes config migrate`，而不是自动写 `~/.hermes/config.yaml` / `~/.hermes/.env`。
- 需要同步 bundled skills 时，用户必须显式运行：
  - `hermes update --sync-skills`
- 需要完整 pre-update zip backup 时，用户必须显式运行：
  - `hermes update --backup`

## 相关文件

### 核心实现

- `hermes_cli/update_source.py` — 本地 update source checkout 解析。
- `hermes_cli/main.py` — `hermes update`、`hermes update --check`、backup/config/skills 同步边界。
- `hermes_cli/banner.py` — 启动 banner 的 update 检查和 `.update_check` cache 语义。
- `hermes_cli/tips.py` — CLI tips 中 update/skills 同步提示文案。

### 回归测试

- `tests/hermes_cli/test_update_source.py` — 本地 source helper 行为。
- `tests/hermes_cli/test_update_check.py` — banner/update check 缓存与本地 source 行为。
- `tests/hermes_cli/test_cmd_update.py` — update 主流程、本地 source 优先、skills 同步默认跳过/显式开启。
- `tests/hermes_cli/test_update_yes_flag.py` — `--yes` 不再触发配置迁移，stash restore 仍自动确认。
- `tests/hermes_cli/test_update_autostash.py` — update autostash 既有覆盖。
- `tests/hermes_cli/test_backup.py` — backup 相关覆盖。

### 相关但非本分支核心

- `hermes_cli/backup.py` — zip backup / quick snapshot 实现。
- `hermes_cli/config.py` — config drift / migration helper。
- `tools/skills_sync.py` — bundled skills 同步实现；现在由 `--sync-skills` 显式触发。
- `hermes_cli/profiles.py` — profile 技能镜像同步入口；同样受 `--sync-skills` 控制。

## 验证状态

本次文档维护阶段已执行：

- `git rev-parse --show-toplevel`：`/Users/rain/dev/-github/hermes-agent-update`
- `git branch --show-current`：`update`
- `git status --short`：当前仍有 update 相关源码/测试变更未提交，并新增本文档文件。
- `git diff --stat`：源码/测试改动主要集中在 `hermes_cli/banner.py`、`hermes_cli/main.py`、`hermes_cli/tips.py` 和 update 测试文件。
- `date +%F`：`2026-05-02`

此前本分支针对 update 变更已报告通过：

- `scripts/run_tests.sh tests/hermes_cli/test_update_source.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_update_autostash.py -q`：`40 passed`
- `scripts/run_tests.sh tests/hermes_cli/test_cmd_update.py tests/hermes_cli/test_update_yes_flag.py tests/hermes_cli/test_update_check.py tests/hermes_cli/test_update_source.py -q`：`22 passed`
- `scripts/run_tests.sh tests/hermes_cli/test_backup.py -q`：`93 passed`

本次只维护文档，没有重新跑完整测试套件。

## 推荐阅读顺序

1. `docs/branch/update/ai-brief.md`
2. `hermes_cli/update_source.py`
3. `hermes_cli/main.py` 中 `_cmd_update_check()`、`_cmd_update_impl()` 和 update argparse 定义
4. `hermes_cli/banner.py` 中 `check_for_updates()` / `_check_via_local_git()`
5. `tests/hermes_cli/test_update_source.py`
6. `tests/hermes_cli/test_cmd_update.py`
7. `tests/hermes_cli/test_update_check.py`

## 后续维护说明

- 如果以后再次调整 update 来源，先改 `resolve_local_update_source_repo(...)`，再让 `cmd_update`、`--check`、banner 复用同一套语义。
- 不要把 config migration、skills sync、profile seeding 重新混回默认 update 主路径；如果必须触碰 `~/.hermes`，优先做显式 flag 或独立命令。
- 修改 update cache 语义时，要同时考虑 default profile 和 named profiles 下的 `.update_check`。
- 修改 `--yes` 行为时，保持“自动确认 stash restore，但不自动输入/迁移 API key 或 config”的边界。
- 对本机而言，文档中的 repo 分支变化不等于已安装 `hermes` 立即变化；需要合并/安装到实际 runtime 后才生效。
