# SPDX-FileCopyrightText: 2025 Mel0nABC
#
# SPDX-License-Identifier: MIT
from views.main_window import Window
from controls.actions import Actions
from pathlib import Path
import gbulb
import subprocess
import gettext
import yaml
import gi
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

gbulb.install()  # Integrate asyncio into Gtk

# Configure gettext
APP_NAME = "mlncommander"
APP_HOME = os.path.dirname(__file__)
LOCALE_DIR = os.path.join(APP_HOME, "locales")

# Initialice gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext


class App(Gtk.Application):

    def __init__(self):
        """
        Constructor
        """
        super().__init__(application_id="com.mel0n.mlncommander")
        self.window = None

    def do_activate(self) -> None:
        """
        Initializes the application when the run() method is executed
        """

        action = Actions()
        self.window = Window(self, action)
        action.set_parent(self.window)
        self.window.present()

        # For generate translation lenguaje_template.pot
        # self.generate_project_file_list()

        # Para actualizar el .po con el nunevo .pot
        # msgmerge --update en_US.po lenguaje_template.pot

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


def load_theme():
    """
    load theme from config file
    """
    CONFIG_FILE = Path(f"{Window.APP_USER_PATH}/config.yaml")
    try:

        # We open configuration and load the from your variable.
        with open(CONFIG_FILE, "r+") as config_file:
            data = yaml.safe_load(config_file)
            os.environ["GTK_THEME"] = data["THEME_NAME"]
            print(f"THEME NAME LOADED: {os.environ["GTK_THEME"]}")

    except Exception as e:
        print(f"ERROR ON LOADING THEME: {e}")


if __name__ == "__main__":
    load_theme()

app = App()
app.run()
