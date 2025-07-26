from views.main_window import Window
from controls.Actions import Actions
import sys, gi, os, time, asyncio
from pathlib import Path

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib

import gbulb

gbulb.install()  # Esto integra asyncio con GTK


class App(Gtk.Application):
    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = Actions()
        self.win = Window(self, action)
        action.set_parent(self.win)
        self.win.present()

    def get_application(self):
        return self.win


app = App()
app.run()
# import gi
# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk, Gio, GObject

# class FileItem(GObject.GObject):
#     """Un objeto de ejemplo con múltiples propiedades"""
#     name = GObject.Property(type=str)
#     type = GObject.Property(type=str)
#     size = GObject.Property(type=str)

#     def __init__(self, name, type_, size):
#         super().__init__()
#         self.name = name
#         self.type = type_
#         self.size = size

# class MyWindow(Gtk.ApplicationWindow):
#     def __init__(self, app):
#         super().__init__(application=app)
#         self.set_title("ColumnView con varias columnas")
#         self.set_default_size(700, 400)

#         # Creamos un ListStore con FileItems
#         store = Gio.ListStore.new(FileItem)
#         store.append(FileItem("archivo1.txt", "Texto", "15 KB"))
#         store.append(FileItem("foto.jpg", "Imagen", "2.1 MB"))
#         store.append(FileItem("video.mp4", "Video", "512 MB"))
#         store.append(FileItem("presentacion.pptx", "Presentación", "4.5 MB"))
#         store.append(FileItem("documento.pdf", "PDF", "890 KB"))

#         # MultiSelection sobre el modelo
#         self.selection = Gtk.MultiSelection.new(store)

#         # Crear el ColumnView
#         self.column_view = Gtk.ColumnView.new(self.selection)

#         # Agregar columnas
#         self.column_view.append_column(
#             self.create_column("Nombre", lambda item: item.name)
#         )
#         self.column_view.append_column(
#             self.create_column("Tipo", lambda item: item.type)
#         )
#         self.column_view.append_column(
#             self.create_column("Tamaño", lambda item: item.size)
#         )

#         self.set_child(self.column_view)

#     def create_column(self, title, get_value_func):
#         """Crea una columna con una fábrica que usa `get_value_func`"""
#         factory = Gtk.SignalListItemFactory.new()

#         def setup(factory, list_item):
#             label = Gtk.Label(xalign=0)
#             list_item.set_child(label)

#         def bind(factory, list_item):
#             item = list_item.get_item()
#             label = list_item.get_child()
#             label.set_text(get_value_func(item))

#         factory.connect("setup", setup)
#         factory.connect("bind", bind)

#         column = Gtk.ColumnViewColumn(title=title, factory=factory)
#         column.set_expand(True)
#         column.set_resizable(True)
#         return column

# class MyApp(Gtk.Application):
#     def __init__(self):
#         super().__init__(application_id="com.example.ColumnViewMulti")

#     def do_activate(self):
#         win = MyWindow(self)
#         win.present()

# app = MyApp()
# app.run()
