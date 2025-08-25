# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from pathlib import Path
import zipfile


class CompressionManager:

    def uncompress_manager(file: Path):

        name = file.name.lower()
        suffix = file.suffix.lower()

        if suffix == ".zip":
            return CompressionManager.uncompress_zipfile(file, file.parent)

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
            return {
                "status": False,
                "msg": _(
                    (
                        "El archivo no corresponde"
                        " a un archivo comprimido o empaquetado."
                    )
                ),
            }

    def uncompress_zipfile(file: Path, dst_dir: Path) -> bool:
        try:
            if not zipfile.is_zipfile(file):
                return {
                    "status": False,
                    "msg": _("El archivo no es un comprimido zip"),
                }

            with zipfile.ZipFile(file, "r") as myzip:

                names = myzip.namelist()

                top_level = {
                    name.split("/")[0] for name in names if name.strip()
                }
                new_name_dir = file.stem
                dst_dir = Path(dst_dir / new_name_dir)

                if dst_dir.exists():
                    return {
                        "status": False,
                        "msg": _("El directorio destino ya existe"),
                    }

                total_size_uncompressed = 0

                for info in myzip.infolist():
                    total_size_uncompressed += info.file_size

                zip_size = file.stat().st_size
                compressed_ratio = total_size_uncompressed / zip_size

                if compressed_ratio > 500:
                    return {
                        "status": False,
                        "msg": _(
                            (
                                "El ratio de compresión es demasiado elevado,"
                                " por seguridad, no se descomprimirá"
                            )
                        ),
                    }

                if len(top_level) > 1:
                    dst_dir.mkdir()
                    myzip.extractall(dst_dir)
                else:
                    myzip.extractall(dst_dir)

                return {
                    "status": True,
                    "msg": "ok",
                }
        except FileExistsError as e:
            return e
        except Exception as e:
            return e
