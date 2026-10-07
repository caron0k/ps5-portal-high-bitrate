#!/bin/sh
set -eu
cd "$(dirname "$0")"
[ "$(uname -s)" = Linux ] || { echo 'Native Linux only'; exit 1; }
case "${1:-help}" in
 setup)
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python -m unittest discover -s tests -v
  ;;
 configure) sudo .venv/bin/python portal_auto.py configure --profile "${2:-65}" ;;
 baseline) sudo .venv/bin/python portal_auto.py baseline ;;
 confirm-baseline) sudo .venv/bin/python portal_auto.py confirm-baseline ;;
 run) sudo .venv/bin/python portal_auto.py run ;;
 install) sudo .venv/bin/python service/install_linux.py ;;
 start)
  sudo rm -f /var/lib/portal-bitrate-auto/disabled
  sudo systemctl start portal-bitrate-auto
  ;;
 stop)
  sudo /opt/portal-bitrate-auto/.venv/bin/python /opt/portal-bitrate-auto/portal_auto.py stop --runtime /var/lib/portal-bitrate-auto
  sudo systemctl stop portal-bitrate-auto
  ;;
 status)
  sudo /opt/portal-bitrate-auto/.venv/bin/python /opt/portal-bitrate-auto/portal_auto.py status --runtime /var/lib/portal-bitrate-auto
  systemctl status portal-bitrate-auto --no-pager
  ;;
 uninstall)
  sudo systemctl disable --now portal-bitrate-auto
  sudo rm -f /etc/systemd/system/portal-bitrate-auto.service
  sudo systemctl daemon-reload
  echo 'Service removed. Private files retained in /opt/portal-bitrate-auto and /var/lib/portal-bitrate-auto.'
  ;;
 *) echo 'Commands: setup, configure [65|100|200], baseline, confirm-baseline, run, install, start, stop, status, uninstall' ;;
esac
