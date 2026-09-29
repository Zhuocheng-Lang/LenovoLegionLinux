#!/bin/bash
# Developer helper (spec R5.6): merge newly marked GUI strings into the
# Simplified Chinese catalog. Run after wrapping new user-visible strings,
# then translate the new entries with Qt Linguist (or `linguist`).
set -e
DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

PKG="${DIR}/../python/legion_linux/legion_linux"

pylupdate6 "${PKG}/legion_gui.py" "${PKG}/fan_curve_plot.py" "${PKG}/i18n.py" \
    -ts "${PKG}/translations/legion_gui_zh_CN.ts"
