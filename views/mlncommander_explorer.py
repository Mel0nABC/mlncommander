# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from views.pop_up_windows.contextual_menu import ContextBox
from utilities.file_manager import File_manager
from utilities.log_manager import LogManager
from icons.icon_manager import IconManager
from utilities.access_control import AccessControl
from controls.actions import Actions
from utilities.my_watchdog import My_watchdog
from pathlib import Path
import shutil
import threading
import time
import os
import gi
from gi.repository import Gtk, Gdk, GLib, GObject, Pango

gi.require_version("Gtk", "4.0")


class Explorer(Gtk.ColumnView):
    def __init__(
        self,
        name: str,
        win: Gtk.ApplicationWindow,
        initial_path: Path,
        APP_USER_PATH: Path,
        add_fav_btn,
    ):
        super().__init__()
        self.win = win
        self.APP_USER_PATH = APP_USER_PATH
        self.name = name
        self.focused = False
        self.actual_path = Path(initial_path)
        self.actual_path_old = None
        self.entry_box = None
        self.my_watchdog = None
        self.log_manager = LogManager(self.win)
        self.action = Actions()
        self.selection = None
        self.n_row = 0
        self.path_history = {}
        self.search_str = ""
        self.thread_reset_str = threading.Thread(target=self.str_search_start)
        self.count_rst_int = 0
        self.COUNT_RST_TIME = 5000
        self.search_str_entry = None
        self.store = None
        self.img_box = None
        self.click_handler = 0
        self.background_list = self.get_last_child()
        self.handler_id_connect = 0
        self.window = None
        self.flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )
        self.access_control = AccessControl()
        self.fav_path_list = []
        self.fav_path_btn_list = []
        type_list = [
            "type_str",
            "name",
            "size",
            "date_created_str",
            "permissions",
        ]
        self.icon_manager = IconManager(win)
        self.label_gesture_list = {}
        self.row_gesture_right_list = {}
        self.add_fav_btn = add_fav_btn

        for property_name in type_list:

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)

            def customSort(a, b, *user_data):

                attr = user_data[0]

                val_a = getattr(a, attr)
                val_b = getattr(b, attr)

                if a.name == "..":
                    return -1

                if b.name == "..":
                    return 0

                if a.type == "DIR" and b.type != "DIR":
                    return -1
                if a.type != "DIR" and b.type == "DIR":
                    return 0

                return (val_a > val_b) - (val_a < val_b)

            column_header_title = ""
            customSortType = ""

            if property_name == "type_str":
                column_header_title = _("TIPO")
            if property_name == "name":
                column_header_title = _("NOMBRE")
                customSortType = "name"
            if property_name == "size":
                column_header_title = _("TAMAÑO")
                customSortType = "size_number"
            if property_name == "date_created_str":
                column_header_title = _("FECHA CREACIÓN")
                customSortType = "date_created_float"
            if property_name == "permissions":
                column_header_title = _("PERMISOS")
                customSortType = "permissions"
            sorter = None
            if customSortType:
                sorter = Gtk.CustomSorter.new(customSort, customSortType)

            column = Gtk.ColumnViewColumn.new(column_header_title, factory)

            column.set_sorter(sorter)

            # Column visual configuration

            if property_name == "type_str":
                column.set_expand(False)
                column.set_resizable(False)
            else:
                column.set_expand(True)
                column.set_resizable(True)

            self.append_column(column)

        # Header text configure, with al_SeveR @Chete

        first_row = self.get_first_child()
        list_list_model = first_row.observe_children()

        for column_title in list_list_model:
            box = column_title.get_first_child()
            box.set_halign(Gtk.Align.CENTER)

        # Configure Gtk.ColumnView

        self.set_show_column_separators(True)
        self.set_can_focus(True)
        self.set_focusable(True)
        self.set_vexpand(True)
        self.set_hexpand(True)
        # self.set_enable_rubberband(True)  # Mouse selection

        self.activate_drop_source()

        # Load css

        if self.name == "explorer_1":
            class_name = "explorer_background_left"
        else:
            class_name = "explorer_background_right"

        self.background_list.get_style_context().add_class(class_name)
        self.get_style_context().add_class("column_view_borders")

        self.get_style_context().add_class("font-color")

        # Focus event
        self.focus_explorer = Gtk.EventControllerFocus()
        self.focus_explorer.connect(
            "enter",
            lambda controller: self.set_explorer_focus(),
        )
        self.add_controller(self.focus_explorer)

        # Activate focus in explorer
        gesture_explorer_left = Gtk.GestureClick()
        gesture_explorer_left.set_button(1)
        self.gesture_click_int = gesture_explorer_left.connect(
            "pressed", self.set_explorer_focus
        )

        self.add_controller(gesture_explorer_left)

        self.activate_drag_source(self)

        # Activate watchdog on startup
        if self.win.config.SWITCH_WATCHDOG_STATUS:
            self.start_watchdog(self.actual_path, self)

        self.activate_gesture_click_label_right_click(None, self)

    def setup(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        """
        Configure type columnview Cell
        """

        def setup_when_idle():
            """
            Depent of type, set Gtk.Image for icons or Gtk.Label for text
            """
            main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            if property_name == "type_str":
                img = Gtk.Image()
                main_box.append(img)
            else:

                label = Gtk.Label(xalign=0)
                label.set_margin_top(0)
                main_box.append(label)

            cell.set_child(main_box)
            gesture_int, gesture = self.activate_gesture_click_label(
                cell, main_box
            )
            self.label_gesture_list[gesture_int] = gesture

            gesture_int_right, gesture_right = (
                self.activate_gesture_click_label_right_click(cell, main_box)
            )
            self.row_gesture_right_list[gesture_int_right] = gesture_right

        setup_when_idle()

    def activate_gesture_click_label(
        self, cell: Gtk.ColumnViewCell, widget: Gtk.Widget
    ) -> dict:
        """
        Active gesture click on labels from columnview
        """

        gesture_row_left = Gtk.GestureClick()
        gesture_row_left.set_button(1)
        gesture_int = gesture_row_left.connect(
            "pressed", self.set_focus_pressed, cell
        )
        widget.add_controller(gesture_row_left)

        return gesture_int, gesture_row_left

    def activate_gesture_click_label_right_click(
        self, cell: Gtk.ColumnViewCell, widget: Gtk.Widget
    ) -> dict:
        """
        Active gesture click on labels from columnview
        """
        gesture_row_right = Gtk.GestureClick()
        gesture_row_right.set_button(3)
        gesture_int_right = gesture_row_right.connect(
            "pressed", self.select_gesture_right_click, cell, widget
        )

        widget.add_controller(gesture_row_right)

        return gesture_int_right, gesture_row_right

    def set_focus_pressed(
        self,
        obj: Gtk.GestureClick,
        n_press: int,
        x: float,
        y: float,
        cell: Gtk.ColumnViewCell,
    ) -> None:
        selected_items = self.get_selected_items_from_explorer()[1]
        list_size = len(selected_items)
        if list_size <= 1:
            self.scroll_to(
                cell.get_position(), None, Gtk.ListScrollFlags.SELECT
            )

    def stop_focus_pressed(self) -> None:
        """
        Stop all connects on labels when push ctrl left or shift left
        """
        for key, gesture in self.label_gesture_list.items():
            gesture.disconnect(key)

    def bind(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        def bind_when_idle():
            """
            Set value for columnview cells
            """
            item = cell.get_item()
            if item:
                main_box = cell.get_child()
                value = item.get_property(property_name)
                if property_name == "type_str":
                    if item.type == "DIR":
                        pintable = self.icon_manager.get_folder_icon(
                            item.path_file
                        )
                    elif item.type == "FILE":
                        path = item.path_file
                        pintable = self.icon_manager.get_icon_for_file(path)
                    else:
                        pintable = self.icon_manager.get_back_icon()

                    image = main_box.get_first_child()
                    image.set_hexpand(True)
                    image.set_from_paintable(pintable)
                else:
                    label = main_box.get_first_child()
                    label.set_text(str(value))
                    label.set_hexpand(True)
                    label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        GLib.idle_add(bind_when_idle)

    def set_explorer_focus(
        self,
        obj: Gtk.GestureClick = None,
        n_press: int = None,
        x: float = None,
        y: float = None,
        win: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Bring focus to the browser when clicking
        anywhere in it. Terminates the search engine if enabled.
        """
        # Validation for detect is multiple
        # selection, for drag multiple selection
        selected = self.get_selected_items_from_explorer()[1]
        if len(selected) > 1:
            return

        if self.count_rst_int > 0:
            self.count_rst_int = self.COUNT_RST_TIME
        else:
            self.action.set_explorer_to_focused(self, self.win)

    def load_data(self, path: Path) -> None:
        """
        Load information from the current directory
        """
        if self.selection:
            self.selection.unselect_all()
        self.store = File_manager().get_path_list(path)

        if self.actual_path != path:
            self.start_watchdog(path, self)

        self.actual_path = path
        if self.name == "explorer_1":
            self.win.path_bar_1.actual_path_temp = self.actual_path
        else:
            self.win.path_bar_2.actual_path_temp = self.actual_path

        self.entry_box.change_entry_text(str(path))

        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(self.store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)

    def start_watchdog(self, path: Path, explorer: "Explorer") -> None:
        """
        Create another watchdog with other path
        """
        self.stop_watchdog()
        self.my_watchdog = My_watchdog(
            self.win, str(path), self.APP_USER_PATH, explorer
        )
        self.watchdog_thread = threading.Thread(target=self.my_watchdog.start)
        self.watchdog_thread.start()

    def stop_watchdog(self) -> None:
        if self.my_watchdog:
            self.my_watchdog.stop()

    def load_new_path(self, path: Path) -> None:
        """
        Load data and display the contents
        of the current directory in the browser
        """
        # Management to save the row number when advancing a directory

        if not self.access_control.validate_src_read(path, self.win):
            return

        self.load_data(path)

        for k in list(self.path_history.keys()):
            if k.is_relative_to(path):
                if k != path:
                    del self.path_history[k]
                    continue

        if path not in self.path_history:
            self.path_history[path] = 0

        GLib.idle_add(
            self.scroll_to, self.path_history[path], None, self.flags
        )

        # We reconnect if it was disconnected when entering new folder

        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )

        if self.count_rst_int > 0:
            self.stop_background_search()
            self.stop_search_mode()

        self.set_on_path_fav_button()

    def on_item_change(
        self,
        obj: Gtk.MultiSelection = None,
        n_press: int = None,
        x: int = None,
        win: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Selecting another row in a browser changes
        the value of the self.path_history variable.
        Update bottom information, selected files and size
        """

        selected = self.get_selected_items_from_explorer()
        selected_items = list(selected[1])
        selected_size = len(selected_items)
        if selected_size == 1:
            self.n_row = selected[0]

        self.update_info_explorer(selected_items, selected_size, win)

        if self.win.config.SWITCH_IMG_STATUS:
            if len(list(selected_items)) <= 1:
                self.open_img_preview(selected_items)
        else:
            self.disable_img_box()

        self.path_history[self.actual_path] = self.n_row

    def update_info_explorer(
        self,
        selected_items: list,
        selected_size: int,
        win: Gtk.ApplicationWindow,
    ) -> None:
        store = self.store
        if not store:
            return

        items_list_size = len(list(store)) - 1

        total_size_items = 0
        for item in selected_items:
            if not item.is_dir():
                if not item.is_symlink():
                    if item.exists():
                        total_size_items += item.stat().st_size

        total_size_items_reduced = File_manager().get_size_and_unit(
            total_size_items
        )

        selecteds = _("Seleccionados")
        of = _("de")
        info_selected_files = (
            f"{selected_size} {of} {items_list_size} "
            f"{selecteds}, {total_size_items_reduced}"
        )

        if self.name == "explorer_1":
            win.label_left_selected_files.set_text(info_selected_files)

        if self.name == "explorer_2":
            win.label_right_selected_files.set_text(info_selected_files)

    def get_selected_items_from_explorer(self) -> list:
        """
        Gets the selection list of an explorer
        """
        selected_items = []
        item = None
        index_return = 0
        for index in range(self.selection.get_n_items()):
            item = self.selection.get_item(index).path_file
            if self.selection.is_selected(index):
                item = self.selection.get_item(index).path_file
                if not str(item) == "..":
                    index_return = index
                    selected_items.append(item)

        return index_return, selected_items

    def set_str_search(self, search_word: str) -> str:
        """
        The search word is changed by
        adding characters and the timer is reset.
        """
        self.search_str = search_word

        if not self.thread_reset_str.is_alive():
            self.thread_reset_str = threading.Thread(
                target=self.str_search_start
            )
            self.thread_reset_str.start()
        self.count_rst_int = 0
        self.search_str_entry.set_text(self.search_str)
        return self.search_str

    def set_str_search_backspace(self, text: str) -> None:
        """
        The search word is changed by deleting
        characters and resetting the timer.
        """
        self.count_rst_int = 0
        self.search_str = text
        self.search_str_entry.set_text(self.search_str)

    def str_search_start(self) -> None:
        """
        Initialize proccess to search word in explorer list
        """
        self.set_background_search()

        while self.count_rst_int < self.COUNT_RST_TIME:
            time.sleep(0.001)
            self.count_rst_int += 1
            if not self.focused:
                self.stop_search_mode()
        self.search_str = ""
        self.search_str_entry.set_text("")
        self.count_rst_int = 0
        GLib.idle_add(self.load_new_path, self.actual_path)
        self.stop_background_search()

    def set_background_search(self) -> None:
        """
        Search colors are activated
        """
        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

        self.handler_id_connect = self.selection.connect(
            "selection-changed", self.reset_count_rst_int
        )

        self.get_style_context().remove_class("font-color")
        self.get_style_context().add_class("background_search")

        self.scroll_to(0, None, self.flags)

    def stop_background_search(self):
        """
        Search colors are desactivated
        """
        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )

        self.get_style_context().remove_class("background_search")
        self.get_style_context().add_class("font-color")

    def reset_count_rst_int(
        self,
        obj: Gtk.MultiSelection = None,
        n_press: int = None,
        x: int = None,
    ) -> None:
        """
        Restablecer la temporización al escribir y seleccionar otra fila
        """
        self.count_rst_int = 0

    def stop_search_mode(self) -> None:
        """
        Finish str_search_start(self) while loop
        """
        self.count_rst_int = self.COUNT_RST_TIME

    def activate_drag_source(self, item: Gtk.Widget) -> None:
        """
        Prepare drag method
        """
        self.drag_source = Gtk.DragSource.new()
        self.drag_source.set_actions(Gdk.DragAction.COPY)
        self.drag_source.connect("prepare", self.on_drag_prepare)
        self.drag_source.connect("drag-begin", self.on_drag_begin)
        item.add_controller(self.drag_source)

    def on_drag_prepare(
        self, source: Gtk.DragSource, x: float, y: float
    ) -> Gdk.ContentProvider:
        """
        How the file is returned
        """
        widget = source.get_widget()
        selected_items = widget.get_selected_items_from_explorer()[1]
        uris_text = "\r\n".join(p.as_uri() for p in selected_items) + "\r\n"

        return Gdk.ContentProvider.new_for_bytes(
            "text/uri-list", GLib.Bytes.new(uris_text.encode("utf-8"))
        )

    def on_drag_begin(self, source: Gtk.DragSource, x: float):
        source.set_icon(self.icon_manager.get_drag_and_drop_icon(), -15, -15)

    def activate_drop_source(self) -> None:
        """
        Prepare drop method
        """
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect("drop", self.on_drop_files)
        self.add_controller(drop_target)

    def on_drop_files(
        self, target: Gtk.DropTarget, value: Gdk.FileList, x: float, y: float
    ) -> bool:
        """
        filter type of source to download url or file path
        """
        files = value.get_files()

        if GObject.type_name(files[0]) == "GLocalFile":
            try:
                self.drop_from_local_file(value)
            except Exception as e:

                self.action.show_msg_alert(
                    self.win,
                    (
                        _(
                            "Ha ocurrido un problema"
                            f" al intentar copiar el archivo: \n\n{e}"
                        )
                    ),
                )

        elif GObject.type_name(files[0]) == "GDaemonFile":
            try:
                self.drop_from_url(files[0])
            except Exception:
                self.action.show_msg_alert(
                    self.win,
                    (
                        _(
                            "Puede que tenga que avanzar más en"
                            " la url para poder descargar este fichero"
                        )
                    ),
                )

    def drop_from_url(self, value: Gdk.FileList) -> None:
        import urllib.request

        url = value.get_uri()
        file_name = os.path.basename(url)
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as resp:
            headers = resp.headers
            content_disp = headers.get("Content-Disposition")
            file_size = int(headers.get("Content-Length"))
            # file_type = headers.get("Content-Type")
            if content_disp and "filename=" in content_disp:
                file_name = content_disp.split("filename=")[1].strip('"')
            else:
                # Usar último segmento de la URL
                from urllib.parse import urlparse

                path = urlparse(resp.geturl()).path
                file_name = path.split("/")[-1]

        dst_file = Path(f"{self.actual_path}/{file_name}")
        dst_dir = dst_file.parent

        if not file_name:
            self.action.show_msg_alert(
                self.win, _("La url no llega a un archivo")
            )
            return

        if dst_file.exists():
            self.action.show_msg_alert(
                self.win,
                _("El fichero que intenta descarga ya existe"),
            )
            return

        dst_free_size = shutil.disk_usage(dst_dir).free

        if dst_free_size < file_size:
            self.action.show_msg_alert(
                self.win,
                _("No tiene espacio suficiente para descargar este fichero"),
            )
            return

        urllib.request.urlretrieve(url, dst_file)

        if dst_file.exists():
            self.load_new_path(dst_dir)

    def drop_from_local_file(self, value: Gdk.FileList) -> None:
        from utilities.my_copy_or_move import MyCopyMove

        files = value.get_files()
        selected_items = []

        for file in files:
            selected_items.append(Path(file.get_path()))

        src_info = Path(files[0].get_path())
        src_dir = Path(src_info.parent.as_posix())

        explorer_dst = self
        explorer_src = self.win.get_other_explorer_with_name(self.name)
        old_src_path = explorer_src.actual_path
        explorer_src.load_new_path(src_dir)
        mycopymove = MyCopyMove()
        mycopymove.on_copy_or_move(
            explorer_src,
            explorer_dst,
            selected_items,
            self.win,
            "copiar",
            False,
        )

        GLib.idle_add(explorer_src.load_new_path, old_src_path)

    def open_img_preview(self, selected_items: list) -> None:
        """
        When show preview image is True,
        insert Gtk.Picture in other explorer
        """

        # Set explorer scroll min size
        self.win.scroll_1.set_size_request(1, self.get_allocated_height() / 2)
        self.win.scroll_2.set_size_request(1, self.get_allocated_height() / 2)

        if not selected_items:
            self.disable_img_box()
            return

        path = selected_items[0]

        if path.is_dir() or not selected_items:
            self.disable_img_box()
            return

        if not self.filter_image_type(path.suffix):
            self.disable_img_box()
            return

        if self.img_box:
            self.vert_screen_preview.remove(self.img_box)
            self.img_box = None

        if not self.img_box:

            self.img_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.img_box.get_style_context().add_class("to_down_explorer")
            self.img_box.set_vexpand(True)

            self.lbl_info = Gtk.Label.new()
            self.lbl_info.set_margin_top(10)
            self.lbl_info.set_hexpand(True)

            # Set box margins
            if self.name == "explorer_1":
                self.vert_screen_preview = self.win.vertical_screen_2
                self.img_box.set_margin_top(self.win.scroll_margin / 2)
                self.img_box.set_margin_start(self.win.scroll_margin / 2)
                self.img_box.set_margin_end(self.win.scroll_margin)
                self.img_box.get_style_context().add_class(
                    "explorer_background_left"
                )
            else:
                self.vert_screen_preview = self.win.vertical_screen_1
                self.img_box.set_margin_top(self.win.scroll_margin / 2)
                self.img_box.set_margin_start(self.win.scroll_margin)
                self.img_box.set_margin_end(self.win.scroll_margin / 2)
                self.img_box.get_style_context().add_class(
                    "explorer_background_right"
                )

        from gi.repository import GdkPixbuf

        box_width = self.win.explorer_1.get_allocated_width()

        self.img_file = GdkPixbuf.Pixbuf.new_from_file(str(path))
        img_width = self.img_file.get_width()
        img_height = self.img_file.get_height()
        img_ratio = img_width / img_height

        new_height = box_width / img_ratio

        if img_width < box_width:
            box_width = img_width
            new_height = img_height

        self.img_file = self.img_file.scale_simple(
            box_width,
            new_height,
            GdkPixbuf.InterpType.BILINEAR,
        )

        self.lbl_info.set_text(
            _(f"Resolución imagen original: {img_width} x {img_height} px")
        )

        paintable = Gdk.Texture.new_for_pixbuf(self.img_file)
        self.img_preview = Gtk.Picture.new_for_paintable(paintable)
        self.img_preview.set_vexpand(True)
        self.img_preview.set_hexpand(True)
        self.img_preview.get_style_context().add_class("image-preview")

        self.img_box.append(self.img_preview)
        self.img_box.append(self.lbl_info)

        self.vert_screen_preview.append(self.img_box)

    def disable_img_box(self):
        if self.img_box:
            self.vert_screen_preview.remove(self.img_box)
            self.img_box = None

    def filter_image_type(self, ext: str) -> bool:
        """
        Filter if ext is a image extension
        """
        ext = ext.lstrip(".")
        dictionari = self.icon_manager.load_mime_types()
        for key, value in dictionari.items():
            if "image/" in value:
                if ext == key:
                    return True

        return False

    def insert_log_line(
        self, operation: str, src_path: Path, dst_path: Path
    ) -> None:
        self.log_manager.print_status_on_log(operation, src_path, dst_path)

    def set_on_path_fav_button(self) -> None:
        for fav_btn in self.fav_path_btn_list:
            btn_path = Path(
                fav_btn.get_child().get_text().split(":")[1].strip()
            )
            if self.actual_path == btn_path:
                fav_btn.get_style_context().add_class("fav")
            else:
                fav_btn.get_style_context().remove_class("fav")

    def select_gesture_right_click(self, gesture, n_press, x, y, cell, widget):
        # Stop all events
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

        contextbox = None
        if cell:
            contextbox = self.open_file_contextual_menu(cell)
        else:
            contextbox = self.open_explorer_contextual_menu()

        rect = Gdk.Rectangle()
        rect.x = int(x)
        rect.y = int(y)
        rect.width = 1
        rect.height = 1

        popovermenu = Gtk.PopoverMenu.new_from_model(contextbox)
        popovermenu.get_style_context().add_class("contextual_menu")

        popovermenu.set_has_arrow(False)  # no show arrow
        popovermenu.set_autohide(True)
        popovermenu.set_cascade_popdown(True)

        popovermenu.set_parent(widget)
        popovermenu.set_pointing_to(rect)

        time.sleep(0.1)

        popovermenu.popup()

    def open_file_contextual_menu(self, cell) -> None:
        # Open with file clicked
        path_list = self.get_selected_items_from_explorer()[1]
        if cell:
            # Files selected
            path_list = self.get_selected_items_from_explorer()[1]

            if not self.focused:
                self.action.set_explorer_to_focused(self, self.win)
                self.scroll_to(
                    cell.get_position(), None, Gtk.ListScrollFlags.SELECT
                )
                path_list = self.get_selected_items_from_explorer()[1]
            else:
                if len(path_list) > 1:
                    path_list = self.get_selected_items_from_explorer()[1]
                else:
                    self.scroll_to(
                        cell.get_position(),
                        None,
                        Gtk.ListScrollFlags.SELECT,
                    )
                    path_list = self.get_selected_items_from_explorer()[1]

            if path_list:
                return ContextBox(
                    self.win,
                    True,
                    self,
                    path_list,
                    self,
                    self.win.get_other_explorer_with_name(self.name),
                )

    def open_explorer_contextual_menu(self) -> None:
        # Explorer menú, no files selected
        if not self.focused:
            self.action.set_explorer_to_focused(self, self.win)
        return ContextBox(
            self.win,
            False,
            self,
            None,
            self,
            self.win.get_other_explorer_with_name(self.name),
        )
