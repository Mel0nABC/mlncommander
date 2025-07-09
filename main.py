from Myapp import App

app = App()
app.run()

# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gtk, Gio, Gdk
# from gi.repository import GObject
# from controls import Actions
# from views.menu_bar import Menu_bar
# from views.header import header
# from views.explorer import Explorer


# class Persona(GObject.GObject):
#     nombre = GObject.Property(type=str)

#     def __init__(self, nombre):
#         super().__init__()
#         self.nombre = nombre

# class App(Gtk.Application):
#     def __init__(self):
#         super().__init__()
#         # action_exit = Gio.SimpleAction.new("exit", None)
#         # action_exit.connect("activate", Actions.on_exit)
#         # self.add_action(action_exit)

#     def do_activate(self):
#         win = Ventana(self)
#         win.present()

#     def get_application(self):
#         return self.win

# class Ventana(Gtk.Window):
#     def __init__(self, app):
#         super().__init__(application=app)

#         self.list = [
#             Persona("Alex"),
#             Persona("Alex2"),
#             Persona("Alex3"),
#         ]

#         liststore = Gio.ListStore.new(Persona)
#         for persona in self.list:
#             liststore.append(persona)

#         # Crear modelo ordenado (sin sorter inicial)
#         self.sorted_model = Gtk.SortListModel.new(model=liststore, sorter=None)

#         # Selector y ColumnView
#         selection = Gtk.SingleSelection.new(model=self.sorted_model)
#         column_view = Gtk.ColumnView.new(selection)

#         # Fábrica de celdas
#         factory = Gtk.SignalListItemFactory()
#         factory.connect("setup", self.setup_factory)
#         factory.connect("bind", self.bind_factory)

#         # ColumnViewColumn con título y fábrica
#         self.columna = Gtk.ColumnViewColumn(title="Nombre", factory=factory)
#         self.columna.set_sorter(Gtk.Sorter())  # Al hacer esto, el header se vuelve clickeable
#         self.columna.connect("notify::sort-order", self.on_sort_order_changed)
#         column_view.append_column(self.columna)

#         box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
#         box.append(column_view)
#         self.set_child(box)

#         print(self.columna.get_sorter())

#     def do_activate(self):
#         win = Window(self)
#         win.present()

#     def get_application(self):
#         return self.win

#     def setup_factory(self, factory, list_item):
#         label = Gtk.Label(xalign=0)
#         list_item.set_child(label)

#     def bind_factory(self, factory, list_item):
#         persona = list_item.get_item()
#         list_item.get_child().set_text(persona.nombre)

#     def on_sort_order_changed(self, column, _):
#         print("HOLA")
#         order = column.get_sorter()
#         if order == Gtk.SortType.ASCENDING:
#             sorter = Gtk.CustomSorter.new(
#                 lambda a, b, _: (a.nombre > b.nombre) - (a.nombre < b.nombre), None
#             )
#             self.sorted_model.set_sorter(sorter)

#         elif order == Gtk.SortType.DESCENDING:
#             sorter = Gtk.CustomSorter.new(
#                 lambda a, b, _: (b.nombre > a.nombre) - (b.nombre < a.nombre), None
#             )
#             self.sorted_model.set_sorter(sorter)

#         else:
#             self.sorted_model.set_sorter(None)


# app = App()
# app.run()