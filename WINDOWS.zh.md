# Windows 社区预览 —— 真机验证尚未完成

若要使用新的常驻自动模式,请看 [AUTOMATION.zh.md](AUTOMATION.zh.md)。本指南只覆盖有边界的手动会话。

本预览版与 macOS 版共用同一套数据包改写逻辑,但在原生 Windows 10/11 上使用 Npcap。**它还没有在任何 Windows 硬件上实际运行过。** 请不要把本地离线测试描述成 Windows 运行时验证。

请先安装带 `py` 启动器的 [Python 3.10+](https://www.python.org/downloads/windows/)(用 `py -3 --version` 验证)以及 [Npcap](https://npcap.com/#download),然后解压整个 ZIP 并运行 `Setup-Windows.cmd`。按 Scapy 的安装建议,**不要勾选** WinPcap 兼容模式;也不需要 monitor/raw 802.11 支持。仅管理员可访问 Npcap 与这些提权启动器是兼容的。请只在同一个直连局域网上使用你自己的两台设备;所选网卡必须已禁用 IPv4 转发。本工具不改动防火墙、注册表或 IP 转发设置。

请按顺序以管理员身份运行以下文件:

1. `Configure-Windows.cmd`:选择局域网网卡,输入当前的 PS5/Portal IPv4 地址。
2. `Check-Windows.cmd`:只读检查,以及对两个对端的 ARP 解析。
3. `Baseline-Windows.cmd`:断开 Portal,回车,出现 READY 之后再重连。这是一个不改写负载的有边界中继,用于检验「是否被接受」和清理是否正常。请肉眼确认游玩正常。
4. `Start-Windows.cmd`:先用 65;只有在基线成功且游玩正常之后,才分别单独测试 100/200。每次测试都需要在 READY 之后开一个全新的 Portal 会话。

中继时间窗是 40 秒(含预热),安装和清理还会额外耗时。一个脱离主进程的 50 秒看门狗必须先发出就绪信号,才会改动 ARP。一个整机范围的命名内核对象会阻止在同一台 Windows 机器上并行跑多个实验。不要同时运行 Mac 版中继。Ctrl+C 会触发清理;而断电是同一台电脑上的看门狗无法恢复的。

独立的本地出包验证使用一个单独的 Npcap 句柄,并且**只保存哈希值,不保存原始包**。这不能证明远端确实收到了。成功发出恢复包,也不独立证明两个对端更新了各自的 ARP 缓存。分辨率字段不会被改动。输入延迟和持续码率均未做基准测试。

若恢复出错,请保持电脑开机至少 60 秒,并检查 `experiments/<run>/recovery-state.recovery.json` 和 `watchdog.log`。确认没有实验或看门狗在跑之后,可以在提权终端里重试 `".venv\Scripts\python.exe" portal_windows.py --restore "experiments\<run>\recovery-state.json"`。**只使用本工具自己生成的**状态文件。必要时请重连两端设备的网络接口。正常断开/重连 Portal 即可撤销码率请求。

不要公开配置、恢复状态或基线回执;它们含有本地网络标识。只分享脱敏后的 `report.json`,加上 Portal 的帧率/分辨率/码率和主观响应感受。本项目不内含原始密钥/固件/会话数据,也不发送遥测。

[English](WINDOWS.md) | [Türkçe](WINDOWS.tr.md)

## 逐步下载与安装

1. 打开仓库的 **Releases**,选择 **Windows Community Preview**,在 **Assets** 下下载名为 Windows 的 ZIP。它**故意**被标记为 **Pre-release**。
2. 右键该 ZIP → **全部提取**。把解压出来的文件放在同一个本地文件夹里。不要直接在 ZIP 内部运行文件,也不要复用 Mac 的 `.venv`。
3. 用上面的官方链接安装 Python 及其启动器,打开一个新的命令提示符,运行 `py -3 --version`,必须显示 Python 3.10 或更高。如果 `py` 不存在,请先修复 Python 启动器安装再继续。**WSL 不受支持。**
4. 从其官网安装 Npcap,选项如上所述。安装驱动后请重开终端。不需要 Wireshark、Git 或 USB 线。发布版 ZIP 不捆绑 Python 和 Npcap。
5. 双击 **Setup-Windows.cmd**。它会创建本地 `.venv`、安装锁定版本的 Scapy 依赖并跑离线测试。下载依赖需要联网。只有测试以 `OK` 结束才继续。
6. 右键 **Configure-Windows.cmd** → **以管理员身份运行**,接受 Windows UAC 提示。选择物理局域网网卡,不要选 VPN 或回环。从 PS5/Portal 的网络设置页或路由器 App 输入当前的设备地址。这一步只写本地配置;不要上传它。
7. 右键 **Check-Windows.cmd** → **以管理员身份运行**。只有显示 `CHECK PASSED` 才继续。如果它报出 Npcap、路由、转发或对端解析错误,请停下来并报告脱敏后的错误。**不要**为了让它通过而去关防火墙。
8. 断开 Portal 会话、保持 PS5 开机,然后右键 **Baseline-Windows.cmd** → **以管理员身份运行**。回车。**只有**出现 READY 之后才开启新的 Portal 会话。等到 `Baseline passed`,并在恢复完成后确认画面/操控正常。若失败,不要进入码率改写阶段。
9. 再次断开,以管理员身份运行 **Start-Windows.cmd**。选择 **65**,回车,等 READY,然后连接。结果成功后,观察一段 30–60 秒的动态画面。**只有**在前面的档位都表现良好时,才在各自独立的新会话里测试 **100** 和 **200**。
10. 用 **Windows preview test result** 开一个 issue。**成功和失败都请报告。** 我们正是靠这种方式才能确定 Windows 实现在各种网卡上到底能不能用。

## 已验证与未验证的部分

合成测试和 ZIP 解包是在 macOS 上测过的。它们覆盖:精确的密文差值、包长度/校验和、确认门控、配置校验以及模拟的恢复路径。以下各项**仍未验证**:Windows 原生执行、物理网卡上的 Npcap 注入、PS5 是否真的接受,以及 Windows 上的 Portal 播放。GitHub 托管的测试还可能因维护者账号的 runner 可用性而被阻塞;请查看实际的运行状态,不要假定 CI 是绿的。

请在自己的设备上测试。驱动不兼容或清理被中断,都可能暂时打断两台设备的连接。有边界的中继和看门狗降低了这个风险,但不是保证。**请先报告任何恢复问题,再重复运行。** 标称 200 Mbps 的档位只是一个实验性请求;在 Mac 原型上它产生了大约 158–166 Mbps 的主机目标码率,而不是经过验证的持续 200 Mbps 流量。

- `0`:所选阶段满足了软件判据;仍请实际检查画面/操控。
- `1`:阶段未确认。对 200 而言,**即使会话是正常工作的**,目标码率也可能稳定在 160 Mbps 确认阈值之下。
- `2`:发生了错误;请阅读错误信息和恢复字段。不要盲目反复重试。

参考:[Scapy Windows 安装说明](https://scapy.readthedocs.io/en/stable/installation.html#windows)。
