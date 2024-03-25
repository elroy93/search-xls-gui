from dataclasses import dataclass


@dataclass
class SearchParams:
    dir_path: str
    search_text: str
    is_strict: bool = False
    match_case: bool = False


@dataclass
class FoundCell:
    path: str
    sheet: str
    cell: str
    cell_value: str
    row_all: list

    def __init__(self, path, sheet, cell, cell_value, row_all=()):
        self.path = str(path)
        self.sheet = str(sheet)
        self.cell = str(cell)
        self.cell_value = str(cell_value)
        self.row_all = row_all
