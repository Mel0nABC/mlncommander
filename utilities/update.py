from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.overwrite_options import Overwrite_dialog
from views.selected_for_copy import Selected_for_copy
from views.copying import Copying
import gi, os, time, shutil, asyncio, threading, multiprocessing
from gi.repository import GLib


def on_update_dir():
    """
    TODO, pulsar para actualizar directorio actual.
    """

    return
