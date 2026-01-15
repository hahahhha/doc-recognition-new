def extract_table_cells_to_list(table):
    cells_list = []
    for id_row, row in enumerate(table.content.values()):
        for id_col, cell in enumerate(row):
            x1 = cell.bbox.x1
            y1 = cell.bbox.y1
            x2 = cell.bbox.x2
            y2 = cell.bbox.y2
            value = cell.value
            to_dict_cell = {
                "coordinates": [[x1, y1], [x2, y2]],
                "text": value
            }
            cells_list.append(to_dict_cell)
        # draw_table(cells_list)
    return cells_list