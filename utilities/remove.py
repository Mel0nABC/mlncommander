from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.copying import Copying
from views.selected_for_delete import Selected_for_delete
from views.deleting import Deleting
import gi, os, time, shutil, asyncio, threading, multiprocessing, traceback, subprocess
from gi.repository import GLib


class Remove:

    def __init__(self):
        self.action = Actions()
        self.dialog_deleting = None
        self.stop_deleting = False

    def on_delete(self, explorer_src, explorer_dst, parent):
        """
        Eliminar archivos y directorios, sin vuelta atrás.

        """
        src_info = explorer_src.actual_path

        if not src_info.exists():
            self.action.show_msg_alert(
                parent,
                "Ha surgido algún problema al intentar eliminar la ubicacion seleccionada",
            )

        selected_items = explorer_src.get_selected_items_from_explorer()[1]

        if not selected_items:
            self.action.show_msg_alert(
                parent, "Debe seleccionar algún archivo o directorio."
            )
            return

        asyncio.ensure_future(
            self.delete_select(parent, explorer_src, explorer_dst, selected_items)
        )

    async def delete_select(self, parent, explorer_src, explorer_dst, selected_items):
        """
        Pide  confirmación sobre que eliminar y lo realiza, borra el contenido de directorios.
        """
        response = await self.create_dialog_selected_for_delete(
            parent, explorer_src, selected_items
        )
        if not response:
            return

        self.thread_update_deleting = threading.Thread(
            target=self.delete_now,
            args=(selected_items, explorer_src, explorer_dst, parent),
        )

        response = await self.create_dialog_deleting(parent, explorer_src.actual_path)

        if not response:
            self.stop_deleting = True
            self.action.show_msg_alert(
                parent, "Se detubo el proceso de borrado antes de finalizar."
            )

    def delete_now(self, selected_items, explorer_src, explorer_dst, parent):

        for item in selected_items:

            if self.stop_deleting:
                return

            GLib.idle_add(self.dialog_deleting.update_labels, item)

            if item.exists():
                if item.is_dir():
                    try:
                        contents = list(item.iterdir())
                        if contents:
                            self.delete_now(contents, explorer_src, parent)
                        if item == explorer_dst.actual_path:
                            GLib.idle_add(
                                explorer_dst.load_new_path,
                                explorer_dst.actual_path.parent,
                            )
                        item.rmdir()

                    except Exception as e:
                        print(f"❌ Error al eliminar directorio {item}: {e}")

                else:
                    try:
                        item.unlink()
                    except Exception as e:
                        print(f"❌ Error al eliminar archivo {item}: {e}")

            GLib.idle_add(explorer_src.load_new_data_path, item.parent)
            GLib.idle_add(explorer_src.scroll_to, 0, None, explorer_src.flags)

        GLib.idle_add(self.dialog_deleting.finish_deleting)

    async def create_dialog_deleting(self, parent, src_info):
        """
        Crea dialog mostrando info del archivo que se está copiando
        """
        self.dialog_deleting = Deleting(parent, src_info)
        self.thread_update_deleting.start()
        self.dialog_deleting.update_labels(src_info)
        response = await self.dialog_deleting.wait_response_async()
        return response

    async def create_dialog_selected_for_delete(
        self, parent, explorer_src, selected_items
    ):
        """
        Muestra el dialog de confirmación antes de iniciar delete_now()
        """
        selected_for_delete = Selected_for_delete(parent, explorer_src, selected_items)
        response = await selected_for_delete.wait_response_async()
        return response
