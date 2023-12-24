import os
import gettext
from enum import Enum


class TUILanguage(Enum):
    EN = "en"
    ZH = "zh"
    Other = "en"  # default to show English

    @classmethod
    def from_str(cls, language: str) -> "TUILanguage":
        if language.startswith("en"):
            return cls.EN
        elif language.startswith("zh"):
            return cls.ZH
        else:
            return cls.Other


def get_translation(tui_lang: TUILanguage) -> gettext.gettext:
    """
    Get the translation function for the given language.
    """
    localdir = os.path.join(os.path.dirname(__file__), "locales")
    lang_translations = gettext.translation(
        "base", localedir=localdir, languages=[tui_lang.value]
    )
    lang_translations.install()

    return lang_translations.gettext
