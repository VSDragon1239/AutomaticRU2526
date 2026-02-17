import logging

from WorkProjectManager.App.InterfacesChunksLoader import InterfacesChunksLoader


class StructureManager(InterfacesChunksLoader):
    def __init__(self, MainIFS):
        super().__init__(MainIFS)
        self.logger = logging.getLogger("StructureManager")

    def load_all_data(self):
        self.logger.info(f"[!!] - StructureManager - load_all_data")
        self.load_main_data()
        self.load_main_structure_file_name()
        self.load_main_structure_data()
        self.load_chunks_data()
        self.load_global_projects_data()
        self.load_applications_data()

    def save_all_data(self):
        self.save_main_data()
        self.save_main_structure_data()
