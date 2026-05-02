# auth 分支说明

最后更新：2026-05-02

## 一句话概括

这个分支修复了“同一个 session 追加消息时会反复选回权重最高账号”的问题：会话一旦绑定了可用凭据，就应继续复用它，而不是每轮又从池子头部重新挑选。

## 为什么要做这个 branch

- 之前只修到了 CLI 的主入口，实际的辅助路由链路还是会在每次 turn 里重新 `select()` 账号。
- 用户看到的现象是：同一 session 里，只要追加一条消息，账号就又跳回最高优先级那一项。
- 这说明问题不在“新会话初始化”，而在“同一 session 的后续 turn / 辅助任务”仍在重新解析 runtime。
- 这个分支把“session 粘性”从 CLI 表层扩展到辅助路由层，避免主路径和辅助路径行为不一致。

## 关键概念

### Session 绑定的 runtime credential

- 一旦某个 session 已经选中了一个可用账号，这个账号应当作为该 session 的绑定 runtime。
- 后续追加消息应优先复用这个绑定结果，而不是重新从磁盘加载 pool 再按 priority 选头部。

### 主路径 vs 辅助路径

- 主对话 turn 经过 `cli.py` 和 `run_agent.py`。
- 压缩、标题、记忆/技能等辅助调用经过 `agent/auxiliary_client.py`。
- 之前的 bug 就藏在辅助路径里：主路径看起来粘住了，但辅助路径仍然会重选账号。

### repo-local 代码 vs installed runtime

- 本次改动同时同步到了 `/Users/rain/hermes-agent` 和 `/Users/rain/dev/-github/hermes-agent-auth` 两个工作树。
- 这不等于已经修改了 `~/.hermes` 下的安装态配置或账号文件；installed profile 仍然是另一层状态。
- 后续排查时要区分“仓库代码已经修好”与“本机已安装运行态是否重新加载”。

## 改动前的设计

- `_ensure_runtime_credentials()` 会在每个 turn 里重新解析 runtime。
- `openai-codex` 的辅助客户端路径仍会走 `_build_codex_client()` / `_select_pool_entry()`。
- 每次 `load_pool()` 后调用 `select()`，都会回到 priority 最高的那个账号。
- 结果就是：同 session 的追加消息看起来像“账户在跳”，实际上是辅助链路在重新选号。

## 改动后的设计

- CLI 在 active session 内复用已绑定的 pool credential。
- `run_agent.py` 传给辅助客户端的 `main_runtime` 保留了当前绑定账号的 `api_key / base_url / api_mode`。
- `agent/auxiliary_client.py` 在 `openai-codex` 场景下优先使用显式 runtime credential，不再强制回到 pool reselection。
- 只有在没有可复用的 session 绑定凭据，或者真失败转移时，才会重新走池子选择。

## 主要行为 / 用户可见效果

- 同一 session 连续追加消息时，账号不会再无缘无故切回权重最高账号。
- 新 session 仍然可以按既有优先级正常选首个可用账号。
- 真正的 auth failure / failover 仍然允许切换到备用凭据。
- 辅助任务（压缩、标题等）与主对话现在共享同一条 session 粘性语义。

## 相关文件

### 核心实现

- `cli.py`
- `run_agent.py`
- `hermes_cli/runtime_provider.py`
- `agent/auxiliary_client.py`
- `agent/credential_pool.py`

### 回归测试

- `tests/cli/test_cli_provider_resolution.py`
- `tests/agent/test_auxiliary_main_first.py`
- `tests/agent/test_codex_cloudflare_headers.py`

### 参考/旁路文件

- `tests/run_agent/test_streaming.py`
- `tests/cli/test_cli_new_session.py`

## 验证状态

- `scripts/run_tests.sh tests/cli/test_cli_provider_resolution.py::test_active_session_keeps_bound_pool_credential_instead_of_reselecting_top -q`: 通过
- `scripts/run_tests.sh tests/agent/test_auxiliary_main_first.py::TestResolveAutoMainFirst tests/agent/test_codex_cloudflare_headers.py -q`: 通过（21 passed）
- `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY -u XAI_API_KEY -u DEEPSEEK_API_KEY -u MISTRAL_API_KEY -u TOGETHER_API_KEY -u AZURE_OPENAI_API_KEY TZ=UTC LANG=C.UTF-8 PYTHONHASHSEED=0 /Users/rain/hermes-agent/venv/bin/python -m pytest tests/cli/test_cli_provider_resolution.py::test_active_session_keeps_bound_pool_credential_instead_of_reselecting_top -q`: 通过
- `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY -u XAI_API_KEY -u DEEPSEEK_API_KEY -u MISTRAL_API_KEY -u TOGETHER_API_KEY -u AZURE_OPENAI_API_KEY TZ=UTC LANG=C.UTF-8 PYTHONHASHSEED=0 /Users/rain/hermes-agent/venv/bin/python -m pytest tests/agent/test_auxiliary_main_first.py::TestResolveAutoMainFirst tests/agent/test_codex_cloudflare_headers.py -q`: 通过（21 passed）
- auth 工作树里没有单独的 venv；验证时复用 `/Users/rain/hermes-agent/venv`，结果正常。

## 推荐阅读顺序

1. `docs/branch/auth/ai-brief.md`
2. `cli.py`
3. `hermes_cli/runtime_provider.py`
4. `agent/auxiliary_client.py`
5. `tests/cli/test_cli_provider_resolution.py`

## 后续维护说明

- 新增任何辅助路由时，都要检查它是否会绕开 active session 的绑定 credential。
- 不能再让 `openai-codex` 这类路径默认退回“每次重新从 pool select”的行为。
- 如果以后再碰到“同 session 账号跳变”，优先查 runtime 传播链，而不是只盯 CLI 表层。
- 本分支的 docs 在两个工作树里保持同一份事实，但不要把它和 `~/.hermes` 的 installed runtime 混为一谈。
