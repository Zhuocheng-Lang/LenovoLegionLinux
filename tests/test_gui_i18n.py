"""Run with QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p test_gui_i18n.py."""

import logging
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python/legion_linux"))

from PyQt6.QtWidgets import QApplication
from legion_linux import i18n
from legion_linux.i18n import detect_system_language, install_translators, parse_language_arg


@contextmanager
def mock_system_locale(ui_languages, name):
    """Pretend QLocale.system() reports the given languages."""
    locale = Mock()
    locale.uiLanguages.return_value = ui_languages
    locale.name.return_value = name
    # wraps= keeps the real QLocale constructor (used for the zh_CN lookup
    # locale) while system() reports the fake locale.
    with patch.object(i18n, "QLocale", wraps=i18n.QLocale) as mock_qlocale:
        mock_qlocale.system.return_value = locale
        yield mock_qlocale


class I18nLoaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        logging.disable(logging.CRITICAL)

    def test_parse_language_arg(self):
        self.assertEqual(parse_language_arg(["legion_gui.py", "--language", "zh_CN"]), "zh_CN")
        self.assertEqual(parse_language_arg(["legion_gui.py", "--language=en"]), "en")
        self.assertIsNone(parse_language_arg(["legion_gui.py", "--use_legion_cli_to_write"]))
        self.assertIsNone(parse_language_arg(["legion_gui.py", "--language"]))

    def test_language_flag_forces_english(self):
        with mock_system_locale(["zh_CN"], "zh_CN"):
            self.assertEqual(install_translators(self.app, ["legion_gui.py", "--language", "en"]), "en")

    def test_unknown_language_falls_back_to_system(self):
        with mock_system_locale(["en_US"], "en_US"):
            self.assertEqual(install_translators(self.app, ["legion_gui.py", "--language", "xx"]), "en")

    def test_traditional_chinese_does_not_load_simplified(self):
        # Only legion_gui_zh_CN.qm exists; zh_TW/zh_HK must stay English.
        for tag in ("zh_TW", "zh_HK", "zh_Hant_TW"):
            with self.subTest(tag=tag), mock_system_locale([tag], tag):
                self.assertIsNone(detect_system_language())
                self.assertEqual(install_translators(self.app, ["legion_gui.py"]), "en")

    def test_simplified_chinese_detected_from_system(self):
        for ui_languages in (["zh_CN"], ["zh-Hans-CN", "zh-CN", "en-US"]):
            with self.subTest(ui_languages=ui_languages), mock_system_locale(ui_languages, "zh_CN"):
                self.assertEqual(detect_system_language(), "zh_CN")

    def test_missing_qm_falls_back_to_english_without_error(self):
        # No .qm is shipped in the test environment; requesting Chinese must
        # not raise and must report English as the effective language.
        with mock_system_locale(["zh_CN"], "zh_CN"), patch.object(
            i18n, "translations_dir", return_value="/nonexistent-translations-dir"
        ):
            self.assertEqual(install_translators(self.app, ["legion_gui.py", "--language", "zh_CN"]), "en")
            self.assertEqual(install_translators(self.app, ["legion_gui.py"]), "en")
