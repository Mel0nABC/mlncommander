# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import pwd
import grp


class SistemInformation:

    def get_sistem_users():
        user_list = [user.pw_name for user in pwd.getpwall()]
        user_list.sort()
        return user_list

    def get_sistem_groups():
        group_list = [group.gr_name for group in grp.getgrall()]
        group_list.sort()
        return group_list
