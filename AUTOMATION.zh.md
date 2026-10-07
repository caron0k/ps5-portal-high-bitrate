# 常驻中继预览:Windows、Linux 与 macOS

作者已在一台 Mac mini 上用真实的 PS5/Portal 确认了最初的常驻原型。本版本把那套单向设计移植到了一个通用引擎上。**Windows 自动模式仍待真机验证。已有一位社区测试者报告 Linux / 树莓派的安装、重启与重连成功;崩溃恢复和更广泛的兼容性仍未验证。** 通用引擎的 macOS 服务打包不在本版本内,原有的 macOS 手动启动器仍然可用。这是社区测试预览版,不提供任何保证。

## 它改变了什么

留一台电脑保持开机、不休眠,并与你的 PS5 和 Portal 处于同一个直连的 IPv4 局域网。中继主机建议用以太网。只登记这两台设备,并在路由器里为它们保留 IP。不需要 USB 连接。

该服务会持续地把**仅 Portal → PS5** 方向的控制/出站流量重定向经过这台电脑,并对每个匹配到的新会话启动包施加所选的 65/100/200 Mbps 请求改写。而 PS5 → Portal 的视频流走直连路径。这与手动启动器不同——后者是在一个有边界的实验结束后就退出路径。控制路径上仍然多了一跳;延迟未测量。本项目不会增加 4K、超分或 200 Mbps 持续吞吐的保证。

包结构判定与推断偏移,和最初的手动启动器有着同样的固件局限性。`unique_modified_startups` 计数只能证明本地发出过一次改写。最终结果必须由 Portal 画面和可玩会话来确认。自动模式不会拦截主机的码率响应,因此**无法报告 PS5 是否接受**。

## Windows 10/11 预览

1. 下载并解压新的预览版 ZIP 到一个可信的本地文件夹。不要把旧版本的文件混进来。
2. 安装来自 [python.org](https://www.python.org/downloads/windows/) 的 **64 位 Python 3.10+**。用于开机任务的 Python,请用完整安装程序,选择为所有用户安装到 `C:\Program Files`,并安装 Python 启动器(launcher)。Microsoft Store 版或仅当前用户的 Python 不适用于 SYSTEM 任务。
3. 安装 [Npcap](https://npcap.com/#download),并启用 WinPcap API 兼容模式。需要的是普通以太网帧;**不要**开启 Wi-Fi 监听模式。本项目不捆绑 Npcap。若安装程序要求重启,请重启。
4. 运行 `Setup-Windows.cmd`。它会创建 `.venv`、安装锁定版本的 Scapy 依赖并跑离线测试。如果 `py -3` 选中的是仅当前用户的 Python,请先用那个「所有用户」Python 的完整路径重建 `.venv`,再继续。
5. 开启 PS5 和 Portal。右键 `Auto-Windows.cmd` → **以管理员身份运行**,输入 `Configure`,首次测试用档位 `65`。选择连接着你 PS5/Portal 所在局域网的那块以太网/Wi-Fi 网卡的**菜单编号**,然后输入两台设备的 IPv4 地址。网卡旁打印出来的本机 IP 仅供参考。较早的 preview.1 会要求输入网卡名/GUID:请填网卡名或完整的 Npcap 设备 ID,**绝不要**填本机 IP。它们的 MAC 地址只登记在本地。不要使用 VPN、访客网络或客户端隔离。
6. 断开 Portal 的游戏会话。以管理员身份打开同一个菜单,选择 `Baseline`。出现 **BASELINE READY** 后连接 Portal,在 60 秒内检查画面和操控。这一步只转发、不改码率。只有当出站流量确实被转发、且守护进程自己也报告已干净地把 ARP 交还回去时,才会保存一份回执。它不会自动验证视频或响应性。
7. 接着选择 `Confirm-Baseline`。它会显示上一条基线转发了多少个**未做任何改动**的出站包,并要求你在确认当时画面与操控都正常后输入 `CONFIRMED`。**这是后面所有改写的前提**:若没人亲眼确认过基线状态,"改完之后能玩"就失去了对照意义。不输入即视为未确认,任何档位都不会被启用。
8. 若基线已确认,选择 `Run` 做一次前台实测。出现 **AUTO READY** 后断开/重连 Portal。检查 Portal 的网络显示,并玩一段动态画面。用 Ctrl+C 停止,并等待恢复完成。**如果这一步失败,就不要安装计划任务。**
9. 只有在上述测试都通过后才选择 `Install`。安装程序会要求你确认基线观察结果。它会把一份文件白名单复制到 `C:\ProgramData\PortalBitrateAuto` 下仅 Administrators/SYSTEM 可访问的目录,创建自己的虚拟环境,并在任务计划程序中以 SYSTEM 身份、开机触发注册 `PortalBitrateAutoPreview`。随后立即启动该任务。**不会保存任何账号密码或令牌。**
10. 用 `Status` 同时检查任务计划程序和带时间戳的中继报告。再次断开/重连 Portal,然后重启电脑并重复一次,以验证无人值守启动。游戏期间请保持电脑不休眠。

`Start`、`Stop`、`Status`、`Uninstall` 都在同一个管理员菜单里。`Stop` 会写入一个持久的停用标记,并等待优雅恢复。被停用的任务在重启后仍保持停用,直到执行 `Start`。`Uninstall` 会注销任务,但保留私有文件以便排查。**不要**强行结束正在运行的守护进程,也不要在恢复完成前删除文件。

如果安装时拒绝了 Python 路径,请为所有用户重装 Python 并重建源目录的 `.venv`。如果守护进程无法脱离 Windows job 对象,或无法在 SYSTEM 下打开 Npcap,启动会在重定向流量之前就失败。请把该失败报告出来,**不要**把这个检查删掉。任务注册成功并不代表中继真的能工作。

## 原生 Linux 预览

初期目标:Debian/Ubuntu 系的原生 Linux,带以太网、Python 3.10+、iproute2、libpcap 和 systemd。其它发行版需要安装等价的软件包。下文有一份树莓派 3B(树莓派 OS)的社区成功报告;但该报告未提供系统架构/版本,因此**ARM64 兼容性尚未确立**。WSL、基于 NAT 的 Docker/虚拟机网络、Android 和路由器固件都不是受支持的部署目标。下面另有一节描述实验性的 Proxmox LXC / Linux Docker macvlan 路径。

```sh
sudo apt update
sudo apt install python3 python3-venv python3-pip iproute2 libpcap0.8
# 在解压出来的发布目录里:
sh Auto-Linux.sh setup
sh Auto-Linux.sh configure 65
```

configure 这一步会询问物理局域网网卡(例如 `eth0` 或 `enp3s0`)和两台设备的 IPv4 地址。用 `ip -br link` 和 `ip -br addr` 查你自己的。登记时两台设备都必须处于唤醒状态。

1. 断开 Portal 的游戏会话。运行 `sh Auto-Linux.sh baseline`,出现 **BASELINE READY** 后再连接。在这 60 秒「不改包」的中继试用中检查画面和操控。
2. 亲眼确认画面与操控正常后,运行 `sh Auto-Linux.sh confirm-baseline` 并按提示输入 `CONFIRMED`。未确认则下一步会被拒绝:本分支认为,"产生了差分效应"必须相对于一个被人确认过的对照状态才有意义。
3. 若可用,运行 `sh Auto-Linux.sh run`。出现 **AUTO READY** 后连接,检查 Portal 画面并开始游玩。Ctrl+C 会停止并修复它的 ARP 条目。
4. **只有**在前台实测成功之后,才运行 `sh Auto-Linux.sh install`。它会要求你确认基线观察结果。安装会把 root 拥有的代码和 venv 放到 `/opt/portal-bitrate-auto`,私有运行时文件放到 `/var/lib/portal-bitrate-auto`,并注册一个名为 `portal-bitrate-auto` 的 systemd 服务。
5. 用 `sh Auto-Linux.sh status` 检查。重连 Portal,然后重启 Linux,以验证在你的硬件上能自动启动。

```sh
sh Auto-Linux.sh stop
sh Auto-Linux.sh start
sh Auto-Linux.sh status
sh Auto-Linux.sh uninstall
# 日志,仅供本地排查:
sudo journalctl -u portal-bitrate-auto -n 50 --no-pager
```

Stop 的效果会跨重启保持,直到执行 Start。Uninstall 会停用/移除该 unit,但保留私有代码/配置/日志供你复查。升级时**有意拒绝覆盖**已有安装:请先 stop/uninstall,备份私有数据,删除旧的安装目录,再用新版本重做 setup/baseline。

## 社区 Linux 反馈(2026-09-30)

[测试者 tissee 报告](https://www.reddit.com/r/PlaystationPortal/comments/1wtyglf/comment/pd2k5ls/):在一台 EndeavourOS 笔记本和一台走以太网的树莓派 3B(树莓派 OS)上使用成功。在树莓派上,该测试者确认了 systemd 开机自启、Portal 全新重连,以及 PS5 从待机唤醒时 100 Mbps 档位可用。但他未提供确切的发行版版本、系统架构、持续视频吞吐和输入延迟。这属于社区报告,不是维护者跑的基准测试,也不构成普遍兼容性保证。崩溃恢复和长时稳定性仍需验证。

该测试者还需要解决 IPv4 转发被 Docker 开启/重新开启的问题。我们的中继在检测到转发已开启时会拒绝启动,并且**不会**去改动这个设置。[Docker 文档](https://docs.docker.com/engine/network/packet-filtering-firewalls/#docker-on-a-router)说明它的常规 iptables 后端会在启动时开启转发,而 Docker 桥接网络本身就需要转发。在共享的 Docker 主机上关掉它可能会破坏容器网络。当这些要求冲突时,请用一台专用的中继主机;不要盲目关闭转发,也不要删掉中继的这个检查。该报告针对的是原生 Linux,不是在 Docker 里跑这个中继。

## Proxmox LXC 与 Docker(社区贡献)

[deploy/](deploy/README.md) 可以把同一个中继跑在 Proxmox VE 上桥接的无特权 Alpine LXC 里,或者跑在 `macvlan` 网络的 Linux Docker 容器里。两种方式都会让中继在 PS5/Portal 局域网上拥有自己的 MAC 和网络命名空间。转发只在这个文档说明的容器内部被关闭。Proxmox 有一份贡献者用真实 PS5 和 Portal 的报告;Docker 只有来自贡献者 fork 的合成测试,没有真机验证。这些都是可选的实验性部署。同样的基线、前台实测和重启检查依然适用。**Proxmox 方案的作者关闭的是新建中继 CT 那块网卡上的过滤(`firewall=0`),而不是主机全局防火墙;请先阅读部署指南里的防火墙作用范围和测试局限。** 贡献者:[SDNick484,PR #1](https://github.com/atameric/ps5-portal-high-bitrate/pull/1)。

## 恢复机制与局限

一个独立的守护进程会监视中继的管道/心跳。在正常停止或进程失败时,它会发送纠正性 ARP 应答;若中继卡死,它会先终止确切的父进程再修复。修复未确认时会留下一个恢复标记阻止重启。在 Linux 上,服务会给守护进程一段宽限期,之后才按进程组终止。Windows 上(若操作系统允许)会使用一个独立于任务 job 的进程组。

断电、拔网线、主机休眠、抓包驱动故障,或两个进程同时被终止,都可能导致无法修复。请重连 Portal 以刷新它的网络状态,并检查主机日志。正因如此,每个平台都仍需要做一次真实的崩溃/重启测试。如果残留了恢复标记,请先停用任务/服务并确认没有中继或守护进程在跑,然后用已安装的 Python 和已安装的 `--runtime` 目录执行 `portal_auto.py repair`。它会要求输入 `STOPPED` 才会发送修复帧。**不要**为了让第二个中继跑起来而删除一个正在生效的锁。

原生的 Windows / systemd 服务不会开启 IP 转发、不会改防火墙、不会开放远程控制端口,也不会改固件;但若发现转发已经开启,它会拒绝启动。可选的容器部署有它自己的转发和网卡过滤设置,见上文。请保持 DHCP 地址保留稳定。启动时若观测到冲突的存活 ARP 应答,已变更的 MAC 登记会被拒绝。这**不是**针对恶意局域网的防御手段。

要更换档位或设备地址,请按上文流程:停用/卸载服务 → 重新 configure → 重跑基线 → 重新安装。请从 65 起步;100/200 是要求更高的目标,可能增加卡顿或延迟,却未必带来可见收益。

## 安全地分享测试结果

请使用 [TESTING.zh.md](TESTING.zh.md)。分享:操作系统/版本、网卡类型、Windows 上的 Npcap 版本、档位、基线/前台/开机自启/重连是否成功、显示区间与卡顿情况。发布前请从错误信息中移除个人信息。**不要上传** `auto-config.json`、含有真实登记的 `config*.json`、`auto-runtime`、ProgramData/var-lib 运行时目录、抓包文件、环境文件、令牌或密钥。自动模式不保留原始抓包或会话负载;但日志/状态里仍含有本地运维信息。
