# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from utilities.i18n import _
from css.explorer_css import Css_explorer_manager
from controls.actions import Actions
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Pango, GObject  # noqa: E402


class Shortcuts(Gtk.Box):

    def __init__(self, win: Gtk.ApplicationWindow):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.win = win
        self.css_manager = Css_explorer_manager(self.win)
        self.action = Actions()
        self.list_shortcuts_exp_1 = (
            self.win.explorer_1.shortcuts.list_shortcuts
        )
        self.list_shortcuts_exp_2 = (
            self.win.explorer_2.shortcuts.list_shortcuts
        )
        self.actual_character_second_key = ""

        # Configure margin Box
        self.set_margin_top(20)
        self.set_margin_end(20)
        self.set_margin_bottom(20)
        self.set_margin_start(20)

        columnview = Gtk.ColumnView.new()
        from entity.shortcut import Shortcut

        attr_list = Shortcut.__dict__["__static_attributes__"]

        for property_name in attr_list:

            if property_name == "explorer" or property_name == "method":
                continue

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self.setup, property_name)
            factory.connect("bind", self.bind, property_name)

            column_header_title = ""

            if property_name == "description":
                column_header_title = _("Descripción de la acción")
            if property_name == "first_key":
                column_header_title = _("Primera tecla")
            if property_name == "second_key":
                column_header_title = _("Segunda tecla")

            column = Gtk.ColumnViewColumn.new(column_header_title, factory)

            column.set_expand(True)
            column.set_resizable(True)

            columnview.append_column(column)

        scroll_1 = Gtk.ScrolledWindow()
        scroll_1.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_1.set_child(columnview)
        scroll_1.set_hexpand(True)
        scroll_1.set_vexpand(True)
        self.append(scroll_1)

        self.store = Gio.ListStore.new(Shortcut)

        for content in self.list_shortcuts_exp_1:
            shotcute_info = Shortcut(
                content.explorer,
                content.first_key,
                content.second_key,
                content.method,
                content.description,
            )
            self.store.append(shotcute_info)

        self.sorter = Gtk.ColumnView.get_sorter(columnview)
        self.sort_model = Gtk.SortListModel.new(self.store, self.sorter)
        self.selection = Gtk.NoSelection.new(self.sort_model)
        columnview.set_model(self.selection)

    def setup(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        if property_name == "description" or property_name == "first_key":
            label = Gtk.Label(xalign=0)
            label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        else:
            label = Gtk.EditableLabel(xalign=0)
            label.set_alignment(0.5)

        cell.set_child(label)

    def bind(
        self,
        signal: Gtk.SignalListItemFactory,
        cell: Gtk.ColumnViewCell,
        property_name: str,
    ) -> None:
        item = cell.get_item()
        if item:
            output_column = cell.get_child()
            value = item.get_property(property_name)
            output_column.set_text(str(value))
            if isinstance(output_column, Gtk.EditableLabel):

                # focus_controller = Gtk.EventControllerFocus()
                # focus_controller.connect("enter", self.on_enter)
                # output_column.add_controller(focus_controller)

                handler_id = output_column.connect("changed", self.on_change)
                output_column.set_name(str(handler_id))
                output_column.connect("notify::editing", self.on_enter)

    def validate_character_second_key(self, second_key: str) -> bool:
        if len(second_key) == 0 or len(second_key) > 1:
            return False

        return True

    def on_enter(
        self, label: Gtk.EditableLabel, psec: GObject.GParamSpec
    ) -> None:
        """
        old value from editablelabel
        """
        self.actual_character_second_key = label.get_text()

    def on_change(self, label: Gtk.EditableLabel) -> None:
        """
        On change on EditableLabel validate new value
        """
        character_value = label.get_text()

        if self.actual_character_second_key == character_value:
            label.stop_editing(True)
            return

        handler_id = int(label.get_name())

        label.handler_block(handler_id)

        if not self.validate_character_second_key(character_value):
            label.set_text(self.actual_character_second_key)
        else:
            item_temp = None
            for i in self.store:
                if i.second_key == character_value:
                    label.set_text(self.actual_character_second_key)

                    self.action.show_msg_alert(
                        self.win,
                        _(
                            (
                                "La segunda tecla ya se está"
                                " empleando. Elija otra o cancele."
                            )
                        ),
                    )
                    label.handler_unblock(handler_id)
                    return
                if i.second_key == self.actual_character_second_key:
                    item_temp = i

        item_temp.second_key = character_value
        label.stop_editing(True)
        label.handler_unblock(handler_id)
