#!/bin/bash
set -ex
sudo dnf install -y kernel-headers kernel-devel dmidecode lm_sensors PyQt6 python3-yaml python3-pip python3-argcomplete python3-pillow python3-wheel polkit
# lrelease: compiles GUI translations/*.ts to *.qm during the Python package build
sudo dnf install -y qt6-linguist
sudo dnf groupinstall -y "Development Tools"
# sudo dnf group install -y "C Development Tools and Libraries"
sudo dnf install -y dkms openssl mokutil
