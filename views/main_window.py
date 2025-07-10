# gi, módulo que permite usar bibliotecas GTK en python.

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk

from controls import Actions, Action_keys
from views.menu_bar import Menu_bar
from views.header import header
from views.explorer import Explorer


class Window(Gtk.Window):

    def __init__(self, app):
        super().__init__(application=app)

        self.explorer_focused = None
        self.explorer_nofocused = None

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

        main_vertical_box.append(Menu_bar().get_new_menu_bar())

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

        # Añadimos entrys a su respectiva pantalla
        vertical_screen_1.append(vertical_entry_1)
        vertical_screen_2.append(vertical_entry_2)

        # Exploradores de archivos
        explorer_1 = Explorer(name="explorer_1")
        vertical_entry_1.set_text(explorer_1.get_actual_path())
        explorer_2 = Explorer(name="explorer_2")
        vertical_entry_2.set_text(explorer_2.get_actual_path())

        # # Añadimos exploradores de archivos a su respectiva pantalla
        self.explorer_1_column_view = explorer_1.get_column_view()
        self.explorer_2_column_view = explorer_2.get_column_view()
        self.explorer_1_column_view.set_vexpand(True)
        self.explorer_2_column_view.set_vexpand(True)

        # Para tener scroll en los  navegadores al obtener lista largas de archivos.
        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_1.set_child(self.explorer_1_column_view)

        scroll_2 = Gtk.ScrolledWindow()
        scroll_2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_2.set_child(self.explorer_2_column_view)

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
        horizontal_boton_menu.set_hexpand(True)

        btn_F5 = Gtk.Button()
        lbl_F5 = Gtk.Label(label="Copiar < F5 >")
        btn_F5.set_child(lbl_F5)
        horizontal_boton_menu.append(btn_F5)

        horizontal_boton_menu.set_halign(Gtk.Align.CENTER)

        main_vertical_box.append(horizontal_boton_menu)

        self.set_child(main_vertical_box)

        # ZONA DE SEÑALES(EVENTOS)

        # EVENTOS PARA ENTRY

        vertical_entry_1.connect(
            "activate", Actions.entry_on_enter_change_path, explorer_1
        )
        vertical_entry_2.connect(
            "activate", Actions.entry_on_enter_change_path, explorer_2
        )

        self.explorer_1_column_view.connect(
            "activate", Actions.on_doble_click, explorer_1, vertical_entry_1
        )
        self.explorer_2_column_view.connect(
            "activate", Actions.on_doble_click, explorer_2, vertical_entry_2
        )

        self.explorer_1_column_view.add_controller(
            Actions.set_explorer_focused(explorer_1, explorer_2, self)
        )
        self.explorer_2_column_view.add_controller(
            Actions.set_explorer_focused(explorer_2, explorer_1, self)
        )

        btn_F5.connect(
            "clicked",
            lambda btn: Actions.on_copy(
                btn, self.explorer_focused, self.explorer_nofocused
            ),
        )

        # Crear un EventControllerKey y conectarlo
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect(
            "key-pressed",
            Action_keys.on_key_press,
            self
        )

        self.add_controller(key_controller)
