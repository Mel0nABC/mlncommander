import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from controls.Actions import Actions

_F5_KEY = Gdk.keyval_name(Gdk.KEY_F5) # Copiar, hecho
_F6_KEY = Gdk.keyval_name(Gdk.KEY_F6) # Mover
_F7_KEY = Gdk.keyval_name(Gdk.KEY_F7) # Crear directorio
_F8_KEY = Gdk.keyval_name(Gdk.KEY_F8) # Eliminar
_F9_KEY = Gdk.keyval_name(Gdk.KEY_F9) # Actualizar


@staticmethod
def on_key_press(controller, keyval, keycode, state, win):
    source = win.explorer_focused
    destination = win.explorer_nofocused
    key_pressed_name = Gdk.keyval_name(keyval)

    actions = Actions(win)

    if key_pressed_name == _F5_KEY:
        actions.on_copy(source, destination, win)
        return True

    if key_pressed_name == _F6_KEY:
        print("F6")
        return True

    if key_pressed_name == _F7_KEY:
        print("F7")
        return True

    if key_pressed_name == _F8_KEY:
        print("F8")
        return True

    if key_pressed_name == _F9_KEY:
        print("F9")
        return True

    return False
