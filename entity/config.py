# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from css.explorer_css import Css_explorer_manager


class ConfigEntity:

    __gtype_name__ = "ConfigEntity"

    def __init__(self):
        super().__init__()

        # GENERAL

        self.SWITCH_COPY_STATUS = None
        self.SWITCH_MOVE_STATUS = None
        self.SWITCH_DUPLICATE_STATUS = None
        self.SWITCH_COMPRESS_STATUS = None
        self.SWITCH_UNCOMPRESS_STATUS = None
        self.LANGUAGE = None

        # DIRECTORYS

        self.FAV_PATH_LIST_1 = None
        self.FAV_PATH_LIST_2 = None
        self.EXP_1_PATH = None
        self.EXP_2_PATH = None
        self.SHOW_DIR_LAST = None
        self.SWITCH_IMG_STATUS = None
        self.SWITCH_WATCHDOG_STATUS = None

        # APPEARANCE

        self.COLOR_BACKGROUND_APP = None
        self.COLOR_ENTRY = None
        self.COLOR_EXPLORER_LEFT = None
        self.COLOR_EXPLORER_RIGHT = None
        self.COLOR_BUTTON = None
        self.COLOR_FAV_BUTTON = None
        self.COLOR_BACKGROUND_SEARCH = None
        self.COLOR_SEARCH_TEXT = None
        self.FONT_STYLE = None
        self.FONT_STYLE_COLOR = None

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
