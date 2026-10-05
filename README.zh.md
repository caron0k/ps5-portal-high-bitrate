# PS5 Portal High Bitrate —— 中文说明

**社区预览版:Windows / Linux 自动模式 + 可选的 Proxmox / Docker 部署。** [下载 v0.3.0-preview.3](https://github.com/atameric/ps5-portal-high-bitrate/releases/tag/v0.3.0-preview.3) |[自动安装(中文)](AUTOMATION.zh.md) | [Automatic setup (EN)](AUTOMATION.md) | [Otomatik kurulum (TR)](AUTOMATION.tr.md) | [容器部署指南(实验性,EN)](deploy/README.md)。包含 Windows 手动启动器,以及一个常驻单向中继,并提供 Windows 任务计划程序 / Linux systemd 安装器。SDNick484 贡献了 Alpine LXC/OpenRC 与 Linux Docker macvlan 打包。**Windows 自动模式尚未通过真机验证**;Linux / 树莓派的重启与重连、Proxmox 真机运行已有社区反馈;Docker 只有合成测试。安装前请先阅读 Proxmox 网卡防火墙的作用范围。作者已确认最初的 Mac mini 自动模式原型可用,但这份跨平台实现仍需要各平台实机测试。**本项目既不是 4K 解锁,也不保证降低延迟。**

以下各节描述的是 **macOS 手动启动器**。Windows 手动模式请看 [WINDOWS.zh.md](WINDOWS.zh.md),Linux 或自动模式请看上面的指南。

这是一个实验性的 **macOS** 启动器,用于在你自己的 PlayStation Portal 上临时请求更高的 PS5 Remote Play 码率。包含 65、100 以及实验性的 200 Mbps 目标档位、一个有边界的中继、独立的出包验证和网络恢复。

**这不是越狱、不是 4K 解锁,也不保证降低延迟。** 目前仅在一台固件版本 **7.1.7** 的 Portal 上测试过。其它固件、网络布局和主机均未验证。本工具匹配的是「录制下来的包结构」,而不是经过验证的固件身份;包长度对得上,并不能保证明文字段偏移也一致。

[English](README.md) | [Türkçe](README.tr.md)

## 实测结果

| 档位 | PS5 报告的目标码率 | 作者实际观察 |
| --- | --- | --- |
| 65 Mbps | 约 63.106 Mbps | Portal 上约 58 Mbps;画面肉眼可见更干净 |
| 100 Mbps | 约 97.087 Mbps | Portal 上峰值约 84 Mbps |
| 200 Mbps(实验性) | 先 166.141 Mbps,随后约 158.3 Mbps | 主观反馈正面;实际持续吞吐未测定 |
| 另一项 4K 实验 | 约 97.087 Mbps | PS5 只提供 720p/540p/360p;画质明显倒退 |

可用的「仅码率」档位在 4K 实验之后把分辨率恢复回了 1080p。**失败的 4K 档位不包含在本项目中。** 以上只是单一环境的观察,不是受控基准测试。目标码率不等于实际视频吞吐。持续 100 或 200 Mbps、降低输入延迟、以及普遍兼容性,均未被证实。本项目不分发私有抓包数据和专有固件。

一位社区成员[报告称在较早的 Windows 手动预览版上成功跑通了 65 Mbps](https://www.reddit.com/r/PlaystationPortal/comments/1wtyglf/comment/pd0nzk0/)。这属于用户反馈,不构成对新的自动模式或 Windows 整体兼容性的独立验证。

一位 [Linux 测试者](https://www.reddit.com/r/PlaystationPortal/comments/1wtyglf/comment/pd2k5ls/) 报告在 EndeavourOS 和树莓派 OS / Pi 3B(有线以太网)上成功,包括 systemd 开机自启、Portal 全新重连,以及 PS5 从待机唤醒时使用 100 Mbps 档位。Docker 与 IP 转发的冲突以及仍未覆盖的测试空白,见[自动模式说明](AUTOMATION.zh.md)中的「社区 Linux 反馈」一节。这属于社区反馈,不是吞吐或延迟基准。

## 前提条件

- macOS,Python 3.10 或更高版本,具备 `sudo` 权限,以及系统自带的 `tcpdump`。
- PS5、Portal 和 Mac 必须在同一个直连的 IPv4 局域网内。彼此之间不能有访客网络/客户端隔离、VPN 路由或跨子网路由。
- PS5 建议接有线以太网。测试用的 Mac 走的是 Wi-Fi;而用 Wi-Fi 做中继本身就会增加丢包和延迟。
- 你需要拥有这台 Mac 的管理员权限,并且有操作这两台设备的授权。本工具会临时改动两台设备的 ARP 映射并关闭 ICMP 重定向;**不会修改固件**。
- Python 依赖不需要 sudo 安装。以管理员身份运行下载的启动器,等于执行它目录下的本地 Python 文件:请先审阅代码,并确保该目录只有可信用户可写。

## 安装

克隆或下载本仓库,然后在该目录下打开终端:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp config.example.json config.json
```

也可以直接双击 `Setup.command`。然后用**真实的** PS5 与 Portal 的 IPv4 地址和 Mac 网卡名去编辑 `config.json`。示例里的地址只是文档占位符,到不了你的设备。建议在路由器上做 DHCP 地址保留,避免地址变化。用 `networksetup -listallhardwareports` 查网卡名;Wi-Fi 通常是 `en0`,但不总是。

可选的预检(只解析配置里的两个对端,不会改动路由/ARP 映射):

```sh
sudo .venv/bin/python portal_capture.py --check
```

## 每次新的游戏会话

1. 断开 Portal 与 PS5 的连接;PS5 保持开机。
2. 双击 `Start.command`,选择 65、100 或 200,回车。只在本地 sudo 提示处输入 Mac 密码。
3. 等到出现 **READY**,再在 Portal 上发起一次全新连接。
4. 留意 **Startup packet modified** 这一行。在被接受且流建立之后,若连续三次上报足够高的目标码率,或到达 40 秒中继时限,本工具就会恢复直连路径。
5. 查看最终状态。结束后这台 Mac 就不再中继该会话了,不需要一直开着启动器。

也可以用终端:

```sh
sudo .venv/bin/python portal_active_probe.py --profile 65
# 或者选择要求更高的目标:
sudo .venv/bin/python portal_active_probe.py --profile 100
```

5 秒预热包含在 40 秒中继时间窗内,启动预检和清理还会在其前后额外花时间。独立的恢复看门狗从它自己启动起等待 55 秒。码率越高越可能加剧网络拥塞;请在同一个动态场景下对比不同档位。要回退,就正常断开再重连(不启动本工具)。每次新会话都会各自重新协商。

### 200 Mbps 实验

```sh
sudo .venv/bin/python portal_active_probe.py --profile 200
```

最初那次 200 Mbps 运行:实施了一次改写,收到了 BANG 接受与 STREAMINFO,并且无错误地恢复了网络。它的 PS5 目标码率最终稳定在 158 Mbps 附近,低于 160 Mbps 的提前退出阈值,因此返回了状态码 1(`UNCONFIRMED`)——**尽管会话其实是正常工作的**。本档位保留了该阈值:判定成功需要连续三次上报 ≥ 160 Mbps,而不是证明真的有 200 Mbps 视频。中继侧观测到的一秒 UDP 峰值是 75.760 Mbps;没有测量直连路径的持续吞吐,也没有测量延迟改善。分辨率字段未被改动。若播放出现劣化,请改用 100 或 65 重连。

## 工作原理

这台 Mac 只临时中继配置里指定的这一对 PS5–Portal。对于一个窄匹配的首个 Takion BIG 包(客户端版本 20、通道 0、GMAC 为零、2296 字节 base64 LaunchSpec),它在推断出的偏移 334 处对密文字节做 XOR。假设是 `25000` → `65000`;100 Mbps 则用等长的 JSON 数字 `1e+05`,200 Mbps 用 `2e+05`。本项目**不声称**做了明文解密或绕过认证。1080p 的分辨率字段不会被改动。

一次独立的有边界 `tcpdump` 抓包会验证「被改写的包确实出现在了 Mac 网卡上」。BANG 接受、STREAMINFO 以及连续的 CONNECTIONQUALITY 目标码率共同决定是否可以提前退出。这些控制消息只是被观测到,本工具并没有对它们做密码学校验。本地出包验证本身也不能证明对方真的收到了。包匹配成功并不代表与设备固件兼容。

## 故障排查与恢复

- **NOT APPLIED:** 没有抓到匹配的新握手。断开重试,并且务必在 READY 之后再连接。**不要**据此推断 PS5 拒绝了目标码率。
- **UNCONFIRMED:** 改写发生了,但没有观测到要求的高目标码率序列。正常重连,或改用 65。不要反复对未知固件结构强推。
- **卡顿或画面发糊:** 先对比 65 和 100,再考虑 200;目标码率不是越高越好。正常重连即可撤销本次会话的改动。
- **恢复失败:** 给看门狗留满它的 55 秒。报告里含有 `watchdog_state`,以及原始网络状态文件的本地路径。可用 `sudo .venv/bin/python portal_capture.py --restore /path/from/report/state.json` 重试恢复。**只使用本工具自己生成的**状态文件。如果进程是被强制杀掉的,把两台设备重新连一下以刷新邻居映射。
- **已存在锁文件:** 不要同时跑多个实验。若确认没有实验或看门狗在跑、且恢复已完成,可用 sudo 删除残留的 `/var/run/portal-lab-capture.lock`。**绝不能**在另一个运行中的实例还没结束时删它。

Ctrl-C 会进入清理流程。另有一个看门狗可在主进程崩溃时提供恢复,但 Mac 断电时它无能为力。请查看 `restoration_errors`,不要假定定时器就一定能成功。

## 隐私

`config.json`、抓包文件和生成的报告都只留在本地,且已被 git 忽略。原始抓包可能包含会话标识和网络元数据。**不要把它们贴到公开 issue 里。** 只分享人工脱敏后的摘要:固件版本、档位、是否发生改写、目标码率上报情况、恢复状态。本项目不发送任何遥测数据。

## 开发

```sh
.venv/bin/python -m unittest discover -s tests -v
```

测试使用合成数据包和模拟的网络操作,不需要真实设备也不需要 sudo。CI 只跑这些测试,不会真机验证。公开的打包与可配置网络层有离线验证;只有它们的原型在作者的设备上实测过。

独立的社区实验项目,与 Sony 或 PlayStation 无隶属关系。协议背景参考:[Chiaki-ng](https://github.com/streetpea/chiaki-ng)。本项目不内含任何 Chiaki 源码、Sony 固件、固件密钥或抓包会话。MIT 许可,详见 LICENSE。

## 支持本项目

☕ **支持本项目:** 本项目和 APK 将始终保持免费和开源。如果你愿意支持持续开发与测试,可以在这里请我喝杯咖啡:[https://buymeacoffee.com/atameric](https://buymeacoffee.com/atameric) ❤️
