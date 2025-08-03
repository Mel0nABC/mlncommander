import gi, threading

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GObject, GLib
from utilities.file_manager import File_manager
from controls.Actions import Actions
from pathlib import Path
from controls import Action_keys
import os, asyncio, time
from entity.File_or_directory_info import File_or_directory_info
from utilities.my_watchdog import My_watchdog
from icons.icon_manager import IconManager


class Explorer(Gtk.ColumnView):
    def __init__(self, name, entry, win, initial_path):
        super().__init__()

        self.name = name
        self.focused = False
        self.actual_path = Path(initial_path)
        self.actual_path_old = None
        self.entry = entry
        self.my_watchdog = None
        self.action = Actions()
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
        self.click_handler = 0
        self.background_list = self.get_last_child()
        self.handler_id_connect = 0
        self.flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )

        type_list = [
            "type",
            "name",
            "size",
            "date_created_str",
            "permissions",
        ]
        self.icon_manager = IconManager(win)

        for property_name in type_list:

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)
            column = Gtk.ColumnViewColumn.new(str.upper(property_name), factory)

            # Create a Gtk.Expression for the property

            if property_name == "type":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "type"
                )
            elif property_name == "name":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "name"
                )
            elif property_name == "size":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "size"
                )
            elif property_name == "date_created_str":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "date_created_str"
                )
            elif property_name == "permissions":
                property_expression = Gtk.PropertyExpression.new(
                    File_or_directory_info, None, "permissions"
                )

            sorter = Gtk.StringSorter.new(property_expression)

            column.set_sorter(sorter)
            column.set_expand(True)
            column.set_resizable(True)

            self.append_column(column)

        self.set_enable_rubberband(True)

        # CONFIGURE COLUMNVIEW
        self.set_show_column_separators(True)
        self.set_can_focus(True)
        self.set_focusable(True)
        self.set_vexpand(True)
        self.set_hexpand(False)

        self.focus_explorer = Gtk.EventControllerFocus()
        self.focus_explorer.connect(
            "enter", lambda controller: self.set_explorer_focus(self.win)
        )
        self.add_controller(self.focus_explorer)

        GLib.idle_add(self.update_watchdog_path, self.actual_path, self)

    def load_css(self):

        css = b"""
            .background-search {
                color: yellow;
                background-color: black;
                font-weight:bold;
            }
            """

        provider = Gtk.CssProvider()
        provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_display(
            self.win.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def set_explorer_focus(self, obj=None, n_press=None, x=None, y=None, win=None):

        if self.count_rst_int > 0:
            self.count_rst_int = self.COUNT_RST_TIME
        else:
            self.action.set_explorer_to_focused(self, self.win)

    def on_item_change(self, obj=None, n_press=None, x=None, y=None, win=None):
        selected = self.get_selected_items_from_explorer()
        selected_item = list(selected[1])
        selected_size = len(selected_item)
        if selected_size == 1:
            self.n_row = selected[0]

    def get_selected_items_from_explorer(self):
        """
        Obtiene la lista de selection de un explorer
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

    def load_new_path(self, path: Path):

        # Gestión para guardar el nº de fila cuando se avanza un directorio
        if self.actual_path_old:
            if not self.actual_path_old.is_relative_to(path):
                self.actual_path_old = self.actual_path
                self.n_row_old = self.n_row
        else:
            self.actual_path_old = self.actual_path

        self.load_new_data_path(path)

        # Volvemos a realizar el connect si estaba desconectado al entrar en nuevo folder
        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )

        lista_path = list(path.iterdir())
        if len(lista_path) == 0:
            GLib.idle_add(self.scroll_to, 0, None, self.flags)
            # return

        # Gestión en qué nº de lista iniciar un directorio si se avanza o retrocede
        # HAY QUE CAMBIAR LA FORMA DE GESTIONARLO, QUIZÁ CON UNA LISTA, DICCIONARIO O SIMILAR
        if self.actual_path_old.is_relative_to(path):
            # Retrocede
            self.scroll_to(self.n_row_old, None, self.flags)
        else:
            # Avanza
            size = len(list(self.store))
            if size == 1:
                file = 0
            else:
                file = 1
            self.scroll_to(file, None, self.flags)

        if self.count_rst_int > 0:
            self.stop_background_search()
            self.stop_search_mode()
        # self.update_columns()

    def load_new_data_path(self, path: Path):
        # Cargamos la data del nuevo directorio
        if self.store:
            self.remove_actual_store()
        self.store = File_manager.get_path_list(path)
        self.apply_model_changes(self.store)
        self.actual_path = path
        self.entry.set_text(str(path))
        if len(list(self.store)) > 1:
            self.n_row = 1

    def remove_actual_store(self):
        self.set_model(None)
        self.store.remove_all()

    def set_new_store(self, item_list):
        self.remove_actual_store()
        self.store = Gio.ListStore.new(File_or_directory_info)
        for item in item_list:
            self.store.append(item)
        self.apply_model_changes(self.store)

    def apply_model_changes(self, store):
        self.sorter = Gtk.ColumnView.get_sorter(self)
        self.sort_model = Gtk.SortListModel.new(store, self.sorter)
        self.selection = Gtk.MultiSelection.new(self.sort_model)
        self.set_model(self.selection)
        self.n_row = 0

    def update_watchdog_path(self, path, explorer):
        asyncio.ensure_future(self.control_watchdog(path, explorer))

    async def control_watchdog(self, path, explorer):
        if self.my_watchdog:
            self.my_watchdog.stop()
            # self.watchdog_thread.join()
        self.my_watchdog = My_watchdog(str(path), explorer)
        self.watchdog_thread = threading.Thread(target=self.my_watchdog.start)
        self.watchdog_thread.start()

    def get_watchdog(self):
        return self.my_watchdog

    def setup(self, signal, cell, property_name):
        def setup_when_idle():
            if property_name == "type":
                image = Gtk.Image()
                cell.set_child(image)
            else:
                label = Gtk.Label(xalign=0)
                cell.set_child(label)

        GLib.idle_add(setup_when_idle)

    def bind(self, signal, cell, property_name):
        def bind_when_idle():
            item = cell.get_item()
            if item:
                output_column = cell.get_child()
                value = item.get_property(property_name)
                if property_name == "type":
                    if item.type == "DIR":
                        pintable = self.icon_manager.get_folder_icon()
                    elif item.type == "FILE":
                        path = item.path_file
                        pintable = self.icon_manager.get_icon_for_file(path)
                    else:
                        pintable = self.icon_manager.get_back_icon()
                    output_column.set_from_paintable(pintable)
                else:
                    output_column.set_text(str(value))

        GLib.idle_add(bind_when_idle)

    def set_str_search(self, search_word):
        self.search_str = search_word

        if not self.thread_reset_str.is_alive():
            self.thread_reset_str = threading.Thread(target=self.str_search_start)
            self.thread_reset_str.start()
        self.count_rst_int = 0
        self.search_str_entry.set_text(self.search_str)
        return self.search_str

    def set_str_search_backspace(self, text):
        self.count_rst_int = 0
        self.search_str = text
        self.search_str_entry.set_text(self.search_str)

    def str_search_start(self):
        self.n_row_old = self.n_row
        while self.count_rst_int < self.COUNT_RST_TIME:
            time.sleep(0.001)
            self.count_rst_int += 1
            if not self.focused:
                self.stop_search_mode()
        self.search_str = ""
        self.search_str_entry.set_text("")
        self.count_rst_int = 0
        GLib.idle_add(self.load_new_data_path, self.actual_path)
        self.stop_background_search()

    def set_background_search(self):
        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.reset_count_rst_int
            )

        self.load_css()
        self.background_list.get_style_context().add_class("background-search")
        self.scroll_to(0, None, self.flags)

    def stop_background_search(self):

        if self.selection.handler_is_connected(self.handler_id_connect):
            self.selection.disconnect(self.handler_id_connect)

        if not self.selection.handler_is_connected(self.handler_id_connect):
            self.handler_id_connect = self.selection.connect(
                "selection-changed", self.on_item_change, self.win
            )
        self.background_list.get_style_context().remove_class("background-search")

    def reset_count_rst_int(self, obj=None, n_press=None, x=None, y=None):
        self.count_rst_int = 0

    def stop_search_mode(self):
        self.count_rst_int = self.COUNT_RST_TIME

    def update_columns(self):
        for column in self.get_columns():
            title = column.get_title()
            if title == "TYPE":
                column.set_fixed_width(30)
            else:
                column.set_fixed_width(150)

        return False
