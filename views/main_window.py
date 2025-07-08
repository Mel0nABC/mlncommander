# gi, módulo que permite usar bibliotecas GTK en python.

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk

from controls import Actions
from views.menu_bar import Menu_bar
from views.header import header
from views.explorer import Explorer


class Window(Gtk.Window):

    def __init__(self, app):
        super().__init__(application=app)

        # Obtenemos información de la pantalla

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        horizontal = geometry.width
        vertical = geometry.height

        self.set_default_size(horizontal / 2, vertical / 2)
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
        explorer_1 = Explorer()
        vertical_entry_1.set_text(explorer_1.get_actual_path())
        explorer_2 = Explorer()
        vertical_entry_2.set_text(explorer_2.get_actual_path())

        # # Añadimos exploradores de archivos a su respectiva pantalla
        explorer_1_column_view = explorer_1.get_column_view()
        explorer_2_column_view = explorer_2.get_column_view()
        explorer_1_column_view.set_vexpand(True)
        explorer_2_column_view.set_vexpand(True)

        # Para tener scroll en los  navegadores al obtener lista largas de archivos.
        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_1.set_child(explorer_1_column_view)

        scroll_2 = Gtk.ScrolledWindow()
        scroll_2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_2.set_child(explorer_2_column_view)

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

        for i in range(1, 10):
            btn1 = Gtk.Button()
            lbl1 = Gtk.Label(label=f"F{i}")
            btn1.set_child(lbl1)
            horizontal_boton_menu.append(btn1)

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

        explorer_1_column_view.connect(
            "activate", Actions.on_doble_click, explorer_1, vertical_entry_1
        )
        explorer_2_column_view.connect(
            "activate", Actions.on_doble_click, explorer_2, vertical_entry_2
        )
