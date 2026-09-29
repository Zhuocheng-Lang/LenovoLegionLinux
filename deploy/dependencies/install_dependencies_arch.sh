#!/bin/bash
set -ex
sudo pacman -S --disable-download-timeout --noconfirm linux-headers base-devel lm_sensors git dmidecode python-pyqt6 python-yaml python-argcomplete python-pillow polkit python-build python-installer python-wheel python-setuptools
# lrelease: compiles GUI translations/*.ts to *.qm during the Python package build
sudo pacman -S --disable-download-timeout --noconfirm qt6-tools
sudo pacman -S --disable-download-timeout --noconfirm dkms openssl mokutil
