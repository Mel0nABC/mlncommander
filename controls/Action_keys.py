import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
from controls.Actions import Actions
from pathlib import Path
from utilities import create, move, remove, rename, update
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.rename import Rename_Logic
from utilities.move import Move

_F2_KEY = Gdk.keyval_name(Gdk.KEY_F2)  # Renombrar
_F5_KEY = Gdk.keyval_name(Gdk.KEY_F5)  # Copiar, hecho
_F6_KEY = Gdk.keyval_name(Gdk.KEY_F6)  # Mover
_F7_KEY = Gdk.keyval_name(Gdk.KEY_F7)  # Crear directorio
_F8_KEY = Gdk.keyval_name(Gdk.KEY_F8)  # Eliminar
_F9_KEY = Gdk.keyval_name(Gdk.KEY_F9)  # Actualizar
_F10_KEY = Gdk.keyval_name(Gdk.KEY_F10)  # Salir
_TAB = Gdk.keyval_name(Gdk.KEY_Tab)  # Babulador
_BACKSPACE = Gdk.keyval_name(Gdk.KEY_BackSpace)  # Borrar
row_explorer = 1


@staticmethod
def on_key_press(controller, keyval, keycode, state, win, actions):
    explorer_src = win.explorer_src
    explorer_dst = win.explorer_dst
    key_pressed_name = Gdk.keyval_name(keyval)

    # print(f"Key pressed: {key_pressed_name}, state: {state},  keyval: {keyval}")

    if key_pressed_name == _F2_KEY:
        # Copy
        rename_logic = Rename_Logic()
        rename_logic.on_rename(explorer_src, win)
        return True

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

    if key_pressed_name == _TAB:

        flags = (
            Gtk.ListScrollFlags.SELECT
            | Gtk.ListScrollFlags.NONE
            | Gtk.ListScrollFlags.FOCUS
        )

        if explorer_src.focused == True:
            # "EX 2 FOCUSED"
            n_row_dst = explorer_dst.n_row
            explorer_dst.set_can_focus(True)
            explorer_dst.focused = True
            explorer_src.focused = False
            explorer_dst.grab_focus()
            explorer_dst.scroll_to(n_row_dst, None, flags)

        else:
            # "EX 1 FOCUSED"
            n_row_src = explorer_src.n_row
            explorer_src.set_can_focus(True)
            explorer_src.focused = True
            explorer_dst.focused = False
            explorer_src.grab_focus()
            explorer_src.scroll_to(n_row_src, None, flags)

        return True

    if key_pressed_name == _BACKSPACE:
        if explorer_src.search_str_entry != "":
            text = explorer_src.search_str_entry.get_text()[:-1]
            explorer_src.set_str_search_backspace(text)
            return True
        else:
            explorer_src.load_new_path(explorer_src.actual_path)
            return True

        parent_path = explorer_src.actual_path.parent
        explorer_src.load_new_path(parent_path)
        return True

    # CONDICIONAL PARA QUE PASE EL ABCDEARIO, MINÚSCULAS Y MAYÚSCULAS
    if keyval in range(65, 90) or keyval in range(97, 122) or keyval in range(48, 58):
        search_str = explorer_src.set_str_search(key_pressed_name)
        filtered_item_list = []

        selection = explorer_src.selection
        print("#############################")
        for item in selection:
            if item != None:
                name = item.name
                # if str.startswith(str.lower(name), str.lower(search_str)):
                if str.lower(search_str) in str.lower(name):
                    print(item)
                    filtered_item_list.append(item)

        explorer_src.set_new_store(filtered_item_list)
        # if not filtered_item_list:
        #     print("NO HAY CONTENIDO EN FILTEREDS")
        #     explorer_src.load_new_path(explorer_src.actual_path)
        # else:
        #     explorer_src.set_new_store(filtered_item_list)

        return True

    return False
