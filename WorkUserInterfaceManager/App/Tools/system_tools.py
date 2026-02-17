import logging

from TemplateProject.core.services.directory_service import DirectoryService


def system_tool(type_tool, main_path, load_exe_path, icon_ico_path) -> list:
    logging.getLogger("system_tool")
    DSApplicationService = DirectoryService(main_path, starry_dir=True)
    logging.info(f"[!!] - vm_new_application - system_tool - Начало -> {type_tool, main_path, load_exe_path, icon_ico_path}")
    logging.info(f"[if⏳else] - vm_new_application - system_tool - Условие -> type_tool")
    if type_tool == 'new_app':
        logging.info(f"[if⏳else] - vm_new_application - system_tool - Истина -> type_tool")
        file_name_id = 1
        logging.info(f"[if⏳else] - vm_new_application - system_tool - Начало бесконечного цикла -> while True")
        while True:
            logging.info(f"[if⏳else] - vm_new_application - system_tool - Условие Цикла -> if not DSApplicationService, file_name_id = {file_name_id}")
            if not DSApplicationService.search_files(str(file_name_id)):
                logging.info(f"[if⏳else] - vm_new_application - system_tool - Истина Цикла -> if not DSApplicationService, file_name_id = {file_name_id}")
                try:
                    DSApplicationService.create_shortcut(load_exe_path, main_path, shortcut_name=str(file_name_id) + '.exe',
                                                         source_mode=True)
                    DSApplicationService.copy_file(icon_ico_path, main_path,
                                                   new_name=str(file_name_id) + '.png',
                                                   source_mode=True)
                except Exception as e:
                    logging.debug(f"[Except][if⏳else] - vm_new_application - system_tool - Ошибка create_shortcut - {e}")
                    raise e
                logging.info(f"[✅][if⏳else] - vm_new_application - system_tool - Конец Цикла -> Возвращение!")
                return [main_path, [str(file_name_id) + '.exe', str(file_name_id) + '.png']]
            elif file_name_id > 993:
                logging.info(f"[✅][if⏳else] - vm_new_application - system_tool - Конец Цикла -> ValueError")
                raise ValueError("Ошибка, номер файла больше 993...")
            else:
                file_name_id += 1
            logging.info(f"[!!][if⏳else] - vm_new_application - system_tool - Повтор Цикла...")


def system_tool_load(type_tool, main_path, sub_path, sub_sub_path) -> list:
    if sub_path == int or sub_sub_path == int:
        return []
    logging.getLogger("system_tool_load")
    logging.info(f"[!!] - load_project_data - system_tool_load - Начало -> {type_tool, main_path, sub_path, sub_sub_path}")
    DSApplicationService = DirectoryService(str(main_path) + str(sub_path) + '/' + str(sub_sub_path), starry_dir=True)
    if type_tool == 'load_project':
        logging.info(
            f"[!!] - system_tool_load - load_project - Условно -> list_files = {DSApplicationService.list_files()}")
        DSApplicationService.create_directory("DocData")
        DSApplicationService.create_directory("LearnData")
        DSApplicationService.create_directory("SourceData")
        DSApplicationService.create_directory("ResultData")
        return [{'id': idx, 'name': item} for idx, item in enumerate(DSApplicationService.list_files() + DSApplicationService.get_directories())]
    elif type_tool == 'start_project':
        logging.info(f"[!!] - system_tool_load - load_project - Условно -> start_project")
        DSApplicationService.openFolder("")
    raise TypeError("Такого инструмента нет!")
