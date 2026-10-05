# Windows community preview - physical-device validation pending

For the new always-on preview, use [AUTOMATION.md](AUTOMATION.md). This guide covers bounded manual sessions only.

See [简体中文说明](WINDOWS.zh.md) | [Turkish test instructions](WINDOWS.tr.md). This preview shares the macOS packet transform but uses Npcap on native Windows 10/11. It has not been run on Windows hardware yet. Do not describe local offline tests as Windows runtime validation.

Install [Python 3.10+](https://www.python.org/downloads/windows/) with the `py` launcher (verify with `py -3 --version`) and [Npcap](https://npcap.com/#download), then extract the entire ZIP and run `Setup-Windows.cmd`. Following Scapy’s installation guidance, leave WinPcap compatibility mode unchecked; monitor/raw 802.11 support is not needed. Administrator-only Npcap access is compatible with the elevated launchers. Use only your own two devices on one directly connected LAN; the selected adapter must have IPv4 forwarding disabled. No firewall, registry or IP forwarding settings are changed.

Run these files as administrator in order:

1. `Configure-Windows.cmd`: select the LAN adapter and enter current PS5/Portal IPv4 addresses.
2. `Check-Windows.cmd`: read-only checks and two-peer ARP resolution.
3. `Baseline-Windows.cmd`: disconnect Portal, press Enter, reconnect only after READY. A bounded relay without payload mutation checks acceptance and cleanup. Visually confirm normal play.
4. `Start-Windows.cmd`: start with 65, then separately test 100/200 only after successful baseline and normal play. Each test needs a fresh Portal session after READY.

The relay window is 40 seconds including warm-up; setup and cleanup add time. A detached 50-second watchdog must signal readiness before ARP changes. A machine-wide named kernel object blocks overlapping experiments on that Windows machine. Do not run a Mac relay simultaneously. Ctrl+C triggers cleanup; power loss cannot be recovered by a watchdog on the same computer.

Independent local egress verification uses a separate Npcap handle and stores only hashes, not raw packets. It is not proof of remote delivery. A successful call sending restoration packets does not independently prove the peers updated their ARP caches. No resolution fields are changed. Input latency and sustained bitrate are not benchmarked.

On restoration error, keep the PC on for at least 60 seconds and inspect `experiments/<run>/recovery-state.recovery.json` and `watchdog.log`. Once no experiment/watchdog is running, an elevated terminal can retry `".venv\Scripts\python.exe" portal_windows.py --restore "experiments\<run>\recovery-state.json"`. Use only a state file created by this tool. Reconnect the peers' network interfaces if necessary. Disconnect/reconnect Portal normally to undo the bitrate request.

Do not publish configuration, recovery state or baseline receipts; they contain local network identifiers. Share redacted `report.json` plus Portal FPS/resolution/bitrate and subjective responsiveness. Raw secrets/firmware/session data are not bundled. No telemetry.

## Download and install, step by step

1. Open the repository's **Releases**, choose **Windows Community Preview**, and download the named Windows ZIP under **Assets**. It is marked **Pre-release** deliberately.
2. Right-click the ZIP → **Extract All**. Keep the extracted files together in a local folder. Do not run files from inside the ZIP or reuse a Mac `.venv`.
3. Install Python from the official link above with its launcher, open a fresh Command Prompt, and run `py -3 --version`. It must show Python 3.10 or newer. If `py` is missing, repair the Python launcher installation before continuing. WSL is not supported.
4. Install Npcap from its official site, using the options described above. Reopen terminals after installing the driver. Wireshark, Git and a USB cable are not required. The release ZIP does not bundle Python or Npcap.
5. Double-click **Setup-Windows.cmd**. It creates a local `.venv`, installs the pinned Scapy dependency and runs offline tests. Internet access is needed for the dependency download. Continue only if tests end in `OK`.
6. Right-click **Configure-Windows.cmd** → **Run as administrator**. Accept the Windows UAC prompt. Choose the physical LAN adapter, not VPN/loopback. Enter the current device addresses from the PS5/Portal network screens or router app. This writes only local configuration; do not upload it.
7. Right-click **Check-Windows.cmd** → **Run as administrator**. Continue only on `CHECK PASSED`. If it reports Npcap, route, forwarding or peer-resolution errors, stop and report the redacted error. Do not disable your firewall to try to force it through.
8. Disconnect the Portal session, leave PS5 on, then right-click **Baseline-Windows.cmd** → **Run as administrator**. Press Enter. Start a new Portal session **only after READY**. Wait for `Baseline passed` and confirm normal picture/control after restoration. If it fails, do not advance to bitrate modification.
9. Disconnect again and run **Start-Windows.cmd** as administrator. Select **65**, press Enter, wait for READY, then connect. After a successful result, observe a moving scene for 30-60 seconds. Test **100** and **200** in separate fresh sessions only if earlier profiles work well.
10. Open an issue using **Windows preview test result**. Report successes as well as failures. This is how we establish whether the Windows implementation actually works across adapters.

## What has and has not been validated

The synthetic tests and extracted ZIP were tested on macOS. They cover exact ciphertext deltas, packet length/checksum, confirmation gating, configuration validation and mocked recovery paths. Native Windows execution, Npcap injection on physical adapters, actual PS5 acceptance and Portal playback on Windows remain unverified. GitHub-hosted tests may also be blocked by the maintainer's account runner availability; check the actual run rather than assuming a green CI result.

Test on your own devices. Driver incompatibility or interrupted cleanup can temporarily disrupt their connection. The bounded relay and watchdog reduce that risk but are not a guarantee. Report any recovery issue before repeating a run. The named 200 Mbps profile is an experimental request; on the Mac prototype it produced roughly 158-166 Mbps console targets, not verified sustained 200 Mbps traffic.

- `0`: the selected stage met its software criteria; still check actual picture/control.
- `1`: stage not confirmed; for 200, the target may settle below the 160 Mbps confirmation threshold despite a working session.
- `2`: an error occurred; read the message and restoration fields. Do not repeatedly retry blindly.

Reference: [Scapy Windows installation](https://scapy.readthedocs.io/en/stable/installation.html#windows).
