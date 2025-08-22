# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from pathlib import Path
import zipfile


class CompressionManager:

    def __init__(self):
        print("COMPRESIón")

    def uncompress_manager(self, file: Path):
        name = file.name.lower()  # para ignorar mayúsculas/minúsculas
        suffix = file.suffix.lower()

        if suffix == ".zip":
            return self.uncompress_zipfile(file, file.parent)

            # For view  management
            # result = self.uncompress_zipfile(file, file.parent)
            # if isinstance(result, Exception):
            #     print(f"ERROR: {result}")
            # else:
            #     print("todo bien")

        elif suffix == ".rar":
            print("RAR (.rar)")

        elif suffix == ".7z":
            print("7-Zip (.7z)")

        elif suffix == ".tar":
            print("TAR (.tar)")

        elif suffix == ".gz" and (
            name.endswith(".tar.gz") or name.endswith(".tgz")
        ):
            print("TAR + Gzip (.tar.gz / .tgz)")

        elif suffix == ".bz2" and (
            name.endswith(".tar.bz2")
            or name.endswith(".tbz")
            or name.endswith(".tb2")
        ):
            print("TAR + Bzip2 (.tar.bz2 / .tbz / .tb2)")

        elif suffix == ".xz" and (
            name.endswith(".tar.xz") or name.endswith(".txz")
        ):
            print("TAR + XZ (.tar.xz / .txz)")

        elif suffix == ".lzma":
            print("LZMA (.lzma)")

        elif suffix == ".lzip":
            print("LZIP (.lzip)")

        elif suffix == ".jar":
            print("JAR (.jar)")

        elif suffix == ".war":
            print("WAR (.war)")

        else:
            print(f"Tipo desconocido ({file})")

    def uncompress_zipfile(self, file: Path, dst_dir: Path) -> bool:
        try:
            if not zipfile.is_zipfile(file):
                return False

            with zipfile.ZipFile(file, "r") as myzip:
                file_count = len(myzip.infolist())
                if file_count > 1:
                    new_name_dir = file.stem
                    new_dir = dst_dir / new_name_dir
                    new_dir.mkdir(exist_ok=False)
                    myzip.extractall(new_dir)
                else:
                    myzip.extractall()

                return True
        except FileExistsError as e:
            return e
        except Exception as e:
            return e
