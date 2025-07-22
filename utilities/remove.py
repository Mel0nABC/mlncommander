from controls.Actions import Actions
from pathlib import Path
from datetime import datetime
from views.copying import Copying
from views.selected_for_delete import Selected_for_delete
import gi, os, time, shutil, asyncio, threading, multiprocessing, traceback, subprocess
from gi.repository import GLib


class Remove:

    def __init__(self):
        self.action = Actions()

    def on_delete(self, explorer_src, explorer_dst, parent):
        """
        Eliminar archivos y directorios, sin vuelta atrás.

        """
        src_info = explorer_src.actual_path

        if not src_info.exists():
            self.action.show_msg_alert(
                "Ha surgido algún problema al intentar eliminar la ubicacion seleccionada"
            )
        selected_items = self.action.get_selected_items_from_explorer(explorer_src)

        if not selected_items:
            self.action.show_msg_alert("Debe seleccionar algún archivo o directorio.")
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

        def delete_now(selected_items):
            for item in selected_items:
                print(item)
                if item.exists():
                    if item.is_dir():
                        try:
                            contents = list(item.iterdir())
                            if contents:
                                delete_now(contents)
                            item.rmdir()
                        except Exception as e:
                            print(f"❌ Error al eliminar directorio {item}: {e}")

                    else:
                        try:
                            item.unlink()
                        except Exception as e:
                            print(f"❌ Error al eliminar archivo {item}: {e}")
            print(
                "FOR FINALIZADO ###########################################################"
            )

        delete_now(list(selected_items))
        self.action.change_path(explorer_src, explorer_src.actual_path)

    async def create_dialog_selected_for_delete(
        self, parent, explorer_src, selected_items
    ):
        """
        Muestra el dialog de confirmación antes de iniciar delete_now()
        """
        selected_for_delete = Selected_for_delete(parent, explorer_src, selected_items)
        response = await selected_for_delete.wait_response_async()
        return response
