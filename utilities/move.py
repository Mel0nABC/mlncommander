def on_move(self, explorer_src, explorer_dst):
    """
    TODO, Mover archivos o directorios
            - Si el fichero existe, pedir confirmación sobre escribir (sobrescribir, cancelar)
    """
    selected_items = selected_items = self.get_selected_items_from_explorer(
        explorer_src
    )
    for i in selected_items:
        print(i)
    return
