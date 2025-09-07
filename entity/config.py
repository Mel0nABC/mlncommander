# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from css.explorer_css import Css_explorer_manager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject  # noqa: E402


class ConfigEntity(GObject.Object):

    __gtype_name__ = "ConfigEntity"

    def __init__(
        self,
        SWITCH_COPY_STATUS: bool = None,
        SWITCH_MOVE_STATUS: bool = None,
        SWITCH_DUPLICATE_STATUS: bool = None,
        SWITCH_COMPRESS_STATUS: bool = None,
        SWITCH_UNCOMPRESS_STATUS: bool = None,
        EXP_1_PATH: str = None,
        EXP_2_PATH: str = None,
        FAV_PATH_LIST_1: list[str] = None,
        FAV_PATH_LIST_2: list[str] = None,
        SHOW_DIR_LAST: bool = None,
        SWITCH_IMG_STATUS: bool = None,
        SWITCH_WATCHDOG_STATUS: bool = None,
        COLOR_BACKGROUND_APP: str = None,
        COLOR_ENTRY: str = None,
        COLOR_EXPLORER_LEFT: str = None,
        COLOR_EXPLORER_RIGHT: str = None,
        COLOR_BUTTON: str = None,
        COLOR_FAV_BUTTON: str = None,
        COLOR_BACKGROUND_SEARCH: str = None,
        COLOR_SEARCH_TEXT: str = None,
        FONT_STYLE: str = None,
        FONT_STYLE_COLOR: str = None,
        LANGUAGE: str = None,
    ):
        super().__init__()

        # GENERAL

        self.SWITCH_COPY_STATUS = SWITCH_COPY_STATUS
        self.SWITCH_MOVE_STATUS = SWITCH_MOVE_STATUS
        self.SWITCH_DUPLICATE_STATUS = SWITCH_DUPLICATE_STATUS
        self.SWITCH_COMPRESS_STATUS = SWITCH_COMPRESS_STATUS
        self.SWITCH_UNCOMPRESS_STATUS = SWITCH_UNCOMPRESS_STATUS
        self.LANGUAGE = LANGUAGE

        # DIRECTORYS

        self.FAV_PATH_LIST_1 = FAV_PATH_LIST_1
        self.FAV_PATH_LIST_2 = FAV_PATH_LIST_2
        self.EXP_1_PATH = EXP_1_PATH
        self.EXP_2_PATH = EXP_2_PATH
        self.SHOW_DIR_LAST = SHOW_DIR_LAST
        self.SWITCH_IMG_STATUS = SWITCH_IMG_STATUS
        self.SWITCH_WATCHDOG_STATUS = SWITCH_WATCHDOG_STATUS

        # APPEARANCE

        self.COLOR_BACKGROUND_APP = COLOR_BACKGROUND_APP
        self.COLOR_ENTRY = COLOR_ENTRY
        self.COLOR_EXPLORER_LEFT = COLOR_EXPLORER_LEFT
        self.COLOR_EXPLORER_RIGHT = COLOR_EXPLORER_RIGHT
        self.COLOR_BUTTON = COLOR_BUTTON
        self.COLOR_FAV_BUTTON = COLOR_FAV_BUTTON
        self.COLOR_BACKGROUND_SEARCH = COLOR_BACKGROUND_SEARCH
        self.COLOR_SEARCH_TEXT = COLOR_SEARCH_TEXT
        self.FONT_STYLE = FONT_STYLE
        self.FONT_STYLE_COLOR = FONT_STYLE_COLOR

    def to_dict(self) -> dict:
        return {
            # GENERAL
            "SWITCH_COPY_STATUS": self.SWITCH_COPY_STATUS,
            "SWITCH_MOVE_STATUS": self.SWITCH_MOVE_STATUS,
            "SWITCH_DUPLICATE_STATUS": self.SWITCH_DUPLICATE_STATUS,
            "SWITCH_COMPRESS_STATUS": self.SWITCH_COMPRESS_STATUS,
            "SWITCH_UNCOMPRESS_STATUS": self.SWITCH_UNCOMPRESS_STATUS,
            # DIRECTORYS
            "FAV_PATH_LIST_1": self.FAV_PATH_LIST_1,
            "FAV_PATH_LIST_2": self.FAV_PATH_LIST_2,
            "EXP_1_PATH": self.EXP_1_PATH,
            "EXP_2_PATH": self.EXP_2_PATH,
            "SHOW_DIR_LAST": self.SHOW_DIR_LAST,
            "SWITCH_IMG_STATUS": self.SWITCH_IMG_STATUS,
            "SWITCH_WATCHDOG_STATUS": self.SWITCH_WATCHDOG_STATUS,
            # APPEARANCE
            "COLOR_BACKGROUND_APP": self.COLOR_BACKGROUND_APP,
            "COLOR_ENTRY": self.COLOR_ENTRY,
            "COLOR_EXPLORER_LEFT": self.COLOR_EXPLORER_LEFT,
            "COLOR_EXPLORER_RIGHT": self.COLOR_EXPLORER_RIGHT,
            "COLOR_BUTTON": self.COLOR_BUTTON,
            "COLOR_FAV_BUTTON": self.COLOR_FAV_BUTTON,
            "COLOR_BACKGROUND_SEARCH": self.COLOR_BACKGROUND_SEARCH,
            "COLOR_SEARCH_TEXT": self.COLOR_SEARCH_TEXT,
            "FONT_STYLE": self.FONT_STYLE,
            "FONT_STYLE_COLOR": self.FONT_STYLE_COLOR,
            "LANGUAGE": self.LANGUAGE,
        }

    def get_param_list(self) -> list:
        return self.to_dict().keys()

    def create_new_config(self):

        # GENERAL
        self.SWITCH_COPY_STATUS = False
        self.SWITCH_MOVE_STATUS = False
        self.SWITCH_DUPLICATE_STATUS = False
        self.SWITCH_COMPRESS_STATUS = False
        self.SWITCH_UNCOMPRESS_STATUS = False
        self.LANGUAGE = "es"

        # DIRECTORYS
        self.EXP_1_PATH = "/"
        self.EXP_2_PATH = "/"
        self.FAV_PATH_LIST_1 = []
        self.FAV_PATH_LIST_2 = []
        self.SHOW_DIR_LAST = True
        self.SWITCH_IMG_STATUS = True
        self.SWITCH_WATCHDOG_STATUS = True

        # APPEARANCE
        self.COLOR_BACKGROUND_APP = (
            Css_explorer_manager.PREDE_COLOR_BACKGROUND_APP
        )
        self.COLOR_ENTRY = Css_explorer_manager.PREDE_COLOR_ENTRY
        self.COLOR_EXPLORER_LEFT = (
            Css_explorer_manager.PREDE_COLOR_EXPLORER_LEFT
        )
        self.COLOR_EXPLORER_RIGHT = (
            Css_explorer_manager.PREDE_COLOR_EXPLORER_RIGHT
        )
        self.COLOR_BUTTON = Css_explorer_manager.PREDE_COLOR_BUTTON
        self.COLOR_FAV_BUTTON = Css_explorer_manager.PREDE_COLOR_FAV_BUTTON

        self.COLOR_BACKGROUND_SEARCH = (
            Css_explorer_manager.PREDE_COLOR_BACKGROUND_SEARCH
        )
        self.COLOR_SEARCH_TEXT = Css_explorer_manager.PREDE_COLOR_SEARCH_TEXT
        self.FONT_STYLE = Css_explorer_manager.PREDE_FONT_STYLE
        self.FONT_STYLE_COLOR = Css_explorer_manager.PREDE_FONT_STYLE_COLOR
