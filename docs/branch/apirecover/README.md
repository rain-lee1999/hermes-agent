# apirecover 分支说明

最后更新：2026-05-02

这个分支的目标，不是简单把某个 timeout 调大，而是把 Hermes 的 API 卡住/失败处理，改成一套可分层、可恢复、可观测的策略。

如果你只想先抓主线：
1. 先看本文件的“改动前/后设计”
2. 再看 `ai-brief.md`
3. 然后看 `docs/specs/api-recovery-strategy.md`
4. 最后回到 `run_agent.py` 和 `cli.py`

## 一句话概括

这个分支把“API 调用失败”从“等一个固定超时再说”改成了：
- streaming 走真实 provider activity 监控
- non-streaming 按 provider/model/context bucket 选 stale timeout
- 可恢复 transport failure 会显式暴露状态
- CLI 会在合适时机自动补一个 `?` 恢复探针

## 这条分支里最重要的概念

### 1) Streaming vs non-streaming

- streaming：只要 provider 还在持续吐出真实 activity，就不该被误判成 stale
- non-streaming：没有增量事件，不能靠“有没有输出”判断是否卡住，必须用 timeout policy

### 2) Stale timeout 不是单点常量

非 streaming 的 stale timeout 不是写死一个值，而是按优先级选择：
1. `providers.<id>.models.<model>.stale_timeout_seconds`
2. `providers.<id>.stale_timeout_seconds`
3. `HERMES_API_CALL_STALE_TIMEOUT`
4. context bucket 默认值
5. `300s` 只作为最后兜底

### 3) Context bucket

当没有显式 timeout 配置时，系统会按上下文规模分桶：
- small
- medium
- large
- huge
- unknown

目的不是“拍脑袋调参”，而是让不同大小的调用走不同的恢复节奏。

### 4) Visible transport recovery

recoverable transport failure 不再只是内部错误，而是会被翻译成可见状态：
- `transport_failure[recovery_pending]`
- `transport_failure[recovered]`
- `transport_failure[recovery_failed]`

并附带 `visible_transport_auto_recovery`，让 CLI / operator 知道当前走的是哪条恢复 lane。

### 5) `?` recovery probe

当 CLI 看到可恢复 transport failure，而且用户没有已经在排队的 interrupt message 时，会自动补一个 `?`。

这个 `?` 不是随便重试，而是“探测这条 recovery lane 是否已经恢复”的轻量动作。

## 改动前的设计

改动前的体验更像是“一个比较粗的统一超时模型”：

- streaming 和 non-streaming 的恢复语义没有完全分开
- non-streaming stale timeout 更容易被单一默认值主导
- recoverable transport failure 对 CLI/operator 的可见性不足
- 没有清晰的 recovery pending / recovered / failed 状态链
- 用户往往只能看到“卡住了”或“报错了”，但看不到系统正在尝试恢复

换句话说，之前更像“超时后再处理”，而不是“根据调用形态和上下文选择恢复策略”。

## 改动后的设计

### 1) Streaming 路径

- 只看真实 provider activity
- 只要 activity 还在更新，就不轻易判 stale
- 这样可以避免把长输出误判成卡死

### 2) Non-streaming 路径

- timeout 先看显式配置
- 如果没显式配置，再按 context bucket 选默认值
- bucket 本质上是“上下文越大，容忍度越高，但仍有上限”的策略层

### 3) 恢复状态链

- 失败时先进入 `recovery_pending`
- 若自动恢复成功，进入 `recovered`
- 若恢复失败，进入 `recovery_failed`

这样 CLI 和测试都能区分“正在恢复”和“已经恢复/失败”。

### 4) CLI 行为

- CLI 监听 agent 的 lifecycle 状态
- 看到 `transport_failure[recovery_pending]` + `visible_transport_auto_recovery` 时，标记需要 probe
- 若用户没有已经输入 interrupt message，就自动 queue 一个 `?`
- 如果用户已经有自己的中断/指令，则尊重用户输入，不额外插 probe

### 5) 测试设计

这条分支的测试重点不是 snapshot，而是行为约束：
- timeout 优先级是否正确
- stale 计数是否会在失败后继续累积
- 成功后是否正确 reset
- recovery 状态标签是否有完整链路
- CLI 是否只在没有用户 interrupt 时才自动补 `?`
- status bar / operator surface 是否仍保持真实

## 相关文件

### 核心实现
- `run_agent.py`
- `cli.py`
- `hermes_cli/plugins.py`

### 回归测试
- `tests/hermes_cli/test_timeouts.py`
- `tests/run_agent/test_api_recovery_strategy.py`
- `tests/cli/test_cli_api_recovery_probe.py`
- `tests/cli/test_cli_status_bar.py`

### 设计文档
- `docs/specs/api-recovery-strategy.md`
- `docs/plans/api-recovery-strategy-plan.md`

## 推荐阅读顺序

如果你想最快搞懂这条分支：

1. `docs/branch/apirecover/ai-brief.md`
2. `docs/specs/api-recovery-strategy.md`
3. `run_agent.py` 里和 stale / recovery 相关的方法
4. `cli.py` 里和 `_on_agent_status` / `_queue_auto_recovery_probe_if_needed` 相关的方法
5. 对应测试文件

## 为什么还要再放一份给 AI 读的文件

有必要，而且这条分支很适合这么做。

原因很简单：
- 这类 branch 的功能范围通常很小、很固定
- 未来更多是小修小补，而不是整仓库重新理解
- 新开会话时，AI 最需要的是“这条 branch 的主线、关键不变量、入口文件”
- 把这些压成一份短文件，可以显著减少首次上下文成本

所以这个目录里保留两份：
- `README.md`：给人读，带一点解释和上下文
- `ai-brief.md`：给 AI 读，尽量短、尽量结构化

## 这条分支现在的定位

这条分支的核心不是“修一个 bug”，而是把 API 恢复策略变成一条完整的产品/运行时路径：
- 有明确的分类
- 有明确的 timeout 选择层次
- 有明确的恢复状态
- 有明确的 CLI 行为
- 有明确的测试约束

后面如果再微调，通常只需要改 timeout policy、状态文案、或者补一个小的回归测试。