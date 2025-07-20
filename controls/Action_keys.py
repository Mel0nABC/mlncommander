import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from controls.Actions import Actions

_F5_KEY = Gdk.keyval_name(Gdk.KEY_F5)  # Copiar, hecho
_F6_KEY = Gdk.keyval_name(Gdk.KEY_F6)  # Mover
_F7_KEY = Gdk.keyval_name(Gdk.KEY_F7)  # Crear directorio
_F8_KEY = Gdk.keyval_name(Gdk.KEY_F8)  # Eliminar
_F9_KEY = Gdk.keyval_name(Gdk.KEY_F9)  # Actualizar


@staticmethod
def on_key_press(controller, keyval, keycode, state, win, actions):
    explorer_focused = win.explorer_focused
    explorer_nofocused = win.explorer_nofocused
    key_pressed_name = Gdk.keyval_name(keyval)

    if key_pressed_name == _F5_KEY:
        actions.on_copy(explorer_focused, explorer_nofocused, win)
        return True

    if key_pressed_name == _F6_KEY:
        actions.on_move(explorer_focused, explorer_nofocused)
        return True

    if key_pressed_name == _F7_KEY:
        actions.on_create_dir(explorer_focused, explorer_nofocused, win)
        return True

    if key_pressed_name == _F8_KEY:
        actions.on_delete(explorer_focused, explorer_nofocused, win)
        return True

    if key_pressed_name == _F9_KEY:
        print("F9")
        return True

    return False
