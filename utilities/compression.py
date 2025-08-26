# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from multiprocessing import Queue
from pathlib import Path
import shutil
from zipfile import ZipInfo
import zipfile


class CompressionManager:

    def uncompress_manager(file: Path, dst_dir: Path, q: Queue) -> dict:
        name = file.name.lower()
        suffix = file.suffix.lower()

        if suffix == ".zip":
            return CompressionManager.uncompress_zipfile(file, dst_dir, q)

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
            result = {
                "status": False,
                "msg": _(
                    (
                        "El archivo no corresponde"
                        " a un archivo comprimido o empaquetado."
                    )
                ),
            }
            q.put(result)
            return

    def uncompress_zipfile(file: Path, dst_dir: Path, q: Queue) -> dict:
        try:
            if not zipfile.is_zipfile(file):
                result = {
                    "status": False,
                    "msg": _("El archivo no es un comprimido zip"),
                }
                q.put(result)
                return

            with zipfile.ZipFile(file, "r") as myzip:

                names = myzip.namelist()

                top_level = {
                    name.split("/")[0] for name in names if name.strip()
                }
                new_name_dir = file.stem
                dst_dir = Path(dst_dir / new_name_dir)

                if dst_dir.exists():
                    result = {
                        "status": False,
                        "msg": _("El directorio destino ya existe"),
                    }
                    q.put(result)
                    return

                total_size_uncompressed = (
                    CompressionManager.get_uncompresset_size_zip(
                        myzip.infolist()
                    )
                )

                zip_size = file.stat().st_size
                compressed_ratio = total_size_uncompressed / zip_size

                if compressed_ratio > 500:
                    result = {
                        "status": False,
                        "msg": _(
                            (
                                "El ratio de compresión es demasiado elevado,"
                                " por seguridad, no se descomprimirá"
                            )
                        ),
                    }
                    q.put(result)
                    return

                if len(top_level) > 1:
                    dst_dir.mkdir()
                    myzip.extractall(dst_dir)
                else:
                    myzip.extractall(dst_dir)
                result = {
                    "status": True,
                    "msg": "ok",
                }
                q.put(result)
                return
        except FileExistsError as e:
            return e
        except Exception as e:
            return e

    def get_dst_suficient_space(file_list: list, dst_dir: Path) -> bool:
        total_size_uncompressed_all_files = 0
        for file in file_list:
            suffix = file.suffix.lower()
            if suffix == ".zip":
                if zipfile.is_zipfile(file):
                    with zipfile.ZipFile(file, "r") as myzip:
                        total_size_uncompressed_all_files += (
                            CompressionManager.get_uncompresset_size_zip(
                                myzip.infolist()
                            )
                        )
        free_space = shutil.disk_usage(dst_dir).free
        return total_size_uncompressed_all_files < free_space

    def get_uncompresset_size_zip(info_list: list[ZipInfo]):
        total_size_uncompressed = 0

        for info in info_list:
            total_size_uncompressed += info.file_size

        return total_size_uncompressed
