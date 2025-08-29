# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from multiprocessing import Queue
from pathlib import Path
import shutil
import subprocess
import re
import pty
import os


class CompressionManager:

    def __init__(self, win: "UncompressWindow"):  # noqa : F821

        self.uncompress_popen = None
        self.win = win

    def stop_uncompress(self) -> None:
        if self.uncompress_popen:
            self.uncompress_popen.kill()

    def uncompress(self, file: Path, dst_dir: Path, q: Queue) -> dict:
        try:

            if file.is_dir():
                result = {
                    "status": False,
                    "msg": _(("Ha seleccionado una carpeta,")),
                }
                q.put(result)
                return

            if self.check_file_compressed_ratio(file):
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

            cmd = [
                "7z",
                "l",
                file,
            ]

            p = subprocess.run(cmd, capture_output=True, text=True)

            if p.returncode != 0:
                result = {
                    "status": False,
                    "msg": _("El archivo no es compatible con 7z"),
                }
                q.put(result)
                return

            # Only test password to check if the file have
            cmd = ["7z", "t", file, "-pNothingTheNothing123"]

            check_pass = subprocess.run(cmd, capture_output=True, text=True)

            password = ""

            if "password" in check_pass.stderr:
                to_work = Queue()
                self.win.get_archivo_password(to_work)
                pass_response = to_work.get()
                if pass_response["status"]:
                    password = pass_response["msg"]
                else:
                    result = {
                        "status": False,
                        "msg": _("Cancelado en la solicitud de contraseña"),
                    }
                    q.put(result)
                    return

            result = self.uncompress_file_with_7z(file, dst_dir, password)
            q.put(result)
            return
        except FileExistsError as e:
            return e
        except Exception as e:
            return e

    def uncompress_file_with_7z(
        self, path: Path, dst_dir: Path, password: str
    ) -> None:
        cmd = ["7z", "x", path, f"-o{dst_dir}", f"-p{password}", "-aou"]

        master_df, slave_fd = pty.openpty()
        self.uncompress_popen = subprocess.Popen(
            cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True
        )
        os.close(slave_fd)

        while self.uncompress_popen.poll() is None:
            try:
                output = os.read(master_df, 1024)
                if not output:
                    break
                texto = output.decode("utf-8")

                if "Wrong password" in texto:
                    return {
                        "status": False,
                        "msg": _("contraseña errónea"),
                    }

                match = re.search(r"(.{2})%", texto)
                if match:
                    percent = f"{match.group(1)}%"
                    self.win.set_percent(percent)
            except OSError:
                continue
        return {
            "status": True,
            "msg": _("El proceso finalizó satisfactoriamente"),
        }

    def get_dst_suficient_space(self, file_list: list, dst_dir: Path) -> bool:
        total_size_uncompressed_all_files = 0
        for file in file_list:
            cmd = ["7z", "l", file]
            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode != 0:
                continue

            total_size = None

            for line in res.stdout.splitlines():
                m = re.search(r"\s+(\d+)\s+(\d+)\s+\d+\s+files", line)
                if m:
                    total_size = int(m.group(1))
                    total_size_uncompressed_all_files += total_size
                    break

        free_space = shutil.disk_usage(dst_dir).free
        return total_size_uncompressed_all_files < free_space

    def check_file_compressed_ratio(self, file: Path) -> bool:
        cmd = ["7z", "l", file]
        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0:
            return

        total_size_uncompressed = None
        total_size_compressed = None

        for line in res.stdout.splitlines():
            m = re.search(r"\s+(\d+)\s+(\d+)\s+\d+\s+files", line)
            if m:
                total_size_uncompressed = int(m.group(1))
                total_size_compressed = int(m.group(2))
                break

        return (total_size_uncompressed / total_size_compressed) > 500
