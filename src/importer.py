# src/importer.py — импорт из разных источников
class CSVImporter:
    def import_to_db(self, file_path: str): ...


class OzonAPIImporter:
    def import_to_db(self, api_key: str): ...
