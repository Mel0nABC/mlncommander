# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from multiprocessing import Queue
from pathlib import Path
import threading
import shutil
import subprocess
import re
import pty
import os

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib  # noqa : E402


class CompressionManager:

    def __init__(self, compression_win: "Window"):  # noqa : F821

        self.uncompress_popen = None
        self.compression_win = compression_win
        self.last_path = None
        self.last_dst_folder = None
        self.EXEC_SEVEN_Z_TYPE = self.validate_7zip_installed()

    def stop_uncompress(self) -> None:
        if self.uncompress_popen:
            self.uncompress_popen.kill()

    def delete_last_uncompress(self):
        if self.last_dst_folder.exists():
            # Delete directory when cancel extract
            threading.Thread(
                target=shutil.rmtree, args=(str(self.last_dst_folder),)
            ).start()

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
                self.EXEC_SEVEN_Z_TYPE,
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
            cmd = [self.EXEC_SEVEN_Z_TYPE, "t", file, "-pNothingTheNothing123"]

            check_pass = subprocess.run(cmd, capture_output=True, text=True)

            password = ""

            if "password" in check_pass.stderr:
                to_work = Queue()
                self.compression_win.get_archivo_password(to_work, file)
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

        import secrets
        import string

        dst_zip_folder = Path(f"{dst_dir}/{path.stem}")

        while dst_zip_folder.exists():
            text = "".join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(1)
            )
            dst_zip_folder = Path(f"{dst_zip_folder}{text}")

        cmd = [
            self.EXEC_SEVEN_Z_TYPE,
            "x",
            path,
            f"-o{dst_zip_folder}",
            f"-p{password}",
            "-aou",
        ]

        master_df, slave_fd = pty.openpty()
        self.uncompress_popen = subprocess.Popen(
            cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True
        )
        os.close(slave_fd)

        self.last_path = path
        self.last_dst_folder = dst_zip_folder

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
                    percent = int(match.group(1))
                    self.compression_win.set_percent(percent)
            except OSError:
                continue
        return {
            "status": True,
            "msg": _("El proceso finalizó satisfactoriamente"),
        }

    def compress_work(
        self,
        compress_win: Gtk.Window,
        win: Gtk.ApplicationWindow,
        progress: Gtk.ProgressBar,
        cmd: str,
        file_name: str,
        output_file: str,
        dst_explorer: "explorer",  # noqa: F821
    ) -> None:

        if win.config.SWITCH_COMPRESS_STATUS:
            GLib.idle_add(compress_win.to_background, None)

        master_df, slave_fd = pty.openpty()
        compress_win.compress_popen = subprocess.Popen(
            cmd, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, text=True
        )
        os.close(slave_fd)

        while compress_win.compress_popen.poll() is None:
            try:
                output = os.read(master_df, 1024)
                if not output:
                    break
                texto = output.decode("utf-8")

                if "Everything is Ok" in texto:
                    GLib.idle_add(progress.set_fraction, 1)
                    GLib.idle_add(
                        dst_explorer.load_new_path, compress_win.dst_dir
                    )

                match = re.search(r"(.{2})%", texto)
                if match:
                    fraction = int(match.group(1)) / 100
                    GLib.idle_add(progress.set_fraction, fraction)
                    if dst_explorer.actual_path == compress_win.dst_dir:
                        GLib.idle_add(
                            dst_explorer.load_new_path, compress_win.dst_dir
                        )
            except OSError:
                continue

        if compress_win.stop_compress:
            GLib.idle_add(progress.set_fraction, 0)
            for i in compress_win.dst_dir.iterdir():
                if file_name in str(i) and output_file in str(i):
                    i.unlink()
        else:
            GLib.idle_add(progress.set_fraction, 1)
            compress_win.compress_activate = False
            compress_win.stop_compress = False
            compress_win.btn_extract.set_label(label=_("Comprimir"))

        compress_win.compress_popen = None

    def get_dst_suficient_space(self, file_list: list, dst_dir: Path) -> bool:
        total_size_uncompressed_all_files = 0
        for file in file_list:
            cmd = [self.EXEC_SEVEN_Z_TYPE, "l", file]
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
        cmd = [self.EXEC_SEVEN_Z_TYPE, "l", file]
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

    def validate_7zip_installed(self) -> str:
        import App

        path = Path(f"{App.APP_HOME}/files/7zip/7z")
        if not shutil.which("7z"):
            return str(path)
        return "7z"
