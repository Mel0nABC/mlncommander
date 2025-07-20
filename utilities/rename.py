def on_rename(self, explorer_src, explorer_dst):
    """
    TODO, renombrar archivos o directorios.
    Si el archivo existe:
        - Cancelar
        - Remplazar
    """

    return


async def create_dialog_rename(self, parent, dst_info):
    rename_dialog = Rename_dialog(parent, dst_info)
    response = await rename_dialog.wait_response_async()
    return response
