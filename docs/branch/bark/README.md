# bark 分支说明

最后更新：2026-05-02

## 一句话概括

这个 branch 把 `bark_macos_notify` 从“只把文件复制过来”补成了 Hermes 插件系统里能被发现、默认启用、并能在实际 hook 上触发 Bark + macOS 通知的可用实现。

## 为什么要做这个 branch

- 之前的问题不是“插件文件有没有放进仓库”，而是“它会不会真的被 PluginManager 加载并在运行时触发”。
- 仅靠把插件目录拷贝到 `plugins/`，并不能保证它会进入 `plugins.enabled`，也不能证明 hook 链路能跑通。
- 用户关心的是实际通知是否生效，而不是目录里有没有一个看起来像插件的文件夹。
- 这个 branch 也刻意把“仓库里的改动”和“已安装的 `~/.hermes` 运行副本”分开处理：前者已经修好，后者要等 merge / reinstall 才会跟上。

## 关键概念

### 插件发现 vs 插件启用

`plugin.yaml` 被扫描到，只代表插件“存在”；是否真正加载，还要看启用策略。

### `default_enabled`

这个 branch 给 bundled standalone plugin 增加了默认启用语义。它允许 `bark_macos_notify` 在没有手动写进 `plugins.enabled` 时也能被加载；但 `plugins.disabled` 仍然优先。

### Hook 驱动通知

通知不是靠轮询，而是靠 Hermes 已有的 hook 机制：
- `pre_tool_call`
- `post_llm_call`
- `on_session_finalize`
- `on_session_reset`

### 双通道通知

插件同时支持 Bark 和 macOS 本地通知，两条路径都是可降级、可选配的：缺配置就静默跳过，不硬失败。

## 改动前的设计

- 插件文件可能存在，但没有可靠的默认启用链路。
- standalone 插件仍然更偏向显式 allowlist，而不是“仓库自带即启用”。
- 没有回归测试证明 `PluginManager -> register(ctx) -> invoke_hook()` 这条链路真的把通知打出来。
- 已安装的 `~/.hermes` 运行环境和当前仓库是两套东西；只改 branch 不会自动修好本机已安装副本。

## 改动后的设计

- `plugins/bark_macos_notify/plugin.yaml` 声明了 `default_enabled: true`。
- `hermes_cli/plugins.py` 读取并尊重 `default_enabled`。
- `plugins/bark_macos_notify/__init__.py` 通过 `register(ctx)` 把四个 hook 注册进插件系统。
- `post_llm_call` 会在任务完成或等待状态时发通知；`pre_tool_call` 会在需要用户输入时发通知；`on_session_finalize` / `on_session_reset` 作为兼容性的会话边界通知路径，默认是更保守的。
- Bark 发送依赖 `BARK_URL`；macOS 通知依赖系统能力和 `osascript`，在非 macOS 或能力缺失时会退化为 no-op。
- 这份改动只在仓库 branch 内生效；要让 `/Users/rain/.hermes` 里的实际 Hermes 生效，仍然要 merge / reinstall 这份代码。

## 相关文件

### 核心实现

- `hermes_cli/plugins.py`：插件发现、启用判断、加载与 hook 注册的核心逻辑。
- `plugins/bark_macos_notify/__init__.py`：Bark/macOS 通知实现、hook 处理、注册入口。
- `plugins/bark_macos_notify/plugin.yaml`：插件元数据与 `default_enabled` 声明。

### 回归测试

- `tests/plugins/test_bark_macos_notify_plugin.py`：验证 manifest、通知构造、过滤逻辑、hook 行为、默认启用与真实 PluginManager 加载。
- `tests/hermes_cli/test_plugins.py`：回归现有插件系统，确认这次改动没有破坏通用插件加载。

### 设计文档

- 无单独 spec / plan 文件；这次改动主要由代码和测试本身定义行为。

## 验证状态

- `python -m pytest -q tests/plugins/test_bark_macos_notify_plugin.py tests/hermes_cli/test_plugins.py`：通过。
- `mcp_crg_detect_changes_tool`：3 个 changed files，0 个 affected flows。
- 未重新跑全量 `scripts/run_tests.sh`。

## 推荐阅读顺序

1. `docs/branch/bark/ai-brief.md`
2. `plugins/bark_macos_notify/plugin.yaml`
3. `plugins/bark_macos_notify/__init__.py`
4. `hermes_cli/plugins.py`
5. `tests/plugins/test_bark_macos_notify_plugin.py`
6. `tests/hermes_cli/test_plugins.py`

## 后续维护说明

- 不要把 `default_enabled` 和 `plugins.disabled` 的优先级搞反。
- 不要让 Bark / macOS 通知在缺配置、缺能力或非 macOS 场景下硬失败。
- 不要把敏感的 Bark key、URL token 或其他凭据写进文档或日志。
- 如果以后加新的通知 hook，记得同时补 `PluginManager` 层面的加载/触发测试。
- 如果要让用户机器上的 `~/.hermes` 立刻生效，必须把这份 branch 合并或重新安装进去；仅仅改仓库不会自动影响已安装 profile。
