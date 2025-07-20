def on_delete(self, explorer_src, parent):
    """
    TODO ,para eliminar archivos y directorios.
            - pedir confirmación para borrar (eliminar, cancelar)
            - Se hará que la recursividad pida confirmación, avisando que se perderá todo. Justo después de darle a eliminar.
    """
    src_info = explorer_src.actual_path

    if not src_info.exists():
        self.action.show_msg_alert(
            "Ha surgido algún problema al intentar eliminar la ubicacion seleccionada"
        )

    selected_items = self.get_selected_items_from_explorer(explorer_src)

    asyncio.ensure_future(
        self.iterate_subfolders_to_delete(parent, explorer_src, selected_items)
    )


async def delete_select(self, parent, explorer_src, selected_items):

    response = await self.create_dialog_selected_for_delete(
        parent, explorer_src, selected_items
    )

    if not response:
        return


def delete_now():
    for item in selected_items:
        print("item")


async def create_dialog_selected_for_delete(self, parent, explorer_src, selected_items):
    selected_for_delete = Selected_for_delete(parent, explorer_src, selected_items)
    response = await selected_for_delete.wait_response_async()
    return response
