# auth 分支说明

最后更新：2026-05-02

## 一句话概括

这个分支把 macOS 的登录项 / LaunchAgent 安装收进 `./setup-hermes.sh` 的收尾流程里，并把 Codex Menubar 的账号顺序同步 watcher 一起装好、拉起来，让 Hermes 能持续跟随 menubar 权重更新账号顺序。

## 为什么要做这个 branch

- 这个分支的目标不是再造一套登录项安装逻辑，而是把“安装、验证、启动”收敛成一条可重复的路径。
- `CodexMaintainerMenubar` 里保存的账号顺序是持续变化的外部状态，必须靠 repo-owned watcher 同步，不能依赖用户手工跑脚本。
- 如果安装步骤分散在多个地方，`./setup-hermes.sh` 很容易“看起来成功了，但 watcher 没拉起来”，后续账号顺序就会和 menubar 脱节。
- 这个分支强调薄入口 + 可扩展 helper：以后新增 macOS 背景项，只需要补清单，不要继续膨胀主安装脚本。

## 关键概念

### Launchd Label vs. Item

- `Item` 只是展示标题，给人读的。
- `Launchd Label` 才是 launchd、测试和验证命令真正依赖的稳定标识。
- 这能避免不同脚本各自发明名字，导致安装和验证对不上。

### 登录项清单是单一来源

- `scripts/macos-login-items.md` 是 macOS 登录项 / LaunchAgent 的 source of truth。
- `scripts/install_macos_login_items.sh` 负责解析这个清单，并按 `## Item:` 分节顺序逐项安装。
- 失败会立刻中止 setup，避免“脚本报成功但后台项其实没装上”的假阳性。

### Menubar 权重同步

- `scripts/HermesCodexAccountSyncWatcher` 是长期运行的 watcher，用来盯住 menubar 的持久化顺序和 auth snapshot。
- `scripts/install_codex_menubar_sync_watcher.py` 负责把 watcher 安装成 LaunchAgent。
- `scripts/reorder_codex_by_menubar_quota.py` 负责根据 menubar / quota 状态做一次性的重排或同步。
- 这条链路的核心是“保持账号顺序跟随 menubar”，而不是每次重新随机选号。

## 改动前的设计

- `setup-hermes.sh` 没有统一负责 macOS 登录项的安装、验证和启动。
- LaunchAgent / Login Item 的安装逻辑更容易散落到各处，新增条目时要改主脚本。
- watcher 和 setup 之间缺少明确的收尾连接，容易出现安装步骤完成但后台服务没启动的情况。
- 登录项信息如果写死在 shell 里，后续扩展新条目会越来越难维护。

## 改动后的设计

- `setup-hermes.sh` 末尾只保留一行委托：调用 `scripts/install_macos_login_items.sh`。
- helper 在非 macOS 上直接 no-op，在 macOS 上读取 `scripts/macos-login-items.md`。
- watcher 对应的 LaunchAgent 由独立 installer 负责，安装后立即 `kickstart`，并交给 launchd 常驻。
- 清单里明确定义了 `Launchd Label`、installer、验证命令，方便未来再加条目。

## 主要行为 / 用户可见效果

- 用户在仓库根目录运行 `./setup-hermes.sh` 后，macOS 会自动安装所需的登录项 / LaunchAgent。
- `Codex Menubar -> Hermes auth sync watcher` 会被立即拉起，而不是只写 plist 不启动。
- 后续 menubar 账号权重变化时，Hermes 能通过这个 watcher 维持账号顺序同步。
- 新增类似后台项时，通常只需要追加 `scripts/macos-login-items.md`，不必重构 setup 主流程。

## 相关文件

### 核心实现

- `setup-hermes.sh`
- `scripts/install_macos_login_items.sh`
- `scripts/macos-login-items.md`
- `scripts/install_codex_menubar_sync_watcher.py`
- `scripts/HermesCodexAccountSyncWatcher`
- `scripts/reorder_codex_by_menubar_quota.py`

### 回归测试

- `tests/scripts/test_setup_hermes_launchagent_install.py`
- `tests/scripts/test_codex_menubar_sync_watcher.py`
- `tests/scripts/test_reorder_codex_by_menubar_quota.py`

### 参考文档

- `website/docs/user-guide/features/credential-pools.md`

## 验证状态

- `git rev-parse --show-toplevel`：`/Users/rain/dev/-github/hermes-agent-auth`
- `git branch --show-current`：`auth`
- `git log --oneline --decorate --graph upstream/main..HEAD --max-count=20`：当前分支相对 `upstream/main` 只有 1 个独立提交，`386a5c5c8`
- `date +%F`：`2026-05-02`
- 本次 docs 更新没有重新跑代码测试；此前已经验证过 `bash -n setup-hermes.sh`、`python3 -m py_compile ...`，以及针对 setup / watcher / quota 的 targeted pytest 均通过。

## 推荐阅读顺序

1. `docs/branch/auth/ai-brief.md`
2. `scripts/macos-login-items.md`
3. `setup-hermes.sh`
4. `scripts/install_macos_login_items.sh`
5. `tests/scripts/test_setup_hermes_launchagent_install.py`

## 后续维护说明

- 如果以后再加 macOS 背景项，优先新增 `scripts/macos-login-items.md` 的一个 `## Item:` 分节，而不是继续往 `setup-hermes.sh` 里堆分支逻辑。
- `Launchd Label` 必须继续作为测试和验证的唯一稳定标识。
- 任何“看似安装成功，但 watcher 没启动”的问题，都应该先检查 helper、launchctl 验证和 plist 位置，而不是先改主 setup 流程。
- 账号顺序同步要保持 menubar 的既有排序语义，不要把它重新排序成另一个不透明规则。