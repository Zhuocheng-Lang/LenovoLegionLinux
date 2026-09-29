#!/usr/bin/env python

"""Build the legion_linux package, compiling Qt GUI translations first.

Every translations/*.ts catalog is compiled to a *.qm file with lrelease
(Qt Linguist tools) so the wheel ships ready-to-load translations. When no
lrelease is found, the build continues with a warning and the GUI falls
back to English at runtime; lrelease is therefore not a pip dependency
(use the distro package instead: qt6-l10n-tools, qt6-linguist,
qt6-tools-linguist or qt6-tools).
"""

import glob
import os
import shutil
import subprocess

import setuptools
from setuptools.command.build_py import build_py as _build_py


def find_lrelease():
    """Return an lrelease executable path, or None if none is available."""
    for candidate in (
        shutil.which("lrelease"),
        shutil.which("lrelease-qt6"),
        "/usr/lib/qt6/bin/lrelease",
        "/usr/lib64/qt6/bin/lrelease",
    ):
        if candidate and os.path.exists(candidate):
            return candidate
    return None


def compile_translations():
    """Compile translations/*.ts to *.qm next to the sources (git-ignored)."""
    translations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "legion_linux", "translations")
    sources = sorted(glob.glob(os.path.join(translations_dir, "*.ts")))
    if not sources:
        return
    lrelease = find_lrelease()
    if lrelease is None:
        print(
            "WARNING: lrelease not found, skipping Qt translation compilation; "
            "the GUI will fall back to English. "
            "Install qt6-l10n-tools (Ubuntu), qt6-linguist (Fedora), "
            "qt6-tools-linguist (openSUSE) or qt6-tools (Arch) to ship translations."
        )
        return
    for source in sources:
        target = os.path.splitext(source)[0] + ".qm"
        print(f"Compiling {source} to {target} with {lrelease}")
        subprocess.run([lrelease, source, "-qm", target], check=True)


class BuildPyWithTranslations(_build_py):
    """build_py that compiles Qt translations before packaging."""

    def run(self):
        compile_translations()
        super().run()


if __name__ == "__main__":
    setuptools.setup(cmdclass={"build_py": BuildPyWithTranslations})
