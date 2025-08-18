# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from views.main_window import Window
from controls.Actions import Actions
from pathlib import Path
import gbulb
import subprocess
import gettext
import gi
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


gbulb.install()  # Integrate asyncio into Gtk


# Configure gettext
APP_NAME = "mlncommander"
LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locales")

# Initialice gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
# _ = gettext.gettext


# trans = gettext.translation(
#     APP_NAME, localedir=LOCALE_DIR, languages=["en"], fallback=False
# )
# trans.install()


class App(Gtk.Application):

    def __init__(self):
        """
        Constructor
        """
        super().__init__(application_id="com.mel0n.mlncommander")

    def do_activate(self) -> None:
        """
        Initializes the application when the run() method is executed
        """
        action = Actions()
        self.window = Window(self, action)
        action.set_parent(self.window)
        self.window.present()
        self.window.set_explorer_initial()

        # self.generate_project_file_list()

    def generate_project_file_list(self):
        py_files = []
        project_path = Path(LOCALE_DIR).parent

        def iter_dir(path: Path):
            for item in path.iterdir():
                if item.is_dir():
                    if not item.name == "venv":
                        iter_dir(item)
                else:
                    if item.suffix == ".py":
                        py_files.append(str(item))

        iter_dir(project_path)

        subprocess.run(
            [
                "xgettext",
                "-o",
                f"{str(Path(LOCALE_DIR))}/lenguaje_template.pot",
            ]
            + py_files,
            check=True,
        )

        # Para actualizar el .po con el nunevo .pot
        # msgmerge --update en_US.po lenguaje_template.pot


app = App()
app.run()
