import os
import gettext
from enum import Enum


class TUILanguage(Enum):
    EN = ("en", "English")
    ZH = ("zh", "Chinese")
    Other = ("en", "English")  # default to show English

    @classmethod
    def from_str(cls, language: str) -> "TUILanguage":
        if language.lower().startswith("en"):
            return cls.EN
        elif language.lower().startswith("zh"):
            return cls.ZH
        else:
            return cls.Other

    @property
    def language_code(self) -> str:
        return self.value[0]

    @property
    def chat_language(self) -> str:
        return self.value[1]


def get_translation(tui_lang: TUILanguage) -> gettext.gettext:
    """
    Get the translation function for the given language.
    """
    localdir = os.path.join(os.path.dirname(__file__), "locales")
    lang_translations = gettext.translation(
        "base", localedir=localdir, languages=[tui_lang.language_code]
    )
    lang_translations.install()

    return lang_translations.gettext
