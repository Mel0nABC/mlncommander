from utilities.i18n import _
from pathlib import Path
import shutil
import threading
import asyncio
import time
import os
import gi

from utilities.file_manager import File_manager
from entity.File_or_directory_info import File_or_directory_info
from icons.icon_manager import IconManager
from css.explorer_css import Css_explorer_manager
from utilities.access_control import AccessControl
from controls.Actions import Actions
from utilities.my_watchdog import My_watchdog
from controls import Action_keys

# from utilities.my_copy import My_copy

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib, Pango, GObject  # noqa E402


class Explorer(Gtk.ColumnView):
    def __init__(
        self,
        name: str,
        entry: Gtk.Entry,
        win: Gtk.ApplicationWindow,
        initial_path: Path,
        APP_USER_PATH: Path,
    ):
        super().__init__()
        self.APP_USER_PATH = APP_USER_PATH
        self.name = name
        self.focused = False
        self.actual_path = Path(initial_path)
        self.actual_path_old = None
        self.entry = entry
        self.my_watchdog = None
        self.action = Actions()
        self.css_manager = Css_explorer_manager(win)
        self.selection = None
        self.n_row = 0
        self.n_row_old = 0
        self.search_str = ""
        self.thread_reset_str = threading.Thread(target=self.str_search_start)
        self.count_rst_int = 0
        self.COUNT_RST_TIME = 5000
        self.search_str_entry = win.search_str_entry
        self.store = None
        self.win = win
        self.img_box = None
        self.click_handler = 0
        self.background_list = self.get_last_child()
        self.handler_id_connect = 0
        self.flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )
        self.access_control = AccessControl()
        self.EXPLORER_MIRROR_KEY = "o"
        type_list = [
            "type_str",
            "name",
            "size",
            "date_created_str",
            "permissions",
        ]
        self.icon_manager = IconManager(win)
        self.label_gesture_list = {}

        for property_name in type_list:

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)

            column_header_title = ""

            if property_name == "type_str":
                column_header_title = _("TIPO")
            if property_name == "name":
                column_header_title = _("NOMBRE")
            if property_name == "size":
                column_header_title = _("TAMAÑO")
            if property_name == "date_created_str":
                column_header_title = _("FECHA CREACIÓN")
            if property_name == "permissions":
                column_header_title = _("PERMISOS")

            column = Gtk.ColumnViewColumn.new(column_header_title, factory)

            # TODO: Center headers title

            # Create a Gtk.Expression for the property
            property_expression = Gtk.PropertyExpression.new(
                File_or_directory_info, None, property_name
            )

            sorter = Gtk.StringSorter.new(property_expression)

            # Column visual configuration

            column.set_sorter(sorter)
            column.set_expand(True)
            column.set_resizable(True)

            self.append_column(column)

        # self.get_style_context().add_class("header")

        # Configure Gtk.ColumnView
        # self.set_show_column_separators(True)
        # self.set_can_focus(True)
        # self.set_focusable(True)
        # self.set_vexpand(True)
        # self.set_hexpand(True)
        # self.set_enable_rubberband(True)  # Mouse selection

        self.activate_drop_source()

        # Load css and set classes
        self.load_css_background()

        # Focus event
        self.focus_explorer = Gtk.EventControllerFocus()
        self.focus_explorer.connect(
            "enter",
            lambda controller: self.set_explorer_focus(self.win),
        )
        self.add_controller(self.focus_explorer)

        # Activate pressed on explorer event
        gesture = Gtk.GestureClick()
        self.gesture_click_int = gesture.connect(
            "pressed", self.set_explorer_focus, self.win
        )
        self.add_controller(gesture)

        # Activate shortcut Control+C
        trigger = Gtk.ShortcutTrigger.parse_string(
            f"<Control>{self.EXPLORER_MIRROR_KEY}"
        )
        action = Gtk.CallbackAction.new(self.shortcut_mirroring_folder)
        self.shortcut = Gtk.Shortcut.new(trigger, action)
        controller = Gtk.ShortcutController.new()
        controller.add_shortcut(self.shortcut)
        self.add_controller(controller)

        self.activate_drag_source(self)

    def shortcut_mirroring_folder(self, *args) -> None:
        """
        Actions when shortcuts is utilized
        """
        # Disconnect key controller from main window
        self.win.key_controller.disconnect(self.win.key_controller_id)

        # Returns the browser that does not contain the passed name
        other_explorer = self.win.get_other_explorer_with_name(self.name)

        if not other_explorer:
            return

        selected_item = self.get_selected_items_from_explorer()[1]

        if not selected_item:
            other_explorer.load_data(self.actual_path.parent)

        if not selected_item:
            path = self.actual_path.parent
        else:
            path = selected_item[0]

        if selected_item:
            if not path.is_dir():
                path = path.parent

        other_explorer.load_new_path(path)

        GLib.idle_add(self._reeconnect_controller)

    def _reeconnect_controller(self) -> None:
        """
        After finish utilization shortcuts, reactivate key controller
        """
        self.win.key_controller_id = self.win.key_controller.connect(
            "key-pressed",
            Action_keys.on_key_press,
            self.win,
            self.win.action,
        )

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
            if property_name == "type_str":
                image = Gtk.Image()
                cell.set_child(image)
            else:
                label = Gtk.Label(xalign=0)
                label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
                label.get_style_context().add_class("explorer_text_size")
                cell.set_child(label)
                gesture_int, gesture = self.activate_gesture_click_label(
                    cell, label
                )
                self.label_gesture_list[gesture_int] = gesture

        GLib.idle_add(setup_when_idle)

    def activate_gesture_click_label(
        self, cell: Gtk.ColumnViewCell, label: Gtk.Label
    ) -> dict:
        """
        Active gesture click on labels from columnview
        """
        gesture = Gtk.GestureClick()
        gesture_int = gesture.connect("pressed", self.set_focus_pressed, cell)
        label.add_controller(gesture)
        return gesture_int, gesture

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
                output_column = cell.get_child()
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
                    output_column.set_from_paintable(pintable)
                else:
                    output_column.set_text(str(value))

                # output_column.get_style_context().add_class("font-color")

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
        self.store = File_manager.get_path_list(path)
        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(self.store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)
        self.actual_path = path
        self.entry.set_text(str(path))

    def load_new_path(self, path: Path) -> None:
        """
        Load data and display the contents
        of the current directory in the browser
        """
        # Management to save the row number when advancing a directory

        if not self.access_control.validate_src_read(path, self.win):
            return

        if self.actual_path_old:
            if not self.actual_path_old.is_relative_to(path):
                self.actual_path_old = self.actual_path
                self.n_row_old = self.n_row
        else:
            self.actual_path_old = self.actual_path

        self.load_data(path)

        # We reconnect if it was disconnected when entering
        # new folder
        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )

        lista_path = list(path.iterdir())
        if len(lista_path) == 0:
            GLib.idle_add(self.scroll_to, 0, None, self.flags)

        # Managing which list number to start a directory at
        # Whether to move forward or backward
        # You need to change the way you manage it, perhaps with a list,
        # Dictionary or similar
        if self.actual_path_old.is_relative_to(path):
            # Step back
            if self.focused:
                self.grab_focus()
                GLib.idle_add(self.scroll_to, self.n_row_old, None, self.flags)
        else:
            # Keep it up
            size = len(list(self.store))
            if size == 1:
                file = 0
            else:
                file = 1
            self.scroll_to(file, None, self.flags)

        if self.count_rst_int > 0:
            self.stop_background_search()
            self.stop_search_mode()

        GLib.idle_add(self.update_watchdog_path, self.actual_path, self)

    def on_item_change(
        self,
        obj: Gtk.MultiSelection = None,
        n_press: int = None,
        x: int = None,
        win: Gtk.ApplicationWindow = None,
    ) -> None:
        """
        Selecting another row in a browser changes
        the value of the self.n_row variable.
        Update bottom information, selected files and size
        """
        selected = self.get_selected_items_from_explorer()
        selected_items = list(selected[1])
        selected_size = len(selected_items)
        if selected_size == 1:
            self.n_row = selected[0]

        self.update_info_explorer(selected_items, selected_size, win)

        if self.win.SWITCH_IMG_STATUS:
            if len(list(selected_items)) <= 1:
                self.open_img_preview(selected_items)
        else:
            self.disable_img_box()

    def update_info_explorer(
        self,
        selected_items: list,
        selected_size: int,
        win: Gtk.ApplicationWindow,
    ) -> None:

        items_list_size = len(list(self.store)) - 1

        total_size_items = 0
        for item in selected_items:
            if not item.is_dir():
                if not item.is_symlink():
                    if item.exists():
                        total_size_items += item.stat().st_size

        temp_file_or_directory = File_or_directory_info("/")
        total_size_items_reduced = temp_file_or_directory.get_size_and_unit(
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

    def update_watchdog_path(self, path: Path, explorer: "Explorer") -> None:
        """
        The watchdog route is changed
        """
        asyncio.ensure_future(self.control_watchdog(path, explorer))

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
        self.n_row_old = self.n_row

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

        self.load_css_search()

        self.scroll_to(0, None, self.flags)

    def load_css_search(self) -> None:
        """
        Load css search
        """
        # tempòral values.

        self.css_manager.load_css_search(
            self.win.COLOR_BACKGROUND_SEARCH,
            self.win.COLOR_SEARCH_TEXT,
        )
        self.win.get_style_context().remove_class("font-color")
        self.background_list.get_style_context().add_class("background_search")

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

        self.win.get_style_context().add_class("font-color")
        self.background_list.get_style_context().remove_class(
            "background_search"
        )

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

    async def control_watchdog(self, path: Path, explorer: "Explorer") -> None:
        """
        Create another watchdog with other path
        """
        if self.my_watchdog:
            self.my_watchdog.stop()
        self.my_watchdog = My_watchdog(str(path), self.APP_USER_PATH, explorer)
        self.watchdog_thread = threading.Thread(target=self.my_watchdog.start)
        self.watchdog_thread.start()

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
            except Exception:
                self.action.show_msg_alert(
                    self.win,
                    (
                        _(
                            "Ha ocurrido un problema"
                            " al intentar copiar el archivo"
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
        from utilities.my_copy import My_copy

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
        my_copy = My_copy()
        my_copy.on_copy(explorer_src, explorer_dst, selected_items, self.win)

        GLib.idle_add(explorer_src.load_new_path, old_src_path)

    def open_img_preview(self, selected_items: list) -> None:
        """
        When show preview image is True,
        insert Gtk.Imgage in other explorer
        """
        if not selected_items:
            self.disable_img_box()
            return

        path = selected_items[0]

        if self.name == "explorer_1":
            self.vert_screen_preview = self.win.vertical_screen_2
        else:
            self.vert_screen_preview = self.win.vertical_screen_1

        if path.is_dir() or not selected_items:
            self.disable_img_box()
            return

        if not self.filter_image_type(path.suffix):
            self.disable_img_box()
            return

        if not self.img_box:
            self.img_preview = Gtk.Image.new()
            self.img_preview.set_size_request(-1, self.win.vertical / 2)

            self.img_preview.set_hexpand(True)
            self.img_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=6
            )

            self.img_box.append(self.img_preview)
            self.vert_screen_preview.append(self.img_box)

        self.img_preview.set_from_file(str(path))

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

    def load_css_background(self) -> None:
        """
        Load background explorers color
        """
        self.css_manager.load_css_explorer_background(
            self.win.COLOR_EXPLORER_LEFT, self.win.COLOR_EXPLORER_RIGHT
        )

        if self.name == "explorer_1":
            class_name = "explorer_background_left"
        else:
            class_name = "explorer_background_right"

        self.background_list.get_style_context().add_class(class_name)
        self.get_style_context().add_class("column_view_borders")
