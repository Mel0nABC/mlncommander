# gi, módulo que permite usar bibliotecas GTK en python.

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

from controls.Actions import Actions
from controls import Action_keys
from views.menu_bar import Menu_bar
from views.header import header
from views.explorer import Explorer
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.move import Move
from utilities.rename import Rename_Logic


class Window(Gtk.ApplicationWindow):

    def __init__(self, app, actions):
        super().__init__(application=app)

        self.explorer_src = None
        self.explorer_dst = None
        self.my_watchdog = None
        self.entry_margin = 6
        self.horizontal_button_list_margin = 8
        self.scroll_1_margin = 10

        # Obtenemos información de la pantalla

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        horizontal = geometry.width
        vertical = geometry.height

        self.set_default_size(horizontal / 2, vertical)
        self.set_titlebar(header().get_new_header())

        # Box, con orientación vertical y separación de 6 entre objetos
        main_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        menu_bar = Menu_bar(self)

        main_vertical_box.append(menu_bar.get_new_menu_bar())

        # Box horizontal para los exploradores, dos ventanas iguales.
        horizontal_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        horizontal_box.set_vexpand(True)

        # Pantalla con lista de archivos y directorios
        vertical_screen_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vertical_screen_1.set_hexpand(True)
        vertical_screen_1.set_vexpand(True)
        vertical_screen_2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vertical_screen_2.set_hexpand(True)
        vertical_screen_2.set_vexpand(True)

        # Campos entry, con la ruta actual o para cambiar.
        vertical_entry_1 = Gtk.Entry()
        vertical_entry_2 = Gtk.Entry()

        vertical_entry_1.set_margin_top(self.entry_margin)
        vertical_entry_1.set_margin_end(self.entry_margin / 2)
        vertical_entry_1.set_margin_bottom(self.entry_margin)
        vertical_entry_1.set_margin_start(self.entry_margin)

        vertical_entry_2.set_margin_top(self.entry_margin)
        vertical_entry_2.set_margin_end(self.entry_margin)
        vertical_entry_2.set_margin_bottom(self.entry_margin)
        vertical_entry_2.set_margin_start(self.entry_margin / 2)

        # Añadimos entrys a su respectiva pantalla
        vertical_screen_1.append(vertical_entry_1)
        vertical_screen_2.append(vertical_entry_2)

        # Exploradores de archivos
        self.explorer_1 = Explorer("explorer_1", vertical_entry_1)
        vertical_entry_1.set_text(self.explorer_1.get_actual_path())

        self.explorer_2 = Explorer("explorer_2", vertical_entry_2)
        vertical_entry_2.set_text(self.explorer_2.get_actual_path())

        # Para tener scroll en los  navegadores al obtener lista largas de archivos.
        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_1.set_child(self.explorer_1)
        scroll_1.set_margin_end(self.scroll_1_margin / 2)
        scroll_1.set_margin_bottom(self.scroll_1_margin)
        scroll_1.set_margin_start(self.scroll_1_margin)

        scroll_2 = Gtk.ScrolledWindow()
        scroll_2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_2.set_child(self.explorer_2)
        scroll_2.set_margin_end(self.scroll_1_margin)
        scroll_2.set_margin_bottom(self.scroll_1_margin)
        scroll_2.set_margin_start(self.scroll_1_margin / 2)

        vertical_screen_1.append(scroll_1)
        vertical_screen_2.append(scroll_2)

        # Añadimos pantallas verticales a la horizontal
        horizontal_box.append(vertical_screen_1)
        horizontal_box.append(vertical_screen_2)

        # Añadimos horizontal que contiene Entry y Explorer a la vertical primaria
        main_vertical_box.append(horizontal_box)

        # Añadimos box horizontal para menú inferior

        horizontal_boton_menu = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )
        horizontal_boton_menu.set_margin_top(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_end(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_bottom(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_margin_start(self.horizontal_button_list_margin)
        horizontal_boton_menu.set_hexpand(True)

        btn_F2 = Gtk.Button(label="Renombrar < F2 >")
        horizontal_boton_menu.append(btn_F2)

        btn_F5 = Gtk.Button(label="Copiar < F5 >")
        horizontal_boton_menu.append(btn_F5)

        btn_F6 = Gtk.Button(label="Mover < F6 >")
        horizontal_boton_menu.append(btn_F6)

        btn_F7 = Gtk.Button(label="Crear dir < F7 >")
        horizontal_boton_menu.append(btn_F7)

        btn_F8 = Gtk.Button(label="Eliminar < F8 >")
        horizontal_boton_menu.append(btn_F8)

        btn_F10 = Gtk.Button(label="Salir < F10 >")
        horizontal_boton_menu.append(btn_F10)

        horizontal_boton_menu.set_halign(Gtk.Align.CENTER)

        main_vertical_box.append(horizontal_boton_menu)

        self.set_child(main_vertical_box)

        # ZONA DE SEÑALES(EVENTOS)

        vertical_entry_1.connect(
            "activate", actions.entry_on_enter_change_path, self.explorer_1
        )
        vertical_entry_2.connect(
            "activate", actions.entry_on_enter_change_path, self.explorer_2
        )

        self.explorer_1.connect(
            "activate", actions.on_doble_click, self.explorer_1, vertical_entry_1
        )
        self.explorer_2.connect(
            "activate", actions.on_doble_click, self.explorer_2, vertical_entry_2
        )

        focus_explorer_1 = Gtk.EventControllerFocus()
        focus_explorer_1.connect(
            "enter",
            lambda controller: actions.set_explorer_src(
                self.explorer_1, self.explorer_2, self
            ),
        )
        self.explorer_1.add_controller(focus_explorer_1)

        focus_explorer_2 = Gtk.EventControllerFocus()
        focus_explorer_2.connect(
            "enter",
            lambda controller: actions.set_explorer_src(
                self.explorer_2, self.explorer_1, self
            ),
        )
        self.explorer_2.add_controller(focus_explorer_2)

        rename_logic = Rename_Logic()
        btn_F2.connect(
            "clicked",
            lambda btn: rename_logic.on_rename(self.explorer_src, self),
        )

        my_copy = My_copy()
        btn_F5.connect(
            "clicked",
            lambda btn: my_copy.on_copy(self.explorer_src, self.explorer_dst, self),
        )

        move = Move(self)
        btn_F6.connect(
            "clicked",
            lambda btn: move.on_move(self.explorer_src, self.explorer_dst),
        )

        create = Create()
        btn_F7.connect(
            "clicked",
            lambda btn: create.on_create_dir(self.explorer_src, self),
        )
        remove = Remove()
        btn_F8.connect(
            "clicked",
            lambda btn: remove.on_delete(self.explorer_src, self.explorer_dst, self),
        )

        btn_F10.connect(
            "clicked",
            lambda btn: self.exit(self),
        )

        # Crear un EventControllerKey y conectarlo
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", Action_keys.on_key_press, self, actions)

        self.add_controller(key_controller)

        self.connect("close-request", self.exit)

    @staticmethod
    def get_windows():
        return self

    def exit(self, win=None):
        self.close()
        mwdog1 = self.explorer_1.get_watchdog()
        mwdog2 = self.explorer_2.get_watchdog()
        mwdog1.stop()
        mwdog2.stop()
