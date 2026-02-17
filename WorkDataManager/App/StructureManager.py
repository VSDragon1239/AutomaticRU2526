import logging
from WorkDataManager.App.MainReaderChunk import MRC


class StructureManager:
    MAIN_FILE = "structure_data"
    list_json_structure_template_files = []
    chunks: list[str] = []

    def __init__(self, MainIFS, TemplateIFS, TemplateIDS):
        self.logger = logging.getLogger("StructureManager")
        self.MainIFS = MainIFS
        self.check_all_files_data(TemplateIFS, TemplateIDS)

    def check_all_files_data(self, TemplateIFS, TemplateIDS):
        for file in TemplateIDS.name_list_files("json"):
            self.list_json_structure_template_files.append(file.replace(".json", ""))

        self.logger.info(f"📁 Проверка всех текущих, программных структурных файлов: {self.list_json_structure_template_files}")


        for file_name in self.list_json_structure_template_files:
            self.logger.info(f"📁 Проверка всех текущих, созданных структурных файлов: {file_name}")
            cache_data = self.MainIFS.read_file(file_name)
            self.logger.info(f"     = = 📁 Проверка кэша: {cache_data}")
            if cache_data == {}:
                self.MainIFS.write_data(file_name, TemplateIFS.read_file(file_name))
            self.chunks.append(file_name)
            self.logger.info(f"     = = 📁 Файл : {file_name} зафиксирован / добавлен")

        if self.chunks == self.list_json_structure_template_files:
            self.list_json_structure_template_files = None

        self.logger.info(f"✅ Проверка всех текущих, созданных структурных файлов завершена!")
        self.logger.info(f"✅ {self.list_json_structure_template_files}")
        self.logger.info(f"✅ {self.chunks}")


class StructureChunkReader(StructureManager):
    MainJSONData = None
    MRC = MRC

    def __init__(self, MainIFS, TemplateIFS, TemplateIDS):
        super().__init__(MainIFS, TemplateIFS, TemplateIDS)

    def get_chunks_structure(self):
        self.logger.info(f"StructureReader === 📁 Получение структуры Chunks")
        chunks = {"ChunksData": []}
        all_chunks = self.load_chunks()

        chunks["ChunksData"].append(all_chunks)

        self.logger.info(f"StructureReader === ✅ Все Chunks получены")
        self.MainIFS.write_data("chunks_ge-0n_data/ChunksLinksData", chunks)
        return chunks

    def load_chunks(self):
        main_chunk_data = self.__get_chunk_structure(self.MAIN_FILE)
        self.logger.info(f"StructureReader === 📁 Загрузка Chunks из main_chunk_data: {main_chunk_data}")

        chunks_name_list = []
        chunks_keys_list = []
        chunks_params = []
        for chunk_links in main_chunk_data["LinksAndParamsChunk"]:
            chunks_name_list.append(chunk_links["LinkChunk"])   # system_data
            chunks_keys_list.append(chunk_links["KeyName"])     # SystemData
            chunks_params.append(chunk_links["Params"])         # ''

        chunks_data = []
        for chunk_name in chunks_name_list:
            chunks_data.append(self.__get_chunk_structure(chunk_name))
        return chunks_data

    def __get_chunk_data_recurse(self, chunk_data: dict) -> list:
        self.logger.info(f"StructureReader === 📁 Получение ссылок из данных Chunk`а: {chunk_data}")
        chunks_name_list = []
        chunks_keys_list = []
        chunks_params = []
        for chunk_links in chunk_data["LinksAndParamsChunk"]:
            chunks_name_list.append(chunk_links["LinkChunk"])
            chunks_keys_list.append(chunk_links["KeyName"])
            chunks_params.append(chunk_links["Params"])
        return chunks_name_list

    def __get_chunk_structure(self, chunk_name: str) -> dict:
        self.logger.info(f"StructureReader === 📁 Получение структуры одного Chunk по названию: {chunk_name}")
        file_data: dict = self.MainIFS.read_file(chunk_name)

        chunk = MRC.copy()
        chunk_data_list_element = list(chunk["LinksAndParamsChunk"][0])
        chunk_data_list = self.__get_links_data_in_file_data(chunk_name, file_data, chunk_data_list_element)
        chunk["NameChunk"] = chunk_name
        chunk["LinksAndParamsChunk"] = chunk_data_list
        self.logger.info(f"StructureReader === ✅ Данные Chunk - заполнены! {chunk}")
        return chunk

    def __get_links_data_in_file_data(self, chunk_name, file_data: dict, chunk_data_list_element) -> list:
        self.logger.info(f"StructureReader === 📁 Получение ссылок из Chunk: {chunk_name} и его данные {file_data}")
        chunk_links_list = []
        if file_data == {}:
            return chunk_links_list

        def get_first_key() -> str:
            for first_key in file_data.keys():
                main_key = first_key
                return main_key

        def get_all_keys() -> list:
            key_list = []
            if type(file_data[get_first_key()]) == dict:
                for all_key in file_data[get_first_key()].keys():
                    key_list.append(all_key)
            else:
                for all_key in file_data[get_first_key()][0].keys():
                    key_list.append(all_key)
            return key_list

        for key in get_all_keys():
            self.logger.info(f"=== StructureReader === Проверка ключа из Chunk: {key}")
            if type(file_data.get(get_first_key())) == dict:
                if file_data.get(get_first_key())[key] != "":
                    if_data = 1
                    KeyName = key
                    LinkChunk = file_data.get(get_first_key())[key]
                    chunk_links_list.append({chunk_data_list_element[0]: KeyName, chunk_data_list_element[1]: LinkChunk, chunk_data_list_element[2]: ""})
                    self.logger.info(f"=== StructureReader === ✅ Ключ Chunk - не имеет параметров - {if_data}! {KeyName, LinkChunk}")
                elif type(file_data.get(get_first_key())[key]) == list:
                    if_data = 2
                    KeyName = key
                    LinkChunk = file_data.get(get_first_key())[key][0]
                    Params = file_data.get(get_first_key())[key][1::]
                    chunk_links_list.append({chunk_data_list_element[0]: KeyName, chunk_data_list_element[1]: LinkChunk, chunk_data_list_element[2]: Params})
                    self.logger.info(f"=== StructureReader === ✅ Ключ Chunk - имеет параметры - {if_data}! {KeyName, LinkChunk, Params}")
            else:
                if file_data.get(get_first_key())[0][key] != "":
                    if_data = 3
                    KeyName = key
                    LinkChunk = file_data.get(get_first_key())[0][key][0]
                    Params = file_data.get(get_first_key())[0][key][1::]
                    chunk_links_list.append({chunk_data_list_element[0]: KeyName, chunk_data_list_element[1]: LinkChunk, chunk_data_list_element[2]: Params})
                    self.logger.info(f"=== StructureReader === ✅ Ключ Chunk - имеет параметры - {if_data}! {KeyName, LinkChunk, Params}")
                elif type(file_data.get(get_first_key())[0][key]) == list:
                    if_data = 4
                    KeyName = key
                    LinkChunk = file_data.get(get_first_key())[0][key][0]
                    Params = file_data.get(get_first_key())[0][key][1::]
                    chunk_links_list.append({chunk_data_list_element[0]: KeyName, chunk_data_list_element[1]: LinkChunk, chunk_data_list_element[2]: Params})
                    self.logger.info(f"=== StructureReader === ✅ Ключ Chunk - имеет параметры - {if_data}! {KeyName, LinkChunk, Params}")

        self.logger.info(f"StructureReader === ✅ Данные ссылок Chunk - заполнены! {chunk_links_list}")
        return chunk_links_list


class StructureChunkDataReader(StructureChunkReader):
    chunk_data = []

    def __init__(self, MainIFS, TemplateIFS, TemplateIDS):
        super().__init__(MainIFS, TemplateIFS, TemplateIDS)
        self.logger.info(f"📁 Проверка всех Чанков: {self.chunks}")

    def get_data_from_all_chunks(self):
        for chunk in self.chunks:
            chunk_data: dict = self.MainIFS.read_file(chunk)
            if chunk_data != {}:
                # chunk_key_name = chunk.title().replace("_", "")
                self.chunk_data.append(chunk_data)
        self.MainIFS.write_data("chunks_ge-0n_data/ChunksData", {"DataChunks": self.chunk_data})
        self.logger.info(f"✅ Все данные Чанков загружены и сохранены!: {self.chunk_data}")
