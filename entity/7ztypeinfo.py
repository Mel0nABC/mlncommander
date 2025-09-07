# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
class SevenZTypeInfo:

    __gtype_name__ = "SevenZTypeInfo"

    def __init__(
        self,
        EXTENSION: str = None,
        COMPRESSION: bool = None,
        DESCOMPRESSION: bool = None,
        LEVELS: bool = None,
        PASSWORD: bool = None,
        COMMENT: str = None,
    ):
        super().__init__()
        self.EXTENSION = EXTENSION
        self.COMPRESSION = COMPRESSION
        self.DESCOMPRESSION = DESCOMPRESSION
        self.LEVELS = LEVELS
        self.PASSWORD = PASSWORD
        self.COMMENT = COMMENT

    def to_dict(self) -> dict:
        return {
            "EXTENSION": self.EXTENSION,
            "COMPRESSION": self.COMPRESSION,
            "DESCOMPRESSION": self.DESCOMPRESSION,
            "LEVELS": self.LEVELS,
            "PASSWORD": self.PASSWORD,
            "COMMENT": self.COMMENT,
        }

    def get_param_list(self) -> list:
        return self.to_dict().keys()
