# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk  # noqa E402


class ContextMenu(Gtk.Window):

    def __init__(
        self,
        main_window: Gtk.ApplicationWindow,
        x: float,
        y: float,
    ):
        super().__init__()

        # main_window = self.get_root()
        width = main_window.get_allocation().width
        height = main_window.get_allocation().height

        # Menu container, set transparent on css
        self.get_style_context().add_class("contextual_menu")
        self.set_size_request(width, height)
        self.set_transient_for(main_window)
        self.set_decorated(False)
        self.set_can_focus(True)
        self.set_focusable(True)

        # Menu visible, container
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.get_style_context().add_class("contextual_content")

        # Contextual menu content
        clicked_point = Gtk.Label.new("COSAS DEL MENU")

        box.append(clicked_point)
        for i in range(10):

            def btn_action(button):
                print("HOLA BOTON:")

            btn = Gtk.Button.new_with_label(f"BOTON - {i}")
            btn.connect("clicked", btn_action)
            box.append(btn)

        # To visibility menu container (box) and set en x,y position
        frame = Gtk.Frame.new()
        frame.set_child(box)

        # For add widgete on x,y position
        fixed = Gtk.Fixed()
        fixed.put(frame, x - 7, y - 7)

        self.set_child(fixed)

        self.present()

        close_contextual_menu = Gtk.GestureClick()
        close_contextual_menu.set_button(0)
        close_contextual_menu.connect("released", self.close_contextual_click)

        self.add_controller(close_contextual_menu)

        # Event controller to control keys
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(key_controller)

        # Focus event
        self.focus_event = Gtk.EventControllerFocus()
        self.focus_event.connect("leave", self.lost_focus)
        self.add_controller(self.focus_event)

    def close_contextual_click(
        self,
        gesture,
        n_press,
        x,
        y,
    ) -> None:
        self.destroy()

    def on_key_press(
        self,
        controller: Gtk.EventControllerKey,
        keyval: int,
        keycode: int,
        state: Gdk.ModifierType,
    ) -> None:
        """
        Manages the keys pressed to close context menu
        """
        self.destroy()

    def lost_focus(self, event: Gtk.EventControllerFocus) -> None:
        """
        Lost focus, close contextual menu
        """
        self.destroy()
