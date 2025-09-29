# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from utilities.file_manager import File_manager
from utilities.log_manager import LogManager
from entity.properties_enty import PropertiesEnty
from utilities.sistem_info import SistemInformation
from controls.actions import Actions
import threading
import time
from pathlib import Path
import gi
from gi.repository import Gtk, Gio, GLib, GObject, Pango

gi.require_version("Gtk", "4.0")


class Permissions(Gtk.Box):

    def __init__(
        self, win: Gtk.Window, path_list: list[Path], information: Gtk.Box
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.path_list = path_list
        self.win = win
        self.log_manager = LogManager(self.win)
        self.action = Actions()
        self.list_store = Gio.ListStore.new(PropertiesEnty)
        self.information = information
        self.result_total_files = self.information.result_total_files

        self.user_list = Gtk.StringList.new(
            SistemInformation.get_sistem_users()
        )

        self.group_list = Gtk.StringList.new(
            SistemInformation.get_sistem_groups()
        )

        self.get_style_context().add_class("properties")
        self.set_hexpand(True)

        # Add widgets
        self.append(self.create_top_menu())
        self.append(self.create_permissions())
        self.append(self.create_bottom_menu())

    def create_top_menu(self) -> Gtk.Box:
        # START TOP MENU

        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )
        self.main_center = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )
        self.main_center.set_halign(Gtk.Align.CENTER)
        self.main_box.set_size_request(-1, 200)
        self.main_box.set_margin_bottom(20)

        self.main_box.get_style_context().add_class("border-style")

        left_box = self.create_left_content()
        right_box = self.create_right_content()

        self.main_center.append(left_box)
        self.main_center.append(right_box)
        self.main_box.append(self.main_center)
        return self.main_box
        # FINAL TOP MENU

    def create_left_content(self) -> Gtk.Box:

        def waiting_to_create(loading_box: Gtk.Box):
            checking = True
            while checking:
                time.sleep(0.2)
                self.result_total_files = self.information.result_total_files
                if self.result_total_files:
                    left_box = Gtk.Box(
                        orientation=Gtk.Orientation.VERTICAL, spacing=5
                    )
                    left_box.set_valign(Gtk.Align.CENTER)

                    left_content = Gtk.Box(
                        orientation=Gtk.Orientation.VERTICAL, spacing=5
                    )
                    left_content.set_margin_top(20)
                    left_content.set_margin_end(20)
                    left_content.set_margin_bottom(20)
                    left_content.set_margin_start(20)
                    left_content.set_hexpand(True)

                    title_label = Gtk.Label.new(_("Información del contenido"))
                    title_label.set_halign(Gtk.Align.START)
                    title_label.set_valign(Gtk.Align.CENTER)
                    title_label.set_margin_bottom(20)

                    left_content.append(title_label)

                    folders_str_lsb = Gtk.Label.new(_("Subcarpetas totales:"))
                    files_str_lsb = Gtk.Label.new(_("Archivos totales:"))
                    total_size_str_lsb = Gtk.Label.new(_("Tamaño total:"))

                    folders_str_lsb.set_xalign(0.0)
                    files_str_lsb.set_xalign(0.0)
                    total_size_str_lsb.set_xalign(0.0)

                    folders_str_lsb.set_width_chars(25)
                    files_str_lsb.set_width_chars(25)
                    total_size_str_lsb.set_width_chars(25)

                    folders_lsb = Gtk.Label.new(
                        str(self.result_total_files["folders"])
                    )
                    files_lsb = Gtk.Label.new(
                        str(self.result_total_files["files"])
                    )
                    total_size_lsb = Gtk.Label.new(
                        File_manager().get_size_and_unit(
                            self.result_total_files["total_size"]
                        )
                    )

                    grid = Gtk.Grid(column_spacing=10, row_spacing=5)

                    grid.attach(folders_str_lsb, 0, 0, 1, 1)
                    grid.attach(files_str_lsb, 0, 1, 1, 1)
                    grid.attach(total_size_str_lsb, 0, 2, 1, 1)
                    grid.attach(folders_lsb, 1, 0, 1, 1)
                    grid.attach(files_lsb, 1, 1, 1, 1)
                    grid.attach(total_size_lsb, 1, 2, 1, 1)

                    left_content.append(grid)

                    left_box.append(left_content)

                    GLib.idle_add(self.main_center.remove, loading_box)
                    GLib.idle_add(self.main_center.prepend, left_box)
                    checking = False

        loading_box = self.add_loading_box()
        threading.Thread(target=waiting_to_create, args=(loading_box,)).start()

        if not self.result_total_files:
            return loading_box

    def create_right_content(self) -> Gtk.Box:

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        right_box.set_margin_top(20)
        right_box.set_margin_bottom(20)
        right_box.set_margin_start(20)

        right_content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        right_content.set_hexpand(True)

        right_content.set_margin_top(20)
        right_content.set_margin_bottom(20)
        right_content.set_margin_start(20)

        title_label = Gtk.Label.new(_("Aplicar a todo"))
        title_label.set_halign(Gtk.Align.START)
        title_label.set_margin_bottom(20)

        all_selection_grid = Gtk.Grid(column_spacing=2, row_spacing=0)

        sticky_lbl = Gtk.Label.new("Sticky")
        string_list = Gtk.StringList.new(
            ["-", "U", "G", "O", "UG", "UO", "GO", "UGO"]
        )

        sticky_dropdown = Gtk.DropDown.new(model=string_list)
        sticky_dropdown.set_size_request(90, -1)

        all_selection_grid.attach(sticky_lbl, 0, 0, 1, 2)
        all_selection_grid.attach(sticky_dropdown, 0, 2, 1, 1)

        def on_changed_sticky_all(
            dropdown: Gtk.DropDown,
            pspec: GObject.GParamSpec,
        ) -> None:
            sticky_for_all = dropdown.get_selected_item().get_string()
            for propertiesenty in self.list_store:
                propertiesenty.set_sticky(sticky_for_all)

                sticky_dropdown = propertiesenty.sticky_dropdown

                for i, value in enumerate(sticky_dropdown.get_model()):
                    sticky = value.get_string()
                    if sticky == propertiesenty.sticky:
                        sticky_dropdown.set_selected(i)

                self.update_labels_and_propertyenty(propertiesenty)

        sticky_dropdown.connect("notify::selected-item", on_changed_sticky_all)

        colum_labels = 1
        param_num = 0
        for index, char in enumerate(["User", "Group", "Other"]):
            result = index * 3
            ugo_label = Gtk.Label.new(char)
            all_selection_grid.attach(ugo_label, result + 1, 0, 3, 1)
            for perm_index, perm in enumerate(list("rwx")):
                prm_label = Gtk.Label.new(perm)
                check = Gtk.CheckButton()
                check.set_name(f"{param_num}={perm}")

                def check_all(button: Gtk.CheckButton):
                    coordinated = button.get_name()
                    check = button.get_name().split("=")
                    check_index = check[0]
                    check_status = button.get_active()

                    for propertiesenty in self.list_store:

                        propertiesenty.set_changes_permissions(
                            coordinated, check_status
                        )

                        check_btn = propertiesenty.checks_btn_list[
                            f"{check_index}"
                        ]

                        check_btn.set_active(check_status)

                        self.update_labels_and_propertyenty(propertiesenty)

                check.connect("toggled", check_all)

                all_selection_grid.attach(prm_label, colum_labels, 1, 1, 1)
                all_selection_grid.attach(check, colum_labels, 2, 1, 1)
                colum_labels += 1
                param_num += 1

        # Recursive section
        recursive_label = Gtk.Label.new(_("Recursivo"))
        recursive_label.set_valign(Gtk.Align.FILL)
        recursive_check = Gtk.CheckButton.new()
        recursive_check.set_hexpand(False)
        recursive_check.set_halign(Gtk.Align.CENTER)

        def on_selec_recursive_all(checkbutton: Gtk.CheckButton):
            check = recursive_check.get_active()
            for propertiesenty in self.list_store:
                propertiesenty.recursive_check_button.set_active(check)

        recursive_check.connect("toggled", on_selec_recursive_all)

        drop_user = Gtk.DropDown.new()
        drop_user.set_vexpand(False)
        drop_user.set_hexpand(False)
        drop_user.set_valign(Gtk.Align.CENTER)
        drop_user.set_halign(Gtk.Align.CENTER)

        drop_user.set_model(self.user_list)
        self.set_dropdown_search_mode(drop_user)

        def on_changed_user_all(
            dropdrown: Gtk.DropDown, pspec: GObject.GParamSpec
        ) -> None:
            new_user = dropdrown.get_selected_item().get_string()
            index = dropdrown.get_selected()
            for propertiesenty in self.list_store:
                response = propertiesenty.set_owner(new_user)

                if response:
                    propertiesenty.user_dropdown.set_selected(index)

        drop_user.connect("notify::selected-item", on_changed_user_all)

        drop_group = Gtk.DropDown.new()
        drop_group.set_vexpand(False)
        drop_group.set_hexpand(False)
        drop_group.set_valign(Gtk.Align.CENTER)
        drop_group.set_halign(Gtk.Align.CENTER)

        drop_group.set_model(self.group_list)
        self.set_dropdown_search_mode(drop_group)

        def on_changed_group_all(
            dropdrown: Gtk.DropDown, pspec: GObject.GParamSpec
        ) -> None:
            new_group = dropdrown.get_selected_item().get_string()
            index = dropdrown.get_selected()
            for propertiesenty in self.list_store:

                response = propertiesenty.set_group(new_group)

                if response:
                    propertiesenty.group_dropdown.set_selected(index)

        drop_group.connect("notify::selected-item", on_changed_group_all)

        drop_user.set_margin_start(20)
        drop_group.set_margin_start(20)

        owner_label = Gtk.Label.new(_("Propietario"))
        group_label = Gtk.Label.new(_("Grupo"))

        owner_label.set_margin_start(20)
        group_label.set_margin_start(20)

        all_selection_grid.attach(recursive_label, 10, 0, 1, 2)
        all_selection_grid.attach(recursive_check, 10, 2, 1, 1)
        all_selection_grid.attach(owner_label, 11, 0, 1, 1)
        all_selection_grid.attach(drop_user, 11, 2, 1, 1)
        all_selection_grid.attach(group_label, 12, 0, 1, 1)
        all_selection_grid.attach(drop_group, 12, 2, 1, 1)

        right_content.append(title_label)
        right_content.append(all_selection_grid)
        right_box.append(right_content)

        return right_box

    def create_permissions(self) -> Gtk.Box:

        permission_data = None
        group_name = None
        user_name = None
        for index, path in enumerate(self.path_list):
            permissions = File_manager().get_permissions(path)
            owner_group = File_manager().get_owner_group(path)

            if not permissions["status"]:
                permission_data = "---------"
            else:
                permission_data = permissions["msg"]

            if not owner_group["status"]:
                user_name = "None"
                group_name = "None"
            else:
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

        self.columnview = Gtk.ColumnView.new()
        self.columnview.set_show_row_separators(True)

        self.selection = Gtk.SingleSelection.new(model=self.list_store)

        self.columnview.set_model(self.selection)

        self.column_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )
        self.column_box.set_margin_bottom(20)

        self.column_scroll = Gtk.ScrolledWindow.new()
        self.column_scroll.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        scroll_margin = 20
        self.column_scroll.set_margin_top(scroll_margin)
        self.column_scroll.set_margin_end(scroll_margin)
        self.column_scroll.set_margin_bottom(scroll_margin)
        self.column_scroll.set_margin_start(scroll_margin)

        self.column_box.append(self.column_scroll)

        self.column_scroll.set_vexpand(True)
        self.column_scroll.set_hexpand(True)

        self.column_scroll.set_child(self.columnview)

        for property_name in columns_header:

            if property_name == "path":
                column_name = _("RUTA")
            elif property_name == "permissions":
                column_name = _("PERMISOS")
            elif property_name == "user_name":
                column_name = _("PROPIETARIO")
            elif property_name == "group_name":
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

        # Header text configure, with al_SeveR @Chete

        first_row = self.columnview.get_first_child()
        list_list_model = first_row.observe_children()

        for column_title in list_list_model:
            box = column_title.get_first_child()
            box.set_halign(Gtk.Align.CENTER)

        # Load css
        self.column_box.get_style_context().add_class("border-style")

        return self.column_box

    def setup(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        if property_name == "path":
            path_label = Gtk.Label.new()
            path_label.set_halign(Gtk.Align.START)
            cell.set_child(path_label)
        else:
            if property_name == "permissions":
                grid = Gtk.Grid(column_spacing=1, row_spacing=0)
                grid.set_margin_top(3)
                grid.set_margin_bottom(3)

                # Sticky section
                sticky_label = Gtk.Label.new("Sticky")

                grid.attach(sticky_label, 0, 0, 1, 1)

                # Recursive section
                recursive_label = Gtk.Label.new(_("Recursivo"))

                grid.attach(recursive_label, 10, 0, 1, 1)

                cell.set_child(grid)
            else:
                drop_user_group = Gtk.DropDown.new()
                drop_user_group.set_vexpand(False)
                drop_user_group.set_hexpand(False)
                drop_user_group.set_valign(Gtk.Align.CENTER)
                drop_user_group.set_halign(Gtk.Align.CENTER)
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
                    char_name = char_check.get_name()
                    index = char_name.split("=")[0]

                    propertiesenty.checks_btn_list[index] = char_check

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
                propertiesenty.sticky_dropdown = sticky_dropdown

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
                widget.attach(sticky_dropdown, 0, 1, 1, 2)

                recursive_check = char_check = Gtk.CheckButton.new()
                recursive_check.set_name("recursive")

                recursive_check.set_hexpand(False)
                recursive_check.set_halign(Gtk.Align.CENTER)

                propertiesenty.recursive_check_button = recursive_check

                widget.attach(recursive_check, 10, 1, 1, 2)

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
                    propertiesenty.user_dropdown = widget
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
                    propertiesenty.group_dropdown = widget
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

                self.set_dropdown_search_mode(widget)

                if property_name == "path":
                    path = propertiesenty.path
                    no_read_permissios = "---------"
                    if propertiesenty.permissions == no_read_permissios:
                        no_access = _(
                            (
                                "No tiene acceso a los permisos,"
                                " si dispones contraseña root,"
                                " puedes cambiarlos"
                            )
                        )
                        widget.set_markup(
                            (
                                f"{path}\n<span foreground='#AC161C'>"
                                f"{no_access}</span>"
                            )
                        )
                    else:
                        widget.set_text(path)

                    widget.set_ellipsize(Pango.EllipsizeMode.START)

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

    def create_bottom_menu(self) -> Gtk.Box:

        horizontal_btn_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=5
        )

        horizontal_btn_box.set_halign(Gtk.Align.END)
        horizontal_btn_box.set_hexpand(True)

        btn_accept = Gtk.Button.new_with_label(_("Aceptar"))
        btn_accept.set_margin_end(20)
        btn_cancel = Gtk.Button.new_with_label(_("Cancelar"))

        def on_accept(button: Gtk.Button):

            for propertiesenty in self.list_store:

                if "None".lower() in [
                    propertiesenty.user_name.lower(),
                    propertiesenty.group_name.lower(),
                ]:

                    text = _(
                        (
                            "No puede haber ningún usuario"
                            " ni grupo None, revisa la lista"
                        )
                    )
                    self.action.show_msg_alert(self.win, text)
                    return

            info_win = Gtk.Window()

            header = Gtk.HeaderBar()
            header.set_title_widget(
                Gtk.Label(label=_("Resultado de los cambios"))
            )
            info_win.set_titlebar(header)

            info_win.set_transient_for(self.win)

            info_win.get_style_context().add_class("app_background")
            info_win.get_style_context().add_class("font")
            info_win.get_style_context().add_class("font-color")

            self.vertical_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=5
            )
            self.vertical_box.set_margin_top(40)
            self.vertical_box.set_margin_end(40)
            self.vertical_box.set_margin_bottom(40)
            self.vertical_box.set_margin_start(40)

            self.vertical_box.set_hexpand(True)
            self.vertical_box.set_vexpand(True)

            grid = Gtk.Grid.new()

            info_win.set_child(self.vertical_box)

            self.vertical_box.append(grid)

            spinner = Gtk.Spinner()
            spinner.start()

            self.vertical_box.append(spinner)

            info_win.present()

            btn_close = Gtk.Button.new_with_label(_("Cerrar"))
            btn_close.set_halign(Gtk.Align.END)
            btn_close.set_margin_top(20)
            self.set_sensitive(False)

            def on_close(btn: Gtk.Button) -> None:
                info_win.destroy()
                self.win.destroy()

            btn_close.connect("clicked", on_close)
            self.vertical_box.append(btn_close)

            import threading

            threading.Thread(
                target=self.work_changes, args=(info_win, spinner, grid)
            ).start()

        def on_cancel(button: Gtk.Button):
            self.win.destroy()

        btn_accept.connect("clicked", on_accept)
        btn_cancel.connect("clicked", on_cancel)

        horizontal_btn_box.append(btn_accept)
        horizontal_btn_box.append(btn_cancel)
        return horizontal_btn_box

    def work_changes(self, win, spinner, grid):
        # Check changes

        owner_group_changes = False
        permissions_changes = False
        for propertiesenty in self.list_store:

            if not propertiesenty.filter_data_permission():
                permissions_changes = True

            if not propertiesenty.filter_data_owners_changed():
                owner_group_changes = True

        resp_owner_group = {"status": True, "msg": False}
        if owner_group_changes:

            resp_owner_group = File_manager().change_owner_group(
                win, self.list_store
            )

            if resp_owner_group["status"]:
                self.log_manager.print_status_on_log(
                    "OWNER_GROUP", None, None, self.list_store
                )  # Noqa : E501

        resp_permissions = {"status": True, "msg": False}
        if permissions_changes:

            resp_permissions = File_manager().change_permissions(
                win, self.list_store
            )

            if resp_permissions["status"]:
                self.log_manager.print_status_on_log(
                    "PERMISSIONS", None, None, self.list_store
                )  # Noqa : E501

        response_lbl_perm = Gtk.Label.new()

        msg_test = _("Operación realizada satisfactoriamente:")

        response_lbl_perm.set_text(
            _(
                (
                    f"{msg_test}\n\n"
                    f"  Permisos: {"✅" if resp_permissions["msg"] else _("Sin cambios")}\n"  # noqa: E501
                    f"  Propietario y grupos: {"✅" if resp_owner_group["msg"] else _("Sin cambios")}"  # noqa: E501
                )
            )
        )

        if not resp_permissions["status"] or not resp_owner_group["status"]:
            response_lbl_perm.set_text(
                _(
                    (
                        "Hubo algún problema:\n\n"
                        f"  Permisos: {resp_permissions["msg"]}\n"
                        f"  Propietario y grupos: {resp_owner_group["msg"]}"
                    )
                )
            )

        grid.attach(response_lbl_perm, 0, 0, 1, 1)

        if not owner_group_changes and not permissions_changes:
            response_lbl_perm.set_text(_("No han habido cambios."))

        spinner.stop()

    def add_loading_box(self) -> Gtk.Box:
        loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        loading_box.set_valign(Gtk.Align.CENTER)
        loading_box.set_size_request(400, 50)

        spinner_header = Gtk.Spinner.new()
        spinner_header.set_size_request(50, 50)
        spinner_header.set_hexpand(False)
        spinner_header.set_valign(Gtk.Align.CENTER)
        spinner_header.start()

        lbl_loading_header = Gtk.Label.new(_("Cargando ..."))
        lbl_loading_header.set_ellipsize(Pango.EllipsizeMode.START)
        lbl_loading_header.set_max_width_chars(200)
        lbl_loading_header.set_margin_top(20)

        loading_box.append(spinner_header)
        loading_box.append(lbl_loading_header)

        return loading_box

    def set_dropdown_search_mode(self, dropdown: Gtk.DropDown) -> None:
        """
        Set search mode in Gtk.Dropdown
        """

        if not isinstance(dropdown, Gtk.DropDown):
            return

        pro_ext = Gtk.PropertyExpression.new(Gtk.StringObject, None, "string")

        dropdown.set_enable_search(True)
        dropdown.set_search_match_mode(Gtk.StringFilterMatchMode.PREFIX)

        dropdown.set_expression(pro_ext)
