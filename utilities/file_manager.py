# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from entity.file_or_directory_info import File_or_directory_info
from entity.properties_enty import PropertiesEnty
from multiprocessing import Queue
from threading import Thread
from queue import Empty
import subprocess
from pathlib import Path
import time
import shutil
import pwd
import grp
import stat
import os
import gi
from gi.repository import Gio, Gtk, GLib

gi.require_version("Gtk", "4.0")


class File_manager:

    def __init__(self):
        self.STOP_PROCESS = False

    def get_path_list(self, path: Path) -> Gio.ListStore:
        """
        Returns io.ListStore of files and directorys from path "path"
        or False is have any problem.
        """
        list_content = Gio.ListStore.new(File_or_directory_info)

        try:
            if not path == Path("/"):
                back_row = File_or_directory_info(path="..")
                back_row.type = "BACK"
                back_row.size = ".."
                back_row.date_created_str = ".."
                back_row.permissions = ".."

                list_content.append(back_row)

            # Sorted list with, .., directorys and files

            q = Queue()
            p = Thread(target=self.get_sorted_dir, args=(path, q))
            p.start()

            try:
                msg = q.get()
            except Empty:

                if p.exitcode == 0:
                    return True
                else:
                    return False

            if msg["status"]:
                ordered_list = msg["data"]
                for content in ordered_list:
                    new_info = File_or_directory_info(content.absolute())
                    list_content.append(new_info)
            else:
                return False

            return list_content
        except Exception as e:
            print(f"Excepción {e}")

    def custom_key(self, path: Path) -> tuple[int, str]:
        """
        Sort first list_content, '..' first, directorys on midle and files last
        """
        name = path.name
        if name == "..":
            group = 0
        elif path.is_dir():
            group = 1
        else:
            group = 2
        return (group, name.lower())

    def get_sorted_dir(self, path: Path, q: Queue):
        try:
            ordered_list = sorted(path.iterdir(), key=self.custom_key)

            q.put({"status": True, "data": ordered_list})
        except OSError as e:
            print(e)
            q.put({"status": False, "data": e})
        except Exception as e:
            print(e)
            q.put({"status": False, "data": e})

    def check_free_space(self, item_list: list, dst_dir: Path) -> bool:
        """
        Check if have space on destination location
        for copy or move all files and directorys
        """
        total_size = 0

        for item in item_list:
            if item.is_dir():
                for archivo in item.rglob("*"):
                    if archivo.exists():
                        total_size += archivo.stat().st_size
            else:
                total_size += item.stat().st_size

        dst_free_size = self.get_dst_free_size(dst_dir)

        if dst_free_size < total_size:
            return False

        return True

    def get_dst_free_size(self, dst_dir: Path):
        return shutil.disk_usage(dst_dir).free

    def get_type_folder(self, path: Path) -> str:
        """
        Go back through folders until you find what
        type of folder it is, network, local, other
        """
        tmp = path
        result = self.get_type_from_mounts(tmp)
        while not result["status"]:
            tmp = tmp.parent
            if path.is_relative_to(tmp):
                result = self.get_type_from_mounts(tmp)

        return result

    def get_type_from_mounts(self, path: Path) -> str:
        """
        Gets information from /proc/mount, to know what type of folder it is
        """
        with open("/proc/mounts") as f:
            for line in f:
                line_clean = line.strip()
                dev, mp, fstype, *_ = line_clean.split()
                if Path(mp) == path:
                    if dev.startswith("/dev"):
                        return {"status": "mount", "msg": "local"}
                    elif dev.startswith("//"):
                        return {"status": "mount", "msg": "network"}

            return self.get_types_from_fstab(path)

    def get_types_from_fstab(self, path: Path) -> str:
        """
        Gets information from /etc/fstab, to know what type of folder it is
        """
        with open("/etc/fstab") as f:
            for line in f:
                line_clean = line.strip()
                if not line_clean.startswith("#"):
                    if not line_clean == "":
                        dev, mp, fstype, *_ = line_clean.split()
                        if Path(mp) == path:
                            if dev.startswith("/dev") or dev.startswith(
                                "UUID"
                            ):
                                return {"status": "fstab", "msg": "local"}
                            elif dev.startswith("//"):
                                return {"status": "fstab", "msg": "network"}

            return {"status": False, "msg": "nothing"}

    def get_permissions(self, path: Path) -> dict:
        try:
            if not path.exists():
                return {
                    "status": False,
                    "msg": _(
                        "La ruta no existe",
                    ),
                }

            mode = os.stat(path).st_mode
            file_permissions = stat.filemode(mode)
            file_permissions_filtered = file_permissions[1:]
        except PermissionError as e:
            return {"status": False, "msg": e}

        return {"status": True, "msg": file_permissions_filtered}

    def get_owner_group(self, path: Path) -> dict:

        try:

            if not path.exists():
                return {
                    "status": False,
                    "msg": _(
                        "La ruta no existe",
                    ),
                }

            st = os.stat(path)
            user_id = st.st_uid
            group_id = st.st_gid
            user_name = pwd.getpwuid(user_id).pw_name
            group_name = grp.getgrgid(group_id).gr_name

        except PermissionError as e:
            return {"status": False, "msg": e}

        return {
            "status": True,
            "msg": {
                "user_name": user_name,
                "group_name": group_name,
            },
        }

    def change_permissions(
        self, win: Gtk.Window = None, path_list: list[PropertiesEnty] = None
    ) -> bool:
        try:
            cmd_to_execute = ""
            for propertieenty in path_list:
                path = Path(propertieenty.path)
                permissions = propertieenty.permissions
                mode = []
                n = 0
                for i in [3, 6, 9]:
                    mode.append(permissions[n:i])
                    n = i

                penalty_check = False
                if not path.exists():
                    continue

                for i, c in enumerate(mode):
                    if len(c) != 3:
                        penalty_check = True
                        break

                    listc = list(c)
                    if listc[0] not in ["r", "-"]:
                        penalty_check = True
                        break

                    if listc[1] not in ["w", "-"]:
                        penalty_check = True
                        break

                    if listc[2] not in ["x", "-", "s", "t"]:
                        penalty_check = True
                        break

                if penalty_check:
                    return {
                        "status": False,
                        "msg": _(
                            "Hay alguna incongruencia en los permisos",
                        ),
                    }

                mode_str = f"u={mode[0]},g={mode[1]},o={mode[2]}".replace(
                    "-", ""
                )

                if any(c.lower() not in ",=ugorwxst" for c in mode_str):
                    return {
                        "status": False,
                        "msg": _(
                            (
                                "El modo facilitado es incorrecto"
                                ", debe ser tipo entero 'u=rwx,g=rwx,o=rwx'"
                                " puede incluir sticky bit s o t"
                            ),
                        ),
                    }

                actual_user_id = os.getuid()
                st = os.stat(path)
                file_user_id = st.st_uid

                recursive_str = " "
                if propertieenty.recursive:
                    recursive_str += " -R "

                cmd_to_execute += f"chmod{recursive_str}{mode_str} {path} && "

            cmd_to_execute = cmd_to_execute.rstrip(" &&")

            with_pass = not actual_user_id == file_user_id

            return self.execute_cmd(win, cmd_to_execute, with_pass)

        except PermissionError as e:
            return {"status": False, "msg": e}
        return {"status": True, "msg": True}

    def change_owner_group(
        self, win: Gtk.Window, path_list: list[Path]
    ) -> dict:
        try:
            filtered_list = []
            if not path_list:
                return {
                    "status": False,
                    "msg": _(
                        "La lista de rutas vino vacia",
                    ),
                }
            else:
                for propertyenty in path_list:
                    path = Path(propertyenty.path)
                    if not path.exists():
                        continue
                    else:
                        user_str = propertyenty.user_name
                        group_str = propertyenty.group_name
                        try:
                            pwd.getpwnam(user_str)
                        except KeyError:
                            return {
                                "status": False,
                                "msg": _(f"El usuario {user_str}, no existe"),
                            }

                        try:
                            grp.getgrnam(group_str)
                        except KeyError:
                            return {
                                "status": False,
                                "msg": _(f"El grupo {group_str}, no existe"),
                            }

                        filtered_list.append(propertyenty)

            cmd_to_execute = ""
            recursive_str = ""
            for propertyenty in filtered_list:

                user_name = propertyenty.user_name
                group_name = propertyenty.group_name
                path = propertyenty.path

                if propertyenty.recursive:
                    recursive_str = "-R"

                cmd_to_execute += (
                    f"chown {recursive_str} "
                    f"{user_name}:{group_name} {path} && "
                )

            cmd_to_execute = cmd_to_execute.rstrip(" &&")

            return self.execute_cmd(win, cmd_to_execute, True)

        except PermissionError as e:
            return {"status": False, "msg": e}

    def execute_cmd(
        self, win: Gtk.Window, cmd_to_execute: str, with_pass: bool
    ) -> dict:
        if not shutil.which("pkexec"):
            cmd_to_execute = f"'{cmd_to_execute}'"
            # When pkexec is not available to request the password.
            q = Queue()

            passwd = ""
            with_root_str = ""
            if with_pass:

                def work(win, q):
                    from views.pop_up_windows.password_entry import (
                        PasswordWindow,
                    )

                    PasswordWindow(
                        win, q, "Es necesario que te identifique como root"
                    )

                GLib.idle_add(work, win, q)
                passwd = q.get()["msg"]
                with_root_str = "sudo -S "

                if passwd.lower() == "cancel":
                    return {"status": False, "msg": "Operación cancelada"}

            exec_str = (
                "faillock --user $(whoami) --reset;"
                f"echo '{passwd}' | "
                f"{with_root_str}bash -c {cmd_to_execute};"  # noqa: E501
                "sudo -k;"
                " exit\n"
            )

            return self.exec_tty_cmd(exec_str)
        else:
            if with_pass:
                cmd = ["pkexec", "bash", "-c"]
            else:
                cmd = ["bash", "-c"]

            cmd.append(cmd_to_execute)

        res = subprocess.run(cmd, capture_output=True, text=True)

        if res.returncode != 0:
            return {"status": False, "msg": res.stderr}

        return {"status": True, "msg": True}

    def exec_tty_cmd(self, exec_str: str):

        import pty

        master_fd, slave_fd = pty.openpty()
        cmd = ["bash"]
        process = subprocess.Popen(
            cmd,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            text=True,
        )

        # Wait a bit for the initial prompt to appear
        time.sleep(0.2)

        os.write(master_fd, exec_str.encode())
        os.close(slave_fd)
        while process.poll() is None:
            try:
                output = os.read(master_fd, 1024)
                if not output:
                    break
                text = output.decode("utf-8")

                if (
                    "sudo: no password was provided" in text
                    or "incorrect password" in text
                ):
                    return {
                        "status": False,
                        "msg": _("Password incorrecto"),
                    }
                    break
            except OSError:
                continue

        return {"status": True, "msg": True}

    def properties_path_list(
        self, path_list: list[Path], loading_label: Gtk.Label
    ) -> dict:
        folders = 0
        files = 0
        total_size = 0

        for path in path_list:
            if self.STOP_PROCESS:
                break
            result = self.properties_path(path, loading_label)

            folders += result["folders"]
            files += result["files"]
            total_size += result["total_size"]

        return {"folders": folders, "files": files, "total_size": total_size}

    def properties_path(self, path: Path, loading_label: Gtk.Label) -> dict:

        if path.is_dir():
            folders = 0
            files = 0
            size = 0

            for f in path.rglob("*"):
                if self.STOP_PROCESS:
                    break
                GLib.idle_add(loading_label.set_text, str(f.name))
                if f.is_file():
                    size += f.stat().st_size
                    files += 1
                else:
                    folders += 1

            return {"folders": folders, "files": files, "total_size": size}
        else:
            return {
                "folders": 0,
                "files": 1,
                "total_size": path.stat().st_size,
            }

    def get_size_and_unit(self, bytes_int: int) -> str:
        """
        Transforms bytes to the unit immediately preceding having decimal
        type 0.9 and assigns the unit
        """
        KBYTES = 1024
        start = True
        count = 0
        unit = ""
        while start:

            if not bytes_int > KBYTES:
                start = False
                continue

            bytes_int = bytes_int / KBYTES
            if bytes_int > 1:
                count += 1
            else:
                start = False

        if count == 0:
            unit = "Bytes"

        if count == 1:
            unit = "KB"

        if count == 2:
            unit = "MB"

        if count == 3:
            unit = "GB"

        if count == 4:
            unit = "TB"

        return f"{round(bytes_int, 2)}{unit}"

    def set_stop(self, stop: bool) -> None:
        self.STOP_PROCESS = stop

    def mount_or_umount(
        self, win: Gtk.ApplicationWindow, path: Path, mount: bool
    ) -> dict:

        cmd = ""

        if mount:
            cmd = f"mount {path}"
        else:
            cmd = f"umount {path}"

        return self.execute_cmd(win, cmd, True)
