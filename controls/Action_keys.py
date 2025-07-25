import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from controls.Actions import Actions
from utilities import create, move, remove, rename, update
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.move import Move

_F5_KEY = Gdk.keyval_name(Gdk.KEY_F5)  # Copiar, hecho
_F6_KEY = Gdk.keyval_name(Gdk.KEY_F6)  # Mover
_F7_KEY = Gdk.keyval_name(Gdk.KEY_F7)  # Crear directorio
_F8_KEY = Gdk.keyval_name(Gdk.KEY_F8)  # Eliminar
_F9_KEY = Gdk.keyval_name(Gdk.KEY_F9)  # Actualizar
_F10_KEY = Gdk.keyval_name(Gdk.KEY_F10)  # Salir


@staticmethod
def on_key_press(controller, keyval, keycode, state, win, actions):
    explorer_src = win.explorer_src
    explorer_dst = win.explorer_dst
    key_pressed_name = Gdk.keyval_name(keyval)

    if key_pressed_name == _F5_KEY:
        # Copy
        my_copy = My_copy()
        my_copy.on_copy(explorer_src, explorer_dst, win)
        return True

    if key_pressed_name == _F6_KEY:
        # Move
        move = Move(win)
        move.on_move(explorer_src, explorer_dst)
        return True

    if key_pressed_name == _F7_KEY:
        # new dir
        create = Create()
        create.on_create_dir(explorer_src, win)
        return True

    if key_pressed_name == _F8_KEY:
        # delete/remove
        remove = Remove()
        remove.on_delete(explorer_src, explorer_dst, win)
        return True

    if key_pressed_name == _F9_KEY:
        print("F9")
        return True

    if key_pressed_name == _F10_KEY:
        print("F10")
        return True

    return False
