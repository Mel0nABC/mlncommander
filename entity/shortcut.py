# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
class Shortcut:

    def __init__(
        self,
        explorer: "Explorer",  # noqa F821
        first_key: str,
        second_key: str,
        method: str,
    ):

        self.explorer = explorer
        self.first_key = first_key
        self.second_key = second_key
        self.method = method

    def to_dict(self) -> dict:
        return {
            "first_key": self.first_key,
            "second_key": self.second_key,
            "method": self.method,
        }
