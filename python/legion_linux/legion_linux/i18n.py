"""Qt translation loading for the Legion GUI.

Language selection order (see the GUI localization spec):
1. ``--language <tag>`` command line argument (``en`` forces English,
   ``zh_CN`` forces Simplified Chinese). This exists for launchers such as
   ``pkexec`` that clear locale environment variables.
2. The system locale via ``QLocale.system()``.
3. English when nothing matches.

Only ``zh_CN`` has a translation file (``translations/legion_gui_zh_CN.qm``),
so other Chinese locales such as ``zh_TW`` fall back to English instead of
loading Simplified Chinese text. Any failure (missing ``.qm`` file, missing
Qt base translation) is logged and the GUI keeps running in English.
"""

import logging
import os
from typing import List, Optional

from PyQt6.QtCore import QLibraryInfo, QLocale, QTranslator

log = logging.getLogger(__name__)

LANGUAGE_ENGLISH = "en"
LANGUAGE_CHINESE_SIMPLIFIED = "zh_CN"
_TRANSLATION_BASENAME = "legion_gui"

# Qt does not take ownership of installed translators, so they must stay
# referenced for the lifetime of the application. A garbage-collected
# QTranslator silently disables translation.
_loaded_translators: List[QTranslator] = []


def translations_dir() -> str:
    """Directory holding the compiled ``legion_gui_*.qm`` files."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "translations")


def parse_language_arg(argv: List[str]) -> Optional[str]:
    """Return the ``--language <tag>`` value from argv, or None if absent."""
    for index, arg in enumerate(argv):
        if arg == "--language" and index + 1 < len(argv):
            return argv[index + 1]
        if arg.startswith("--language="):
            return arg.split("=", 1)[1]
    return None


def _normalize_tag(tag: str) -> str:
    return tag.strip().replace("-", "_")


def _match_supported(names: List[str]) -> Optional[str]:
    """Map an ordered locale name list onto a supported language tag."""
    for name in names:
        normalized = _normalize_tag(name)
        if normalized == LANGUAGE_CHINESE_SIMPLIFIED or normalized.startswith("zh_Hans"):
            return LANGUAGE_CHINESE_SIMPLIFIED
        if normalized == LANGUAGE_ENGLISH or normalized.startswith("en_"):
            return LANGUAGE_ENGLISH
    return None


def detect_system_language() -> Optional[str]:
    """Return the supported language matching the system locale, if any."""
    system = QLocale.system()
    language = _match_supported(system.uiLanguages())
    if language is None and system.name():
        language = _match_supported([system.name()])
    if language is None:
        log.info("System locale %s is not supported, using English", system.name())
    return language


def _load_translator(locale: QLocale, basename: str, filename_suffix: str, directory: str) -> Optional[QTranslator]:
    translator = QTranslator()
    if translator.load(locale, basename, filename_suffix, directory):
        return translator
    log.info("Translation file %s_%s.qm not found in %s", basename, locale.name(), directory)
    return None


def install_translators(app, argv: List[str]) -> str:
    """Install Qt translators on app; return the effective language tag.

    Must be called after the QApplication is created but before any widget
    is constructed. Never raises for translation problems: failures fall
    back to English.
    """
    requested = parse_language_arg(argv)
    language: Optional[str] = None
    if requested is not None:
        normalized = _normalize_tag(requested)
        if normalized in (LANGUAGE_ENGLISH, LANGUAGE_CHINESE_SIMPLIFIED):
            language = normalized
        else:
            log.warning("Unknown --language %r, falling back to system locale", requested)
    if language is None:
        language = detect_system_language()
    if language is None or language == LANGUAGE_ENGLISH:
        return LANGUAGE_ENGLISH

    # Only Simplified Chinese ships a translation; the file is looked up for
    # exactly zh_CN so zh_TW/zh_HK never pick up Simplified Chinese text.
    locale = QLocale(LANGUAGE_CHINESE_SIMPLIFIED)
    translator = _load_translator(locale, _TRANSLATION_BASENAME, "_", translations_dir())
    if translator is None:
        return LANGUAGE_ENGLISH
    app.installTranslator(translator)
    _loaded_translators.append(translator)

    qt_translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qtbase = _load_translator(locale, "qtbase", "_", qt_translations_path)
    if qtbase is not None:
        app.installTranslator(qtbase)
        _loaded_translators.append(qtbase)
    return LANGUAGE_CHINESE_SIMPLIFIED
