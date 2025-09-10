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

            ##################################################
            ## HAY QUE HACER VALIDACIONES DE STATUS = FALSE ## noqa :E226
            ##################################################

            if not permissions["status"]:
                print("permissions FALSE")
                continue

            if not owner_group["status"]:
                print("Owner group FALSE")
                continue

            permission_data = permissions["msg"]
            uid = owner_group["msg"]["user_id"]
            user_name = owner_group["msg"]["user_name"]
            gid = owner_group["msg"]["group_id"]
            group_name = owner_group["msg"]["group_name"]

            properties = PropertiesEnty(
                path, permission_data, uid, user_name, gid, group_name
            )
            self.list_store.append(properties)

        columns_header = [
            "path",
            "permissions",
            "uid",
            "gid",
        ]

        selection = Gtk.SingleSelection.new(model=self.list_store)
        columnview = Gtk.ColumnView.new()
        columnview.set_model(selection)

        for property_name in columns_header:

            if property_name == "path":
                column_name = _("RUTA")
            elif property_name == "permissions":
                column_name = _("PERMISOS")
            elif property_name == "uid":
                column_name = _("PROPIETARIO")
            elif property_name == "gid":
                column_name = _("GRUPO")

            self.factory = Gtk.SignalListItemFactory()
            self.factory.connect("setup", self.setup, property_name)
            self.factory.connect("bind", self.bind, property_name)

            column = Gtk.ColumnViewColumn.new(column_name, self.factory)

            # For column order
            property_expression = Gtk.PropertyExpression.new(
                PropertiesEnty, None, property_name
            )

            sorter = Gtk.StringSorter.new(property_expression)

            column.set_sorter(sorter)

            columnview.append_column(column)

        self.set_child(columnview)

        self.present()

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
                permissions = item.permissions[1:]
                sticky_label = Gtk.Label.new("Sticky")
                sticky_label.get_style_context().add_class("border")
                sticky_label.set_vexpand(True)
                sticky_label.set_valign(Gtk.Align.FILL)
                widget.attach(sticky_label, 0, 0, 1, 2)
                for index, char in enumerate(["User", "Group", "Other"]):
                    result = index * 3
                    ugo_label = Gtk.Label.new(char)
                    ugo_label.get_style_context().add_class("border")
                    widget.attach(ugo_label, result + 1, 0, 3, 1)
                    for perm_index, perm in enumerate(list(permissions)):
                        prm_label = Gtk.Label.new(perm)
                        prm_label.get_style_context().add_class("border")
                        widget.attach(prm_label, perm_index + 1, 1, 1, 1)

                sticky_output = ""
                for i, c in enumerate(list(permissions)):

                    if c == "s" and i == 2:
                        sticky_output += "U"
                    elif c == "s" and i == 5:
                        sticky_output += "G"
                    elif c == "t":
                        sticky_output += "O"

                    char_check = Gtk.CheckButton.new()
                    char_check.get_style_context().add_class("border")
                    if c == "-":
                        char_check.set_active(False)
                    else:
                        char_check.set_active(True)
                    widget.attach(char_check, i + 1, 2, 1, 1)

                string_list = Gtk.StringList.new(
                    ["U", "G", "O", "UG", "UO", "GO", "UGO"]
                )

                dropdown = Gtk.DropDown.new(model=string_list)
                widget.attach(dropdown, 0, 2, 1, 1)

                for i, v in enumerate(string_list):
                    if v.get_string() == sticky_output:
                        dropdown.set_selected(i)
                        print(i)

                print(f"STICKY RESULT: {sticky_output}")
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
