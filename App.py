from views.main_window import Window
from controls.Actions import Actions
import sys, gi, os, time, asyncio
from pathlib import Path

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, Gio, GLib

import gbulb

gbulb.install()  # Esto integra asyncio con GTK


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.mel0n.mlncommander")

    def do_activate(self):
        action = Actions()
        self.win = Window(self, action)
        action.set_parent(self.win)
        self.win.present()
        self.win.set_explorer_initial()

    def get_application(self):
        return self.win


# print(Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())
# print(hasattr(Gtk, "PropertySorter"))
# print(Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION, Gtk.MICRO_VERSION)


app = App()
app.run()


# import random
# import string

# import gi

# gi.require_version("Gtk", "4.0")
# from gi.repository import Gio, GLib, GObject, Gtk  # noqa


# class DataObject(GObject.GObject):

#     __gtype_name__ = "DataObject"

#     text = GObject.Property(type=GObject.TYPE_STRING, default="")
#     number = GObject.Property(type=GObject.TYPE_FLOAT, default=0)
#     truefalse = GObject.Property(type=GObject.TYPE_BOOLEAN, default=False)

#     def __init__(self, text, number, truefalse=False):

#         super().__init__()

#         self.text = text
#         self.number = number
#         self.truefalse = truefalse


# class MyApp(Gtk.Application):
#     def __init__(self):
#         super().__init__(application_id="org.gtk.Example")
#         self.column_view = Gtk.ColumnView()
#         self.store = Gio.ListStore.new(DataObject)
#         self.update_timer = None

#     @staticmethod
#     def to_str(bind, from_value):
#         return str(from_value)

#     def update_data(self):
#         print("Updating data...")
#         for i, item in enumerate(self.store):
#             random_text = "".join(
#                 random.choices(string.ascii_uppercase + string.digits, k=5)
#             )
#             random_number = random.randint(5555, 9999)
#             item.text = random_text
#             item.number = random_number
#             item.truefalse = random.choice([True, False])

#         # Randomly remove 1 or more items if there are more than 5 items
#         if len(self.store) > 5:
#             remove_count = random.randint(1, len(self.store) - 5)
#             for _ in range(remove_count):
#                 remove_index = random.randint(0, len(self.store) - 1)
#                 self.store.remove(remove_index)

#         # Randomly add 1 or more items if there are less than 20 items
#         if len(self.store) < 20:
#             add_count = random.randint(1, 20 - len(self.store))
#             for _ in range(add_count):
#                 random_text = "".join(
#                     random.choices(string.ascii_uppercase + string.digits, k=5)
#                 )
#                 random_number = random.randint(5555, 9999)
#                 truefalse = random.choice([True, False])
#                 self.store.append(DataObject(random_text, random_number, truefalse))

#         sorter = self.sort_model.get_sorter()
#         sorter.changed(0)
#         return False

#     def init_columnview(self):
#         properties = [prop.name for prop in DataObject.list_properties()]
#         for x in range(10):
#             self.store.append(DataObject("entry", 0.0))

#         for i, property_name in enumerate(properties):
#             factory = Gtk.SignalListItemFactory()
#             factory.connect("setup", self.setup, property_name)
#             factory.connect("bind", self.bind, property_name)
#             column = Gtk.ColumnViewColumn.new(property_name, factory)

#             # Create a Gtk.Expression for the property
#             property_expression = Gtk.PropertyExpression.new(
#                 DataObject, None, property_name
#             )

#             # Create a Gtk.Sorter based on the property type
#             property_type = DataObject.find_property(
#                 property_name
#             ).value_type.fundamental
#             if property_type == GObject.TYPE_STRING:
#                 sorter = Gtk.StringSorter.new(property_expression)
#             elif property_type == GObject.TYPE_FLOAT:
#                 sorter = Gtk.NumericSorter.new(property_expression)
#             elif property_type == GObject.TYPE_BOOLEAN:
#                 sorter = Gtk.NumericSorter.new(property_expression)

#             # Set the sorter on the column
#             column.set_sorter(sorter)

#             self.column_view.append_column(column)

#         sorter = Gtk.ColumnView.get_sorter(self.column_view)
#         self.sort_model = Gtk.SortListModel.new(self.store, sorter)
#         self.selection = Gtk.SingleSelection.new(self.sort_model)
#         self.selection.connect("selection-changed", self.on_selection_changed)
#         self.column_view.set_model(self.selection)
#         self.update_timer = GLib.timeout_add_seconds(1, self.update_data)
#         # GLib.idle_add(self.update_data)

#     def on_selection_changed(self, selection, position, item):
#         item = selection.get_selected_item()
#         if item is not None:
#             print(f"Selected item: {item.text}, {item.number}, {item.truefalse}")
#         else:
#             print("No item selected")

#     def setup(self, widget, item, property_name):
#         def setup_when_idle():
#             obj = item.get_item()
#             property_type = obj.find_property(property_name).value_type
#             if property_type == GObject.TYPE_BOOLEAN:
#                 widget_type = Gtk.CheckButton
#             else:
#                 widget_type = Gtk.Label
#             widget = widget_type()
#             item.set_child(widget)

#         GLib.idle_add(setup_when_idle)

#     def bind(self, widget, item, property_name):
#         def bind_when_idle():
#             child = item.get_child()
#             obj = item.get_item()
#             if obj is not None:
#                 property_type = obj.find_property(property_name).value_type
#                 if property_type == GObject.TYPE_BOOLEAN:
#                     widget_property = "active"
#                     obj.bind_property(
#                         property_name,
#                         child,
#                         widget_property,
#                         GObject.BindingFlags.SYNC_CREATE,
#                     )
#                 else:
#                     widget_property = "label"
#                     obj.bind_property(
#                         property_name,
#                         child,
#                         widget_property,
#                         GObject.BindingFlags.SYNC_CREATE,
#                         self.to_str,
#                     )

#         GLib.idle_add(bind_when_idle)

#     def do_activate(self):
#         win = Gtk.ApplicationWindow(
#             application=self,
#             title="Gtk4 is Awesome !!!",
#             default_height=400,
#             default_width=400,
#         )
#         sw = Gtk.ScrolledWindow()

#         self.init_columnview()

#         sw.set_child(self.column_view)
#         win.set_child(sw)
#         win.present()


# app = MyApp()
# app.run(None)
