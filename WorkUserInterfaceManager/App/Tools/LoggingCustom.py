import logging
import time

from annotated_types.test_cases import cases


class MIModelFormatter(logging.Formatter):
    """Форматтер для выровненных логов MIModel"""

    def __init__(self, datefmt=None):
        super().__init__(datefmt=datefmt)

    def formatTime(self, record, datefmt=None):
        """Переопределяем формат времени с миллисекундами"""
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        # Добавляем миллисекунды
        return f"{s}.{int(record.msecs):03d}"

    def format(self, record):
        """Основной метод форматирования"""
        # Разбиваем сообщение на максимум 4 части
        msg_parts = record.getMessage().split(' - ', 3)

        if len(msg_parts) >= 4:
            prefix, module, method, message = msg_parts
            # Очищаем от лишних пробелов
            prefix = prefix.strip()
            module = module.strip()
            method = method.strip()
            message = message.strip()

            # Выравниваем каждую часть
            prefix_formatted = f"{prefix:^5}" if len(prefix) <= 5 else prefix
            module_formatted = f"{module:<15}"
            method_formatted = f"{method:<20}"

            formatted_msg = f"{prefix_formatted} - {module_formatted} - {method_formatted} - {message}"
        else:
            formatted_msg = record.getMessage()

        # Форматируем время и уровень
        time_str = self.formatTime(record, self.datefmt)
        level = f"[{record.levelname}]"

        return f"{time_str} {level} {formatted_msg}"


def get_logger_img(prefix: str) -> str:
    data_prefix: dict = {"Инициализация": "[!🡻!]", "Загрузка": "[🡻]", "Добавление": "[!✲]", "Получение": "[!🡵]",
                         "Открытие": "[⏳]", "Создание": "[!⏳]", "Возвращение": "[✅]", "Запуск": "[⏳][↴]",
                         "Ошибка": "[❌]", "Остановка": "[!❌]"}
    if prefix is None:
        return ""
    else:
        return data_prefix[prefix]
