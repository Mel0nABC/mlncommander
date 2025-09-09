# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from pathlib import Path
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GObject  # noqa E402


class Properties(Gtk.Window):
    def __init__(self, win: Gtk.Window, path_list: list = None):
        super().__init__()

        self.list_store = Gio.ListStore.new(PropertiesEnty)

        for index, path in enumerate(path_list):
            permissions = File_manager.get_permissions(path)
            owner_group = File_manager.get_owner_group(path)

            if not permissions["status"]:
                print("permissions FALSE")
                continue

            if not owner_group["status"]:
                print("Owner group FALSE")
                continue

            permission_data = permissions["msg"].replace("0o", "")

            uid = owner_group["msg"]["user_id"]
            user_name = owner_group["msg"]["user_name"]
            gid = owner_group["msg"]["group_id"]
            group_name = owner_group["msg"]["group_name"]

            permission_rwt_numbers = list(permission_data)
            symbolic_result = []

            def transform_octal_to_symbolic(octal_numer: str, sticky: bool):
                if octal_numer == "7":
                    if sticky:
                        return "rws"
                    return "rwx"
                elif octal_numer == "6":
                    return "rw-"
                elif octal_numer == "5":
                    if sticky:
                        return "r-s"
                    return "r-x"
                elif octal_numer == "4":
                    return "r--"
                elif octal_numer == "3":
                    if sticky:
                        return "-ws"
                    return "-wx"
                elif octal_numer == "2":
                    return "-w-"
                elif octal_numer == "1":
                    if sticky:
                        return "--s"
                    return "--x"
                elif octal_numer == "0":
                    return "---"

            if len(permission_rwt_numbers) == 3:
                for num in permission_rwt_numbers:
                    symbolic_result.append(
                        transform_octal_to_symbolic(num, False)
                    )
            else:
                sticky = permission_rwt_numbers[0]
                print(f"STICKY: {sticky}")
                for index, num in enumerate(permission_rwt_numbers):
                    if index == 0:
                        continue

                    if sticky == "4" and index == 1:
                        symbolic_result.append(
                            transform_octal_to_symbolic(num, True)
                        )
                    elif sticky == "2" and index == 2:
                        symbolic_result.append(
                            transform_octal_to_symbolic(num, True)
                        )
                    elif sticky == "1" and index == 3:
                        symbolic_result.append(
                            transform_octal_to_symbolic(num, True)
                        )
                    else:
                        symbolic_result.append(
                            transform_octal_to_symbolic(num, False)
                        )

            print(symbolic_result)

        #     properties = PropertiesEnty(
        #         path, permission_data, uid, user_name, gid, group_name
        #     )
        #     self.list_store.append(properties)

        # columns_header = [
        #     "path",
        #     "permissions",
        #     "uid",
        #     "gid",
        # ]

        # selection = Gtk.SingleSelection.new(model=self.list_store)
        # columnview = Gtk.ColumnView.new()
        # columnview.set_model(selection)

        # for property_name in columns_header:

        #     if property_name == "path":
        #         column_name = _("RUTA")
        #     elif property_name == "permissions":
        #         column_name = _("PERMISOS")
        #     elif property_name == "uid":
        #         column_name = _("PROPIETARIO")
        #     elif property_name == "gid":
        #         column_name = _("GRUPO")

        #     self.factory = Gtk.SignalListItemFactory()
        #     self.factory.connect("setup", self.setup, property_name)
        #     self.factory.connect("bind", self.bind, property_name)

        #     column = Gtk.ColumnViewColumn.new(column_name, self.factory)

        #     # For column order
        #     property_expression = Gtk.PropertyExpression.new(
        #         PropertiesEnty, None, property_name
        #     )

        #     sorter = Gtk.StringSorter.new(property_expression)

        #     column.set_sorter(sorter)

        #     columnview.append_column(column)

        # self.set_child(columnview)

        # self.present()

    def setup(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        if property_name == "path":
            cell.set_child(Gtk.Label.new(""))
        else:
            if property_name == "permissions":
                grid = Gtk.Grid(column_spacing=10, row_spacing=5)
                lbl_sticky = Gtk.Label.new("Sticky")
                lbl_user = Gtk.Label.new(_("Usuario"))
                lbl_group = Gtk.Label.new(_("Grupo"))
                lbl_other = Gtk.Label.new(_("Otros"))
                grid.attach(lbl_sticky, 0, 0, 1, 1)
                grid.attach(lbl_user, 1, 0, 1, 1)
                grid.attach(lbl_group, 2, 0, 1, 1)
                grid.attach(lbl_other, 3, 0, 1, 1)
                cell.set_child(grid)
            else:
                entry = Gtk.Entry()
                cell.set_child(entry)

            def on_changed(entry, cell, property_name):
                obj = cell.get_item()
                # old_value = getattr(obj, property_name)
                new_value = entry.get_text()
                setattr(obj, property_name, new_value)
                obj.notify(property_name)
                entry.connect("changed", on_changed, cell, property_name)

    def bind(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        item = cell.get_item()
        if item:
            widget = cell.get_child()
            if isinstance(widget, Gtk.Grid):
                permissions = item.permissions

                if len(permissions) == 3:
                    permissions = f"0{permissions}"

                entry_sticky = Gtk.Entry.new()
                entry_user = Gtk.Entry.new()
                entry_group = Gtk.Entry.new()
                entry_other = Gtk.Entry.new()

                entry_sticky.set_text(permissions[0])
                entry_user.set_text(permissions[1])
                entry_group.set_text(permissions[2])
                entry_other.set_text(permissions[3])

                widget.attach(entry_sticky, 0, 1, 1, 1)
                widget.attach(entry_user, 1, 1, 1, 1)
                widget.attach(entry_group, 2, 1, 1, 1)
                widget.attach(entry_other, 3, 1, 1, 1)
            else:
                value = item.get_property(property_name)
                text_value = str(value)
                if property_name == "uid":
                    text_value = item.get_property("user_name")
                elif property_name == "gid":
                    text_value = item.get_property("group_name")

                widget.set_text(text_value)

    def get_properties(self):
        print("lala")
        # threading.Thread(
        #     target=File_manager.properties_work, args=(self.path_list,)
        # ).start()


class PropertiesEnty(GObject.Object):

    __gtype_name__ = "PropertiesEnty"

    path = GObject.Property(type=GObject.TYPE_STRING, default="default")
    permissions = GObject.Property(type=GObject.TYPE_STRING, default="default")
    uid = GObject.Property(type=GObject.TYPE_STRING, default="default")
    user_name = GObject.Property(type=GObject.TYPE_STRING, default="default")
    gid = GObject.Property(type=GObject.TYPE_STRING, default="default")
    group_name = GObject.Property(type=GObject.TYPE_STRING, default="default")

    def __init__(
        self,
        path: Path,
        permissions: str,
        uid: int,
        user_name: str,
        gid: int,
        group_name: str,
    ):
        super().__init__()

        self.path = path
        self.permissions = permissions
        self.uid = uid
        self.user_name = user_name
        self.gid = gid
        self.group_name = group_name

    def to_dict(self):
        return {
            "path": self.path,
            "permissions": self.permissions,
            "uid": self.uid,
            "user_name": self.user_name,
            "gid": self.gid,
            "group_name": self.group_name,
        }
