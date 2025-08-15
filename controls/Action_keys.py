import gi
from utilities.my_copy import My_copy
from utilities.create import Create
from utilities.remove import Remove
from utilities.rename import Rename_Logic
from utilities.move import Move
from utilities.new_file import NewFile
from controls.Actions import Actions

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib  # noqa: E402

_F2_KEY = Gdk.keyval_name(Gdk.KEY_F2)  # Rename
_F3_KEY = Gdk.keyval_name(Gdk.KEY_F3)  # New file
_F5_KEY = Gdk.keyval_name(Gdk.KEY_F5)  # Copy
_F6_KEY = Gdk.keyval_name(Gdk.KEY_F6)  # Move
_F7_KEY = Gdk.keyval_name(Gdk.KEY_F7)  # Create directory
_F8_KEY = Gdk.keyval_name(Gdk.KEY_F8)  # Delete
_F9_KEY = Gdk.keyval_name(Gdk.KEY_F9)  # Update
_F10_KEY = Gdk.keyval_name(Gdk.KEY_F10)  # Exit
_TAB = Gdk.keyval_name(Gdk.KEY_Tab)  # Tabulator
_BACKSPACE = Gdk.keyval_name(Gdk.KEY_BackSpace)  # Borrar
_ESCAPE = Gdk.keyval_name(Gdk.KEY_Escape)  # Escape
_PUNTO = Gdk.keyval_name(Gdk.KEY_period)  # Punto
_DELETE = Gdk.keyval_name(Gdk.KEY_Delete)  # supr
_BACKSLASH = Gdk.keyval_name(Gdk.KEY_KP_Divide)  # /
_SHIFT_L = Gdk.keyval_name(Gdk.KEY_Shift_L)  # Left shift
_CTRL_L = Gdk.keyval_name(Gdk.KEY_Control_L)  # Left shift

# Dictionary for numeric keyboard
KP_KEYVALS = {
    "KP_0": "0",
    "KP_1": "1",
    "KP_2": "2",
    "KP_3": "3",
    "KP_4": "4",
    "KP_5": "5",
    "KP_6": "6",
    "KP_7": "7",
    "KP_8": "8",
    "KP_9": "9",
    "KP_Subtract": "-",  # hyphen on numeric keypad
    "KP_Decimal": ".",  # period on numeric keypad
}


def on_key_press(
    controller: Gtk.EventControllerKey,
    keyval: int,
    keycode: int,
    state: Gdk.ModifierType,
    win: Gtk.ApplicationWindow,
    actions: Actions,
) -> bool:
    """
    Manages the keys pressed
    """
    explorer_src = win.explorer_src
    explorer_dst = win.explorer_dst
    key_pressed_name = Gdk.keyval_name(keyval)
    flags = (
        Gtk.ListScrollFlags.SELECT
        | Gtk.ListScrollFlags.NONE
        | Gtk.ListScrollFlags.FOCUS
    )

    print(
        (
            f"Keyval: {keyval}  - keycode: {keycode}"
            f"- keypressed: {key_pressed_name}"
        )
    )

    return {
        handle_navitation_keys(
            explorer_src, explorer_dst, key_pressed_name, win, flags
        )
        or handle_file_operation(
            explorer_src, explorer_dst, win, key_pressed_name
        )
        or handle_search_keys(
            explorer_src, explorer_dst, win, key_pressed_name, keyval
        )
    }


def handle_navitation_keys(
    explorer_src: "Explorer",  # noqa: F821
    explorer_dst: "Explorer",  # noqa: F821
    key_pressed_name: str,
    win: Gtk.ApplicationWindow,
    flags: list,
) -> bool:
    """
    Manage navigation keys, change explorer focus,
    change focus to Entry path...
    """

    if key_pressed_name == _BACKSLASH:
        explorer_src.entry.grab_focus()
        return True

    if key_pressed_name == _TAB:
        if explorer_src.focused:
            # Explorer 2, focused
            n_row_dst = explorer_dst.n_row
            explorer_dst.set_can_focus(True)
            explorer_dst.grab_focus()
            explorer_dst.scroll_to(n_row_dst, None, flags)

        else:
            # Explorer 1, focused
            n_row_src = explorer_src.n_row
            explorer_src.set_can_focus(True)
            explorer_src.grab_focus()
            explorer_src.scroll_to(n_row_src, None, flags)

        return True

    if key_pressed_name == _SHIFT_L:
        explorer_src.stop_focus_pressed()
        return True

    if key_pressed_name == _CTRL_L:
        explorer_src.stop_focus_pressed()
        return True

    return False


def handle_file_operation(
    explorer_src: "Explorer",  # noqa: F821
    explorer_dst: "Explorer",  # noqa: F821
    win: Gtk.ApplicationWindow,
    key_pressed_name: str,
) -> bool:
    """
    Manage shortkeys, keyboard and GUI button actions
    """
    if key_pressed_name == _F2_KEY:
        # Copy
        rename_logic = Rename_Logic()
        rename_logic.on_rename(explorer_src, win)
        return True

    if key_pressed_name == _F3_KEY:
        # Copy
        new_file = NewFile()
        new_file.on_new_file(explorer_src, win)
        return True

    if key_pressed_name == _F5_KEY:
        # Copy
        my_copy = My_copy()
        my_copy.on_copy(explorer_src, explorer_dst, None, win)
        return True

    if key_pressed_name == _F6_KEY:
        # Move
        move = Move(win)
        move.on_move(explorer_src, explorer_dst)
        return True

    if key_pressed_name == _F7_KEY:
        # new dir
        create = Create()
        create.on_create_dir(explorer_src, explorer_dst, win)
        return True

    if key_pressed_name == _F8_KEY or key_pressed_name == _DELETE:
        # delete/remove
        remove = Remove()
        remove.on_delete(explorer_src, explorer_dst, win)
        return True

    if key_pressed_name == _F9_KEY:
        # Copy
        my_copy = My_copy()
        my_copy.on_duplicate(explorer_src, explorer_dst, win)
        return True

    if key_pressed_name == _F10_KEY:
        print("F10")
        return True

    return False


def handle_search_keys(
    explorer_src: "Explorer",  # noqa: F821
    explorer_dst: "Explorer",  # noqa: F821
    win: Gtk.ApplicationWindow,
    key_pressed_name: str,
    keyval: int,
) -> bool:
    """
    Manages the search for files or folders
    """
    if key_pressed_name == _BACKSPACE:

        # Reload store from actual dir
        explorer_src.load_data(explorer_src.actual_path)

        # File and folder name search system, character deletion
        search_word = explorer_src.search_str_entry.get_text()[:-1]

        set_search_word(search_word, explorer_src, win)

        if search_word != "":
            explorer_src.set_str_search_backspace(search_word)

            find_name_path(explorer_src, search_word, win)

            return True

        stop_search_mode(explorer_src)
        parent_path = explorer_src.actual_path.parent
        explorer_src.load_new_path(parent_path)

        return True

    # Conditional to pass the alphabet, lowercase and uppercase, add character
    if (
        keyval in range(65, 91)
        or keyval in range(97, 123)
        or keyval in range(48, 58)
        or keyval in range(65453, 65466)
        or keyval == 45
        or keyval == 46
    ):
        # File and folder name search system

        if keyval == 45:
            key_pressed_name = "-"

        if keyval == 46:
            key_pressed_name = "."

        if key_pressed_name in KP_KEYVALS:
            key_pressed_name = KP_KEYVALS[key_pressed_name]

        search_word = f"{explorer_src.search_str}{key_pressed_name}"
        find_name_path(explorer_src, search_word, win)

    if key_pressed_name == _ESCAPE:
        stop_search_mode(explorer_src)
        return True

    return False


def stop_search_mode(explorer_src: "Explorer") -> None:  # noqa: F821
    """
    End the file and folder search system
    """
    if explorer_src.count_rst_int > 0:
        explorer_src.stop_search_mode()
    explorer_src.stop_background_search()


def find_name_path(
    explorer_src: "Explorer",  # noqa: F821
    search_word: str,
    win: Gtk.ApplicationWindow,
) -> None:
    """
    Search for file and folder names containing with search_word.
    """

    explorer_src.set_str_search(search_word)

    set_search_word(search_word, explorer_src, win)

    # We load actual dir store
    store = explorer_src.store

    for index in reversed(range(len(store))):
        item = store[index]
        if item:
            name = item.name
            # Any name that does not begin with search_word is deleted from
            # the store. if not name.lower().startswith(search_word.lower())
            # and name != "..":

            # The file or directory must have the word you are searching for.
            if not search_word.lower() in name.lower() and name != "..":
                store.remove(index)

    sorter_model = explorer_src.sort_model.get_sorter()
    sorter_model.changed(0)
    # explorer_src.set_background_search()

    # When there are no results in filtering
    if len(list(store)) == 1:
        return

    GLib.idle_add(explorer_src.scroll_to, 1, None, explorer_src.flags)


def set_search_word(
    search_word: str,
    explorer_src: "Explorer",  # noqa: F821
    win: Gtk.ApplicationWindow,
) -> None:
    search_entry_text = f"Buscando: {search_word}"
    if explorer_src.name == "explorer_1":
        win.vertical_entry_1.set_text(search_entry_text)
    else:
        win.vertical_entry_2.set_text(search_entry_text)
