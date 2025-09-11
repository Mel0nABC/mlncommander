# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from entity.properties_enty import PropertiesEnty
from css.explorer_css import Css_explorer_manager
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GObject  # noqa E402


class Properties(Gtk.Window):
    def __init__(self, win: Gtk.Window, path_list: list = None):
        super().__init__(transient_for=win)

        header = Gtk.HeaderBar()
        header.set_title_widget(
            Gtk.Label(label=_("Propiedades de archivos y carpetas"))
        )
        self.set_titlebar(header)

        self.win = win
        self.path_list = path_list

        # Load css
        self.css_manager = Css_explorer_manager(self)
        self.css_manager.load_css_properties()

        self.get_style_context().add_class("app_background")
        self.get_style_context().add_class("font")
        self.get_style_context().add_class("font-color")

        main_vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        notebook = Gtk.Notebook.new()

        notebook.append_page(
            self.create_permissions(), Gtk.Label.new(_("Permisos"))
        )
        notebook.append_page(
            self.create_information(), Gtk.Label.new(_("Información"))
        )

        main_vertical_box.append(notebook)

        self.set_child(main_vertical_box)

        self.present()

    def create_information(self) -> Gtk.Box:

        information_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        information_box.append(
            Gtk.Label.new("INFORMACION ARCHIVOS Y CARPETAS")
        )

        # image = Gtk.Image.new()

        return information_box

    def create_permissions(self) -> Gtk.Box:

        self.list_store = Gio.ListStore.new(PropertiesEnty)
        from utilities.sistem_info import SistemInformation

        self.user_list = Gtk.StringList.new(
            SistemInformation.get_sistem_users()
        )
        # self.store_users = Gio.ListStore.new(item_type=String)
        self.group_list = Gtk.StringList.new(
            SistemInformation.get_sistem_groups()
        )

        for index, path in enumerate(self.path_list):
            permissions = File_manager.get_permissions(path)
            owner_group = File_manager.get_owner_group(path)

            ##################################################
            ## HAY QUE HACER VALIDACIONES DE STATUS = FALSE ## noqa :E226
            ##################################################

            if not permissions["status"]:
                print(
                    "## HAY QUE HACER VALIDACIONES DE STATUS = FALSE ## noqa :E226"
                )
                continue

            if not owner_group["status"]:
                print(
                    "## HAY QUE HACER VALIDACIONES DE STATUS = FALSE ## noqa :E226"
                )
                continue

            permission_data = permissions["msg"]
            user_name = owner_group["msg"]["user_name"]
            group_name = owner_group["msg"]["group_name"]

            properties = PropertiesEnty(
                path, permission_data, user_name, group_name
            )

            self.list_store.append(properties)

        columns_header = [
            "path",
            "permissions",
            "user_name",
            "group_name",
        ]

        properties_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        self.selection = Gtk.SingleSelection.new(model=self.list_store)
        self.columnview = Gtk.ColumnView.new()

        self.columnview.get_style_context().add_class("properties-columnview")

        self.columnview.set_model(self.selection)

        properties_box.append(self.columnview)
        properties_box.set_hexpand(True)

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
            column.set_expand(True)
            column.set_resizable(True)
            column.set_sorter(sorter)

            self.columnview.append_column(column)

        horizontal_btn_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )

        horizontal_btn_box.set_halign(Gtk.Align.END)
        horizontal_btn_box.set_hexpand(True)
        horizontal_btn_box.set_margin_top(30)

        btn_accept = Gtk.Button.new_with_label(_("Aceptar"))
        btn_accept.set_margin_end(20)
        btn_cancel = Gtk.Button.new_with_label(_("Cancelar"))

        def on_accept(button: Gtk.Button):
            win = Gtk.Window(
                title=_("Ajustando permisos..."), transient_for=self
            )
            # win.set_size_request(300, 300)
            self.vertical_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=5
            )
            self.vertical_box.set_margin_top(50)
            self.vertical_box.set_margin_end(50)
            self.vertical_box.set_margin_bottom(50)
            self.vertical_box.set_margin_start(50)
            win.set_child(self.vertical_box)

            spinner = Gtk.Spinner.new()
            spinner.start()

            grid = Gtk.Grid.new()

            self.vertical_box.append(spinner)
            self.vertical_box.append(grid)

            win.present()

            for i, propertiesenty in enumerate(self.list_store):
                path_lbl = Gtk.Label.new(propertiesenty.path)
                path_lbl.set_halign(Gtk.Align.START)
                grid.attach(path_lbl, 0, i, 1, 1)

                response = propertiesenty.save_data_permissions()
                response_lbl = Gtk.Label.new()
                response_lbl.set_margin_start(30)

                if response["status"]:
                    response_lbl.set_text("✅")
                else:
                    response_lbl.set_text("❌")
                grid.attach(response_lbl, 1, i, 1, 1)
            spinner.stop()

            btn_close = Gtk.Button.new_with_label(_("Cerrar"))
            btn_close.set_margin_top(40)
            btn_close.set_halign(Gtk.Align.END)

            def on_close(btn: Gtk.Button) -> None:
                win.destroy()
                self.destroy()

            btn_close.connect("clicked", on_close)
            self.vertical_box.append(btn_close)

        def on_cancel(button: Gtk.Button):
            self.destroy()

        btn_accept.connect("clicked", on_accept)
        btn_cancel.connect("clicked", on_cancel)

        horizontal_btn_box.append(btn_accept)
        horizontal_btn_box.append(btn_cancel)

        properties_box.append(horizontal_btn_box)

        properties_box.get_style_context().add_class("properties")

        return properties_box

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

                # Sticky section
                sticky_label = Gtk.Label.new("Sticky")
                sticky_label.set_vexpand(True)
                sticky_label.set_valign(Gtk.Align.FILL)
                grid.attach(sticky_label, 0, 0, 1, 2)

                # Recursive section
                recursive_label = Gtk.Label.new(_("Recursivo"))
                recursive_label.set_valign(Gtk.Align.FILL)
                grid.attach(recursive_label, 10, 0, 1, 2)

                cell.set_child(grid)
            else:
                drop_user_group = Gtk.DropDown.new()
                drop_user_group.set_vexpand(False)
                cell.set_child(drop_user_group)

    def bind(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:

        propertiesenty = cell.get_item()
        if propertiesenty:
            widget = cell.get_child()
            controller = Gtk.EventControllerMotion()
            controller.connect("enter", self.focust_row_with_some_widget, cell)
            widget.add_controller(controller)

            if isinstance(widget, Gtk.Grid):
                row_labels = 1
                for index, char in enumerate(["User", "Group", "Other"]):
                    result = index * 3
                    ugo_label = Gtk.Label.new(char)
                    widget.attach(ugo_label, result + 1, 0, 3, 1)
                    for perm_index, perm in enumerate(list("rwx")):
                        prm_label = Gtk.Label.new(perm)
                        propertiesenty.labels_list.append(prm_label)
                        self.set_names_to_widgets(prm_label, perm_index, perm)
                        widget.attach(prm_label, row_labels, 1, 1, 1)
                        row_labels += 1

                permissions_list = propertiesenty.permissions_list

                for i, c in enumerate(permissions_list):
                    char_check = Gtk.CheckButton.new()
                    self.set_names_to_widgets(char_check, i, c)
                    propertiesenty.checks_btn_list.append(char_check)

                    if c == "-":
                        char_check.set_active(False)
                    else:
                        char_check.set_active(True)

                    def set_permission_changes(button, cell, property):
                        propertiesenty = cell.get_item()
                        coordinate = button.get_name()
                        checked = button.get_active()
                        response = propertiesenty.set_changes_permissions(
                            coordinate, checked
                        )

                        if response:
                            self.update_labels_and_propertyenty(propertiesenty)

                    char_check.connect(
                        "toggled",
                        set_permission_changes,
                        cell,
                        property_name,
                    )

                    widget.attach(char_check, i + 1, 2, 1, 1)

                string_list = Gtk.StringList.new(
                    ["-", "U", "G", "O", "UG", "UO", "GO", "UGO"]
                )

                sticky_dropdown = Gtk.DropDown.new(model=string_list)
                sticky_dropdown.set_size_request(90, -1)

                for i, value in enumerate(sticky_dropdown.get_model()):
                    sticky = value.get_string()
                    if sticky == propertiesenty.sticky:
                        sticky_dropdown.set_selected(i)

                def on_changed_sticky(
                    dropdrown: Gtk.DropDown,
                    pspec: GObject.GParamSpec,
                    cell: Gtk.ColumnViewCell,
                    property_name: str,
                ) -> None:
                    propertiesenty = cell.get_item()
                    response = propertiesenty.set_sticky(
                        sticky_dropdown.get_selected_item().get_string()
                    )

                    if response:
                        self.update_labels_and_propertyenty(propertiesenty)

                sticky_dropdown.connect(
                    "notify::selected-item",
                    on_changed_sticky,
                    cell,
                    property_name,
                )
                widget.attach(sticky_dropdown, 0, 2, 1, 1)

                recursive_check = char_check = Gtk.CheckButton.new()
                recursive_check.set_name("recursive")
                recursive_check.set_halign(Gtk.Align.CENTER)
                recursive_check.set_valign(Gtk.Align.CENTER)
                widget.attach(recursive_check, 10, 2, 1, 2)

                def update_recursive_check(
                    button: Gtk.CheckButton = None,
                    cell: Gtk.ColumnViewCell = None,
                    property_name: str = None,
                ) -> None:
                    if button:
                        propertiesenty = cell.get_item()
                        propertiesenty.set_recursive(button.get_active())

                recursive_check.connect(
                    "toggled",
                    update_recursive_check,
                    cell,
                    property_name,
                )

            else:

                if property_name == "user_name":
                    widget.set_model(self.user_list)

                    for i, value in enumerate(widget.get_model()):
                        user = value.get_string()
                        if user == propertiesenty.user_name:
                            widget.set_selected(i)

                    def on_changed_user(
                        dropdrown: Gtk.DropDown,
                        pspec: GObject.GParamSpec,
                        cell: Gtk.ColumnViewCell,
                        property_name: str,
                    ) -> None:
                        propertiesenty = cell.get_item()
                        new_owner = dropdrown.get_selected_item().get_string()
                        propertiesenty.set_owner(new_owner)

                    widget.connect(
                        "notify::selected-item",
                        on_changed_user,
                        cell,
                        property_name,
                    )

                elif property_name == "group_name":
                    widget.set_model(self.group_list)
                    for i, value in enumerate(widget.get_model()):
                        group = value.get_string()
                        if group == propertiesenty.group_name:
                            widget.set_selected(i)

                    def on_changed_group(
                        dropdrown: Gtk.DropDown,
                        pspec: GObject.GParamSpec,
                        cell: Gtk.ColumnViewCell,
                        property_name: str,
                    ) -> None:
                        propertiesenty = cell.get_item()
                        new_group = dropdrown.get_selected_item().get_string()
                        propertiesenty.set_group(new_group)

                    widget.connect(
                        "notify::selected-item",
                        on_changed_group,
                        cell,
                        property_name,
                    )
                if property_name == "path":
                    widget.set_text(propertiesenty.path)

                widget.set_hexpand(False)
                widget.set_valign(Gtk.Align.CENTER)
                widget.set_halign(Gtk.Align.CENTER)
                widget.set_size_request(250, -1)

    def focust_row_with_some_widget(self, control, x, y, cell) -> None:
        flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )
        position = cell.get_position()
        self.columnview.scroll_to(position, None, flags)

    def update_labels_and_propertyenty(
        self, propertiesenty: GObject.Object
    ) -> None:
        for i, value in enumerate(propertiesenty.permissions_list):
            propertiesenty.labels_list[i].set_text(value)

    def set_names_to_widgets(self, widget, i, c):
        if i >= 0 and i < 3:
            widget.set_name(f"{i}={c}")
        elif i >= 3 and i < 6:
            widget.set_name(f"{i}={c}")
        elif i >= 6 and i < 9:
            widget.set_name(f"{i}={c}")
