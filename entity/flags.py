# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject  # noqa: E402


class Flags(GObject.Object):
    __gtype_name__ = "Flags"

    acronym = GObject.Property(type=str, default="")
    country_name = GObject.Property(type=str, default="")
    flag = GObject.Property(type=str, default="")

    def __init__(
        self, acronym: str = None, country_name: str = None, flag: str = None
    ):
        super().__init__()
        self.acronym = acronym
        self.country_name = country_name
        self.flag = flag

    def to_dict(self) -> dict:
        return {
            "acronym": self.acronym,
            "country_name": self.country_name,
            "flag": self.flag,
        }

    def get_flags(self):
        return {
            "es": Flags("ES", _("Español"), "🇪🇸"),
            "pt": Flags("PT", _("Portugués"), "🇵🇹"),
            "gb": Flags("GB", _("Inglés GB"), "🇬🇧"),
            "us": Flags("US", _("Inglés US"), "🇺🇸"),
            "fr": Flags("FR", _("Francés"), "🇫🇷"),
            "de": Flags("DE", _("Alemán"), "🇩🇪"),
            "it": Flags("IT", _("Italiano"), "🇮🇹"),
            "mx": Flags("MX", _("Español"), "🇲🇽"),
            "br": Flags("BR", _("Portugués"), "🇧🇷"),
            "ar": Flags("AR", _("Español"), "🇦🇷"),
            "ca": Flags("CA", _("Inglés / Francés"), "🇨🇦"),
            "jp": Flags("JP", _("Japonés"), "🇯🇵"),
            "cn": Flags("CN", _("Chino"), "🇨🇳"),
            "kr": Flags("KR", _("Coreano"), "🇰🇷"),
            "in": Flags("IN", _("Hindi"), "🇮🇳"),
            "ru": Flags("RU", _("Ruso"), "🇷🇺"),
            "au": Flags("AU", _("Inglés"), "🇦🇺"),
            "se": Flags("SE", _("Sueco"), "🇸🇪"),
            "no": Flags("NO", _("Noruego"), "🇳🇴"),
            "fi": Flags("FI", _("Finlandés"), "🇫🇮"),
            "nl": Flags("NL", _("Neerlandés"), "🇳🇱"),
            "be": Flags("BE", _("Francés / Neerlandés"), "🇧🇪"),
            "ch": Flags("CH", _("Alemán / Francés / Italiano"), "🇨🇭"),
            "at": Flags("AT", _("Alemán"), "🇦🇹"),
            "dk": Flags("DK", _("Danés"), "🇩🇰"),
            "ie": Flags("IE", _("Inglés"), "🇮🇪"),
            "za": Flags("ZA", _("Inglés / Zulú / Xhosa"), "🇿🇦"),
            "eg": Flags("EG", _("Árabe"), "🇪🇬"),
            "ng": Flags("NG", _("Inglés / Hausa / Yoruba / Igbo"), "🇳🇬"),
            "ke": Flags("KE", _("Inglés / Swahili"), "🇰🇪"),
            "tr": Flags("TR", _("Turco"), "🇹🇷"),
            "gr": Flags("GR", _("Griego"), "🇬🇷"),
            "pl": Flags("PL", _("Polaco"), "🇵🇱"),
        }
