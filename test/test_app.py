# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import pytest
from pathlib import Path
from utilities.file_manager import File_manager
from entity.properties_enty import PropertiesEnty
import shutil
import os

APP_HOME = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def dir_and_files_for_test():

    test_folder = Path(f"{APP_HOME}")
    path_test = Path(f"{test_folder}/folder_to_test")

    if not path_test.exists():
        path_test.mkdir()

    if path_test.exists():
        file = path_test / "file_test_TRUE.test"
        file.touch(exist_ok=True)

    yield file

    if path_test.exists():
        shutil.rmtree(path_test)


def test_change_permissions_validations_permissions_leng(
    dir_and_files_for_test,
):
    path = dir_and_files_for_test

    permissions_test_list = [
        [
            "",
            "",
            "",
        ],
        [
            "rwxae",
            "rwxee",
            "rwxee",
        ],
        [
            "rwxae",
            "rwxee",
            "rwxee",
        ],
        [
            "rwxa",
            "rwx",
            "rwx",
        ],
        [
            "rwx",
            "rwxa",
            "rwx",
        ],
        [
            "rwx",
            "rwx",
            "rwxa",
        ],
        [
            "rwx",
            "rwx",
            "rwx",
        ],
    ]

    propertieenty_list = []

    for permissions in permissions_test_list:
        propertieenty_list.append(
            PropertiesEnty(path, permissions, "mel0n", "mel0n")
        )

    assert (
        File_manager().change_permissions(None, propertieenty_list)["status"]
        is False
    )


# def test_change_permissions_true(dir_and_files_for_test):
#     file = dir_and_files_for_test

#     import itertools

#     usuario = [
#         "---",
#         "--x",
#         "-w-",
#         "-wx",
#         "r--",
#         "r-x",
#         "rw-",
#         "rwx",
#         "rws",
#         "-ws",
#         "--s",
#     ]
#     grupo = [
#         "---",
#         "--x",
#         "-w-",
#         "-wx",
#         "r--",
#         "r-x",
#         "rw-",
#         "rwx",
#         "rws",
#         "-ws",
#         "--s",
#     ]
#     otros = [
#         "---",
#         "--x",
#         "-w-",
#         "-wx",
#         "r--",
#         "r-x",
#         "rw-",
#         "rwx",
#         "rwt",
#         "-wt",
#         "--t",
#     ]

#     combinaciones = list(itertools.product(usuario, grupo, otros))
#     propertieenty_list = [
#         PropertiesEnty(file, permissions, "mel0n", "mel0n")
#         for permissions in combinaciones
#     ]

#     salida = File_manager().change_permissions(None, propertieenty_list)
#     print(salida)
#     assert salida


# def test_change_permissions_false(dir_and_files_for_test):
#     file = dir_and_files_for_test
#     assert (
#         File_manager().change_permissions(file, ["", "rws", "r-x"])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["r", "rws", "r-x"])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["w", "rws", "r-x"])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["x", "rws", "r-x"])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["rwa", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["rab", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["ffff", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["123", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["a", "rws", "r-x"])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["bdd", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["wrx", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["rrs", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["rwst", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["rsw", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["", "", ""])["status"]
#         is False
#     )
#     assert (
#         File_manager().change_permissions(file, ["swr", "rws", "r-x"])[
#             "status"
#         ]
#         is False
#     )
