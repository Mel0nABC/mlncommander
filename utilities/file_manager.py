# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from entity.File_or_directory_info import File_or_directory_info
from pathlib import Path
import gi
import shutil
from multiprocessing import Process, Queue
from queue import Empty

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
                    total_size += archivo.stat().st_size
            else:
                total_size += item.stat().st_size

        dst_free_size = shutil.disk_usage(dst_dir).free

        if dst_free_size < total_size:
            return False

        return True

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
