# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from entity.File_or_directory_info import File_or_directory_info
from multiprocessing import Process, Queue
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


gi.require_version("Gtk", "4.0")
from gi.repository import Gio  # noqa: E402


class File_manager:

    def get_path_list(path: Path) -> Gio.ListStore:
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

            def get_sorted_dir(path: Path, q: Queue):
                try:
                    ordered_list = sorted(
                        path.iterdir(), key=File_manager.custom_key
                    )
                    q.put({"ok": True, "data": ordered_list})
                except OSError:
                    q.put({"ok": False, "data": None})
                except Exception:
                    q.put({"ok": False, "data": None})

            q = Queue()
            p = Process(target=get_sorted_dir, args=(path, q))
            p.start()
            p.join(0.3)

            try:
                msg = q.get_nowait()
            except Empty:

                if p.exitcode == 0:
                    return True
                else:
                    return False

            if msg["ok"]:
                ordered_list = msg["data"]
                for content in ordered_list:
                    new_info = File_or_directory_info(content.absolute())
                    list_content.append(new_info)
            else:
                return False

            return list_content
        except Exception as e:
            print(f"Excepción {e}")

    def custom_key(path: Path) -> tuple[int, str]:
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
        while not result:
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
                        return "local"
                    elif dev.startswith("//"):
                        return "network"

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
                                return "local"
                            elif dev.startswith("//"):
                                return "network"

            return False

    def get_dir_or_file_size(path: Path) -> dict:

        if path.is_dir():
            folders = 0
            files = 0
            size = 0

            for f in path.rglob("*"):
                if f.is_file():
                    size += f.stat().st_size
                    files += 1
                else:
                    folders += 1

            return {"folders": folders, "files": files, "size": size}
        else:
            return {"folders": 0, "files": 0, "size": path.stat().st_size}

    def get_permissions(path: Path) -> dict:
        try:
            if not path.exists():
                return {
                    "status": False,
                    "msg": _(
                        "La ruta no existe",
                    ),
                }

            if not os.access(path, os.X_OK):
                return {
                    "status": False,
                    "msg": _(
                        (
                            "No dispone de permiso de"
                            " ejecución en el directorio contenedor"
                        )
                    ),
                }

            mode = os.stat(path).st_mode
            file_permissions = stat.filemode(mode)
            file_permissions_filtered = file_permissions[1:]
        except PermissionError as e:
            return {"status": False, "msg": e}

        return {"status": True, "msg": file_permissions_filtered}

    def get_owner_group(path: Path) -> dict:

        try:

            if not path.exists():
                return {
                    "status": False,
                    "msg": _(
                        "La ruta no existe",
                    ),
                }

            if not os.access(path, os.X_OK):
                return {
                    "status": False,
                    "msg": _(
                        (
                            "No dispone de permiso de"
                            " ejecución en el directorio contenedor"
                        )
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

    def change_permissions(path: Path, mode: list, recursive: bool) -> bool:

        try:
            penalty_check = False

            if not path.exists():
                return {
                    "status": False,
                    "msg": _(
                        "La ruta no existe",
                    ),
                }

            for i, c in enumerate(mode):
                if len(c) != 3:
                    penalty_check = True
                    break

                listc = list(c)
                if listc[0] != "r" and listc[0] != "-":
                    penalty_check = True

                if listc[1] != "w" and listc[1] != "-":
                    penalty_check = True
                    break

                if (
                    listc[2] != "x"
                    and listc[2] != "-"
                    and listc[2] != "s"
                    and listc[2] != "t"
                ):
                    penalty_check = True
                    break

            if penalty_check:
                return {
                    "status": False,
                    "msg": _(
                        "Hay alguna incongruencia en los permisos",
                    ),
                }

            mode_str = f"u={mode[0]},g={mode[1]},o={mode[2]}".replace("-", "")

            # mode need int, octal type ex: 0o777 or 0o1777
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
            recursive_str = ""
            if recursive:
                recursive_str = "-R"

            actual_user_id = os.getuid()
            st = os.stat(path)
            file_user_id = st.st_uid

            if not shutil.which("pkexec"):

                need_passwd = ""
                sudo = ""

                if not actual_user_id == file_user_id:
                    # TODO PASSWORD WITH UI
                    passwd = ""
                    sudo = "sudo -S"
                    need_passwd = f"echo '{passwd}' |"

                exec_str = (
                    "faillock --user $(whoami) --reset;"
                    f"{need_passwd} "
                    f"{sudo} chmod {recursive_str} {mode_str} {str(path)};"
                    "sudo -k;"
                    " exit\n"
                )

                return File_manager.exec_tty_cmd(exec_str)
            else:
                cmd = []
                if not actual_user_id == file_user_id:
                    cmd.append("pkexec")
                cmd.append("chmod")
                if recursive:
                    cmd.append("-R")
                cmd.append(mode_str)
                cmd.append(path)
            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode != 0:
                return {"status": False, "msg": res.stderr}

        except PermissionError as e:
            return {"status": False, "msg": e}
        return {"status": True, "msg": True}

    def change_owner_group(path_list: list[Path]) -> dict:
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

            cmd_paths = ""
            recursive_str = ""
            for propertyenty in filtered_list:

                user_name = propertyenty.user_name
                group_name = propertyenty.group_name
                path = propertyenty.path

                if propertyenty.recursive:
                    recursive_str = "-R"

                cmd_paths += (
                    f"chown {recursive_str} "
                    f"{user_name}:{group_name} {path} && "
                )

            cmd_paths = cmd_paths.rstrip(" &&")

            if not shutil.which("pkexec"):
                cmd_paths = f"'{cmd_paths}'"
                # When pkexec is not available to request the password.
                # TODO PASSWORD WITH UI
                passwd = ""
                exec_str = (
                    "faillock --user $(whoami) --reset;"
                    f"echo '{passwd}' | "
                    f"sudo -S bash -c {cmd_paths};"  # noqa: E501
                    "sudo -k;"
                    " exit\n"
                )
                return File_manager.exec_tty_cmd(exec_str)
            else:

                cmd = ["pkexec", "bash", "-c"]
                cmd.append(cmd_paths)

            res = subprocess.run(cmd, capture_output=True, text=True)

            if res.returncode != 0:
                return {"status": False, "msg": res.stderr}

        except PermissionError as e:
            return {"status": False, "msg": e}

        return {"status": True, "msg": True}

    def exec_tty_cmd(exec_str: str):

        import pty

        master_fd, slave_fd = pty.openpty()
        # cmd = ["ls", path]
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

    def properties_work(path_list: list[Path]) -> None:
        folders = 0
        files = 0
        total_size = 0

        for path in path_list:
            print(f"FILE MANAGER PATH: {path}")
            result = File_manager.get_dir_or_file_size(path)
            folders += result["folders"]
            files += result["files"]
            total_size += result["size"]

        print(f"Folders: {folders}")
        print(f"Files: {folders}")
        print(f"Total size: {total_size}")
