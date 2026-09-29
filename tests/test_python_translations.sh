#!/bin/bash
# GUI translation gate (spec R5.5):
# 1. re-extract translatable strings with pylupdate6 and require the message
#    set (context, source) to match the committed .ts (ignoring <location>);
# 2. compile the .ts with lrelease without errors;
# 3. fail when any message is still unfinished.
set -e
DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)

PKG="${DIR}/../python/legion_linux/legion_linux"
TS="${PKG}/translations/legion_gui_zh_CN.ts"

if ! command -v pylupdate6 >/dev/null 2>&1; then
    echo "pylupdate6 not found (install pyqt6-dev-tools); cannot verify translation extraction" >&2
    exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

pylupdate6 "${PKG}/legion_gui.py" "${PKG}/fan_curve_plot.py" "${PKG}/i18n.py" -ts "${TMP}/fresh.ts" >/dev/null

python3 - "${TS}" "${TMP}/fresh.ts" <<'EOF'
import sys
import xml.etree.ElementTree as ET


def message_set(path):
    messages = set()
    for context in ET.parse(path).getroot().iter("context"):
        name = context.find("name").text
        for message in context.iter("message"):
            messages.add((name, message.find("source").text or ""))
    return messages


committed, fresh = message_set(sys.argv[1]), message_set(sys.argv[2])
if committed != fresh:
    for name, source in sorted(fresh - committed):
        print(f"missing in committed .ts: [{name}] {source}")
    for name, source in sorted(committed - fresh):
        print(f"obsolete in committed .ts: [{name}] {source}")
    sys.exit(1)
print(f"message sets match ({len(committed)} messages)")
EOF

LRELEASE=""
for candidate in "$(command -v lrelease)" "$(command -v lrelease-qt6)" \
    /usr/lib/qt6/bin/lrelease /usr/lib64/qt6/bin/lrelease; do
    if [ -n "${candidate}" ] && [ -x "${candidate}" ]; then
        LRELEASE="${candidate}"
        break
    fi
done
if [ -z "${LRELEASE}" ]; then
    echo "lrelease not found; install qt6-l10n-tools (Ubuntu), qt6-linguist (Fedora)," >&2
    echo "qt6-tools-linguist (openSUSE) or qt6-tools (Arch)" >&2
    exit 1
fi

"${LRELEASE}" "${TS}" -qm "${TMP}/legion_gui_zh_CN.qm"

UNFINISHED=$(grep -c 'type="unfinished"' "${TS}" || true)
if [ "${UNFINISHED}" != "0" ]; then
    echo "${UNFINISHED} unfinished translations in ${TS}" >&2
    exit 1
fi
echo "translations complete: 0 unfinished"
