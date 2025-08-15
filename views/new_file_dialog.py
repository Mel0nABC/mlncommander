from utilities.i18n import _
from controls.Actions import Actions
from pathlib import Path
import asyncio
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class NewFileDialog(Gtk.Window):
    def __init__(
        self,
        parent: Gtk.ApplicationWindow,
        src_dir: "Explorer",  # noqa: F821
        new_file: "NewFile",  # noqa: F821
    ):
        super().__init__(title=_("Crear fichero"), transient_for=parent)

        self.actions = Actions()
        self.win = parent
        self.new_file = new_file
        self.src_dir = src_dir

        vertical_box_info = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )
        vertical_box_info.set_margin_top(20)
        vertical_box_info.set_margin_start(20)

        horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6
        )

        name_label = Gtk.Label.new(_("Nombre del nuevo archivo:"))
        name_label.set_margin_top(20)
        name_label.set_halign(Gtk.Align.START)

        vertical_box_info.append(name_label)
        self.entry_file_name = Gtk.Entry()
        self.entry_file_name.connect("activate", self.get_selected_option)
        self.entry_file_name.set_hexpand(True)

        horizontal_box.append(self.entry_file_name)
        # Extension list
        extensions = [
            "*.docx",  # Office Word
            "*.odt",  # libreoffice word
            "*.xlsx",  # Office Spreadsheets
            "*.ods",  # libreoffice Spreadsheets
            "*.txt",  # Plain text / RTF
            "*.csv",  # Tabular data
        ]

        extension_list = Gtk.StringList.new(extensions)
        self.extension_drop_down = Gtk.DropDown(model=extension_list)
        self.extension_drop_down.set_selected(0)
        horizontal_box.append(self.extension_drop_down)
        horizontal_box.set_margin_end(20)

        vertical_box_info.append(horizontal_box)

        self.btn_accept = Gtk.Button(label=_("Aceptar"))
        self.btn_cancel = Gtk.Button(label=_("Cancelar"))

        self.btn_accept.connect("clicked", self.get_selected_option)
        self.btn_cancel.connect("clicked", self.exit)

        self.vertical_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6
        )

        self.vertical_box.set_margin_top(20)
        self.vertical_box.set_margin_bottom(20)
        self.vertical_box.set_margin_start(20)
        self.vertical_box.set_margin_end(20)

        self.vertical_box.append(self.btn_accept)
        self.vertical_box.append(self.btn_cancel)
        vertical_box_info.append(self.vertical_box)

        self.set_child(vertical_box_info)

        self.response_text = None
        self.future = asyncio.get_event_loop().create_future()

        self.present()

    def get_selected_option(self, botton: Gtk.Button) -> None:
        """
        On accept or press enter in entry, we confirm new name
        """
        self.response_text = self.entry_file_name.get_text()

        if not self.response_text:
            self.actions.show_msg_alert(
                self.win, "Debe indicar un nombre de un archivo."
            )
            return

        ext_name = (
            self.extension_drop_down.get_selected_item()
            .get_string()
            .lstrip("*")
        )
        file_name = f"{self.response_text}{ext_name}"

        path = Path(f"{self.src_dir.actual_path}/{file_name}")

        if path.exists():
            self.actions.show_msg_alert(self.win, _("El archivo ya existe."))
            return

        response = self.new_file.create_new_file(path)

        if not response:
            self.actions.show_msg_alert(
                self.win,
                _("Ha surgido algún problema al crear el archivo."),
            )
            return

        self.src_dir.load_new_path(self.src_dir.actual_path)

        self.destroy()

    def exit(self, botton: Gtk.Button) -> None:
        self.destroy()
