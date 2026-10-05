# 社区讨论知识库(Reddit 原帖 1wtyglf)

> 本文把项目首发帖下的全部讨论整理成可检索的知识条目,供排障、需求排序和二次开发参考。
> 所有结论都标注了来源评论 ID,可回溯原文核对。

## 数据来源与口径

| 项 | 值 |
| --- | --- |
| 原帖 | [I got higher bitrate PS Remote Play working on PS Portal — 65/100/200 Mbps experiment, no jailbreak](https://www.reddit.com/r/PlaystationPortal/comments/1wtyglf/) |
| 发帖人 | `lllnicotinelll` —— 即本仓库作者 atameric |
| 时间跨度 | 2026-09-30 07:20 ~ 2026-10-03 14:33(UTC) |
| 规模 | 184 条评论 / 56 条根评论 / 31 位参与者,其中作者本人回复 69 条 |
| 抓取方式 | 通过 pullpush.io 公开归档 API 全量拉取(单次上限 100,按 `before` 游标翻页);复现脚本见 [`scripts/fetch_reddit_thread.py`](scripts/fetch_reddit_thread.py) |
| 证据等级 | **全部为用户自报,非受控基准测试。** 单条报告不构成兼容性证明;重复出现的同构报告才视为信号 |

引用约定:文末 `[pd2k5ls]` 这类标记是 Reddit 评论 ID,可拼成 `reddit.com/r/PlaystationPortal/comments/1wtyglf/comment/<id>/` 直达原文。西班牙语、德语评论均已译为中文并注明。

---

## 一、协议与原理层面的外部洞察(价值最高)

这部分来自**本项目之外**的独立信源,尤其是 PXPlay(原 PSPlay)作者 `grill2010` 的发言,直接印证/修正了本项目的技术假设。

1. **码率只是一个启动参数,没有秘密。** PXPlay 作者:让 PS 以更高码率串流所需做的全部事情,就是在 Remote Play 连接的启动参数里配置最大码率,"仅此而已,没有任何高深逻辑。换句话说,索尼只是不想解锁它,就这一个参数的改动,一行修复。" `[pcyq25t]`
2. **超过 100 Mbps 大概率无效。** 同一位作者据其调研称:高于 100 Mbps 的码率不会产生效果,因为主机本身不会以更高质量串流。 `[pcyqbf9]`
   → 这是把 200 档定位为「实验性」的外部依据;也解释了为什么 200 档实测稳定在 158–166 Mbps 却未见画质再提升。
3. **PS5 的 2K/4K 是硬编码屏蔽,不是硬件不行。** "PS5 其实具备 2K 和 4K 解码能力,只是被 PS5 上的截屏程序硬编码屏蔽了……换句话说,对已越狱的机器这可能是可修补的。"该作者与部分 Chiaki-ng 开发者表示会去验证。 `[pczyy98]`
   → 项目 README 里那次「4K 实验导致 PS5 只提供 720p/540p/360p」的失败,线索指向截屏/编码侧限制,而非本工具的改写逻辑有误。
4. **瓶颈在网络,不在 SoC。** `tissee`:PS5 的 SoC 应当有专用编解码模块,这里的限制是中间的网络。 `[pcyu5tq]` 另有人追问 PS5 Pro 是否突破限制,答案是「没有,Pro 是同一套引擎」。 `[pczvsmd]` `[pczyy98]`
5. **码率↑ ≠ 延迟↓。** `grill2010`:更高码率意味着编码器压缩更少、画质更高,但网络包更大,在网络不稳定时可能**增加**视频延迟,主观上像输入延迟,其实只是视频。 `[pcysiam]`
   `tissee`:理论上压缩率更低但延迟会升高;现实中延迟强依赖连接稳定性,丢包越多重传越多。 `[pcysquf]`
6. **技术定性:本地中间人。** 作者本人确认:"技术上它是一种本地中间人手法,用临时 ARP 重定向来改写你自己设备上一个匹配的启动码率请求。它不绕过 PSN 认证、不解密整个会话、也不修改 Portal 固件。" `[pde80a0]`

---

## 二、成功案例台账

| 平台 | 环境 | 档位 | 观测结果 | 来源 |
| --- | --- | --- | --- | --- |
| macOS | 作者本人,Portal 固件 7.1.7 | 65 / 100 / 200 | 见 README 实测表 | 原帖 |
| macOS | `BrokennDark`,网络一般 | 65 | 画面明显更锐利 | `[pcyn4pm]` |
| macOS | `barwen1899`,MacBook M5 Max | 100 | "画质差异巨大" | `[pd325me]` |
| macOS | `Pelcom2`,MacBook Air M2(2023)/ macOS 27,两端最新固件 | 65 | 实测 **56 Mbps**(自述为普通用户,靠 ChatGPT 引导完成) | `[pd5j1wm]` |
| Windows | `Stunning-Vegetable-5`,Win11 + 最新 Npcap,PC 走 Wi-Fi 2.4 GHz/20 MHz | 65 | 一次成功,"清晰如水晶" | `[pd0nzk0]` `[pd0ug3t]` |
| Windows | 同上,改走 5 GHz | 200 | 峰值 **90 Mbps** | `[pd11b3w]` |
| Windows | 同上,5 GHz / 20–40 MHz | 100 | 峰值 80、均值约 60(CoD 类高速场景常在 80) | `[pdgi5y8]` |
| Windows | `alitlp53`,Win11 + Realtek 有线网卡 | 65 / 100 | 画质很好 | `[pdbifng]` |
| Windows | `talgold`,Win11 | 未注明 | 需自行 tweak 才能跑通;**且笔记本必须接网线**(原本走 Wi-Fi) | `[pd33d3v]` |
| Windows | `Radxical` | 100 | Portal 显示峰值约 50 Mbps;但对照:关闭程序约 25 Mbps、开启后超过 50 Mbps → 确认生效 | `[pd80f80]` `[pdit18v]` |
| Linux | `tissee`,EndeavourOS(Arch)笔记本 | — | 无问题 | `[pd2ddwu]` |
| Linux | `tissee`,**树莓派 3B** / 树莓派 OS / **以太网** | 100 | systemd 开机自启成功、Portal 全新重连成功、**PS5 从待机唤醒时同样生效**;需先关掉被 Docker 开启的 IPv4 转发 | `[pd2k5ls]` |
| Proxmox | `SDNick484`,PVE 上 Alpine LXC(miniPC) | — | 当晚测试成功 → 提交 PR #1(已合入 v0.3.0-preview.3) | `[pd4tazo]` `[pd5pukp]` `[pd9fbl0]` |
| Docker | `Genjizero`,按容器指南 | — | 成功 | `[pdfp8un]` |
| Android(root) | `eahmedatef`,已 root 的旧安卓机 | — | 移植后"运行得很顺";据其称**必须 root** | `[pddpnlu]` `[pddq6l7]` |
| Home Assistant OS | `Acceptable-Top3961`(用 Gemini 生成) | — | 实现了开关与按需切换档位 | `[pd2j1ww]` |

**由此可得的可靠结论**:以太网 > 5 GHz Wi-Fi > 2.4 GHz Wi-Fi;Pi 3B 这类低算力设备在中继场景下是可行的( tissee 一人同时验证了 EndeavourOS 与 Pi,且覆盖开机自启与待机唤醒);Windows 与 Realtek/Npcap 组合已有多例成功,但失败案例同样集中在 Windows(见下节)。

---

## 三、已知失败模式与排查线索

| 现象 | 环境细节 | 作者判断 / 处置 | 来源 |
| --- | --- | --- | --- |
| **NOT APPLIED**(无匹配的新握手) | `blagd`,macOS Tahoe 26.6.2 / 固件 7.1.7;报告显示 `mode=candidate_byte_probe`、`unique_mutated_sequences:0`、`counts` 仅 forwarded 18/10 | 这其实是**手动模式**日志(用户误以为是自动模式)。必须在 READY 之后才发起新连接;核对 `config.json` 里的 PS5/Portal IP 与 Mac 网卡名。**未发生改写 ≠ PS5 拒绝** | `[pd7v2g4]` `[pddnksm]` `[pde7s6d]` |
| **Run 阶段 Portal 连不上 PS5**(Baseline 正常) | `confusedinboston`,Win11 / 7.1.7 / 65;Npcap 1.89、Realtek Gaming 2.5be、TP-Link Deco mesh;终端报 `Network interface was not found` + exit code 1 | 属**网卡/Npcap 错误,不是 PS5 拒绝码率**。换一台 miniPC 直连后仍复现 → 怀疑指向 Deco mesh 网络。曾为 Moonlight 改过网卡配置,但作者明确表示"还不能确立因果,不要盲目重置" | `[pd2b7ly]` `[pd9mez9]` `[pde7txo]` `[pdh8aex]` |
| **Configure 填了 PC 的 IP** | 同上用户,在「LAN interface name/guid」处填了本机 IP | 该字段要的是网卡名或完整 Npcap ID,不是 IP。preview.2 已改为**菜单编号选网卡**;另注意失败的 Configure 会留下旧配置 | `[pd2kpf9]` `[pd2qm2x]` |
| **Baseline 阶段就不稳** | `Unhappy-Bluejay-6518`,PS5 与 PC 均为有线;码率掉到约 1 Mbps,操控时好时坏,约一分钟后断线;不开程序时串流完美 | 连 Baseline 都不稳 → 指向**中继/网络路径**,而非高码率请求本身。不要在此期间安装自动模式;确认只有一个中继在跑。**共用 Pi-hole 的主机未经验证** | `[pd6h6wa]` `[pd9f6o4]` |
| **Win10 自动模式会话丢失** | `cristiANgn1`,Win10:出现 "Startup packet modified" → "High Target observed" → 恢复直连后 Portal 报 "You lost the connection to your PS5";Baseline 与 65/100/200 均复现,但确实看到码率上升 | 无人跟进回复(发帖时点靠后)。模式特征指向**恢复直连阶段**的稳定性问题,而非改写失败 | `[pdgg4i4]` |
| **卸载后无法重新安装** | `Radxical`,提示已存在 profile,但 start/stop/status 都报没有已保存内容 | **已知行为**:Uninstall 移除任务但保留 `ProgramData` 下的配置与日志 → 需在 relay 与 guardian 都停止后再清理该目录 | `[pd4otjj]` `[pd5m5px]` |
| 全 Wi-Fi 下偶发断线 | `_Surgeee`,100 Mbps,Portal 峰值 96.1 Mbps(《巫师 重制版》) | 建议同场景对比 65,并检查原生未修改的 Remote Play 是否同样断线,以便区分是工具还是网络 | `[pcyv33m]` `[pczesmh]` |

---

## 四、副作用与性能观察(对二次开发最关键)

### ⭐ 前台 Relay 在环会显著抬高延迟,退出后码率仍保持

`Key-Visual4476`(Windows,手动模式)的观察,65 与 100 档均复现:

> 我 Run 起来玩的时候,延迟会跳到 **13–30 ms**;但一旦按 Ctrl+C 关掉窗口,**码率保持在高位,延迟却降到 1–2 ms**。65 和 100 档都这样……我必须按 Ctrl+C 才能让延迟消失。 `[pdjb57n]` `[pdjcwsq]`

这条的价值在于:

- 它是**架构分析里"常驻模式在控制路径上多一跳、延迟未测量"的第一个实测旁证**。中继在环时有可感知代价,退出后码率效果保留——正好对应手动模式「改完就恢复直连」与自动模式「常驻中继」的设计差异。
- 给自动模式提出了明确的待办:**把延迟/丢包做成对照测量项**,而不是只看 `unique_modified_startups`。
- 注意作者已提醒:他处看到的 1–2 ms 读数**不应当作端到端输入延迟** `[pd5mo7l]`。

### 其它观察

- **5 GHz 明显优于 2.4 GHz。** 同一位西班牙测试者:Portal 上限 25 Mbps 的年代 2.4 GHz 够用,但上了高码率后 5 GHz 稳定得多;并在路由器上给 PS5 与 Portal 设了固定 IP 与网络优先级。 `[pd11b3w]` `[pdgi5y8]`
- **高码率不是延迟药。** 作者多次重申:没测过输入延迟改善,不建议把提高码率当作降延迟手段;"0 latency" 是早期口误,已自行更正。 `[pczehq5]` `[pczep1x]` `[pczepw0]`

---

## 五、社区需求清单(按提及密度排序)

1. **安卓版** —— 提及最多、付费意愿最强(`Stunning-Vegetable-5`、`LaxExterior`、`Dreaditty`、`Key-Visual4476` 均表示"出就买")。作者回应:跑 Python 只是一部分,中继还需要抓包/注入、ARP 处理与可靠的后台网络访问,这些平台相关部分**尚未移植或测试**;但**不排除可能性**(已把早先"不可能"的绝对表述收回)。rooted Android 已有 1 例社区成功。 `[pd9f3pj]` `[pde7leb]`
2. **档位热切换 / 开关** —— `tissee` 明确提出"能不能简单地切换档位";`Acceptable-Top3961` 已在 HAOS 上做出开关与按需切档。作者确认:手动模式启动时可选;**已安装的自动模式换档必须 stop → 重新 configure → 重跑 Baseline/Run → 重装,没有 live switch,已连接流的切换也未实现,无 ETA**。 `[pdds9zl]` `[pde7nkl]` `[pd2j1ww]`
3. **视频教程** —— 多人要求。`Key-Visual4476` 后来改口:说明其实够清楚,唯一卡点是**给 PS5 和 Portal 设静态 IP**。 `[pd4lzia]` `[pdjb57n]`
4. **iPad Remote Play / Asobi 客户端** —— 本工具只匹配 Portal 启动包,这两者**未验证**。 `[pd5mdz8]`
5. **家外(互联网)远程串流** —— 当前实现依赖 PS5/Portal/主机在同一直连 LAN,远程需要另一套网络设计,**当前实现的档位不是经过测试的出门方案**。 `[pd7anos]` `[pd9ezct]`
6. **把 Steam 串流注入 Portal** —— 需要兼容的会话/服务端实现与输入处理,不只是换视频包,**未实现**。 `[pdbifng]` `[pde7pcv]`
7. **远程关闭 HDR/VRR/120 Hz** —— 本工具只改码率请求,**未实现**。 `[pd17dm6]` `[pd5mfhn]`
8. **降低输入延迟** —— 明确**不是本工具目标**;作者建议不要指望它解决 60–70 ms 的串流延迟问题。

---

## 六、作者反复澄清的认知红线

在写文档、做二开、对外描述时,以下边界不能越过:

- **不越狱、不改固件、不解密完整会话、不绕过 PSN 认证**;LAN-only 场景下 PSN 握手照常走官方通道(作者未验证离线 PSN 与旧固件)。 `[pczenbs]` `[pczels8]` `[pde80a0]`
- **目标码率 ≠ 实际视频吞吐**。作者主动把 158–166 Mbps 的读数更正为"主机上报的目标值,不是实际吞吐或画质更好的证据"。 `[pczemlw]`
- **未测量输入延迟**。 `[pczehq5]`
- **手动模式结束后恢复直连并退出;自动模式保留主机承载控制/出站流量,视频仍直连。** `[pd0u0a1]` `[pd9fmvs]`
- **不修复弱 Wi-Fi**。 `[pd0u0a1]`
- 本项目**不分发**抓包与固件;受控测试才有效。

---

## 七、对二次开发的直接启示

结合本仓库的架构分析,这份讨论里能直接转成行动项的有:

1. **档位热切换是需求榜首,而仓库现状恰好是它的障碍。** 同一份「档位 → XOR 掩码 + 阈值」表在 `portal_active_probe.py:208`、`portal_auto.py:23`、`portal_windows.py:15` 各存一份,三处必须同改。要做 live switch,第一步应是抽成 `profiles.py` 单一数据源。
2. **延迟测量是空白且已有风险信号。** `Key-Visual4476` 的 13–30 ms → 1–2 ms 观察说明中继在环代价可观;自动模式应加延迟/丢包对照,而不是只数 `unique_modified_startups`。
3. **Windows 的失败集中在「网卡选择」这一交互点。** `Network interface was not found` 与 mesh / 多网段环境相关,Configure 的适配器选择是全链路最高风险的一步(上游已用菜单编号选择缓解,但仍需更强的错误提示)。
4. **卸载/重装残留是真实痛点。** Uninstall 保留 ProgramData 配置导致无法重装,自动模式的生命周期管理值得补一个"彻底清理"路径。
5. **共用主机的场景未验证。** 树莓派与 Pi-hole 共用、Docker 主机(转发冲突)都只有单点报告或明确警告。
6. **超过 100 Mbps 的收益存疑。** PXPlay 作者的独立判断支持把 200 档继续标记为实验性,不宜在文档或 UI 中暗示"越高越好"。

---

## 附:如何复现这份抓取

```sh
python scripts/fetch_reddit_thread.py 1wtyglf --out _fetch/reddit_full.txt
```

脚本走 pullpush.io 公开归档 API,只读、不需 Reddit 账号。输出为缩进评论树(含 ID/作者/时间/score),便于在帖子更新后重新生成并 diff。
