import re
import subprocess


class DeviceManager:
    def __init__(self):
        self.drive_map = {}  # letter -> physical drive
        self.drives_name = []  # list of {"device_id", "model"}
        self.disks = {"Disks": {}}

    def _get_drive_id(self, device_id: str) -> str | None:
        """
        Возвращает букву диска (например, "C:") по физическому device_id (например, "\\\\.\\PHYSICALDRIVE0").
        """
        norm_id = device_id.strip().lower()
        for letter, phys_id in self.drive_map.items():
            if phys_id.lower() == norm_id:
                return letter
        return None

    def _get_drive_name(self, drive=None):
        if not self.drive_map:
            # 1) соберём маппинг букв в физические диски
            self._build_letter_to_physical_map()
            # 2) получим список всех физ. Дисков и их моделей
            self._fetch_drive_models()

        # Если drive не указан — вернём список всех
        if drive is None:
            return self.drives_name

        # Нормализуем вход: "C:/", "c:\" → "C:"
        drive_letter = drive.strip().upper().rstrip('\/')
        if not drive_letter.endswith(':'):
            drive_letter += ':'

        # Ищем физ. диск по букве
        phys = self.drive_map.get(drive_letter)
        if not phys:
            return None

        # Ищем в списке моделей
        for item in self.drives_name:
            if item["device_id"].lower() == phys.lower():
                return item

        return None

    def get_drive(self):
        return self.disks["Disks"]

    def _build_letter_to_physical_map(self):
        self.drive_map.clear()
        # выводит строки вида:
        # Antecedent                                           Dependent
        # \\.\ROOT\cimv2:Win32_DiskPartition.DeviceID="Disk #0, Partition #0"    \\.\ROOT\cimv2:Win32_LogicalDisk.DeviceID="C:"
        result = subprocess.run(
            ['wmic', 'path', 'Win32_LogicalDiskToPartition', 'get', 'Antecedent,Dependent'],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines()[1:]:
            if not line.strip():
                continue
            # Извлекаем номер диска из Antecedent
            m1 = re.search(r'Disk #(?P<disk>\d+), Partition #\d+', line)
            # Извлекаем букву из Dependent
            m2 = re.search(r'DeviceID="(?P<letter>[A-Z]:)"', line)
            if m1 and m2:
                disk_num = m1.group('disk')
                letter = m2.group('letter')
                self.drive_map[letter] = f"\\\\.\\PHYSICALDRIVE{disk_num}"

    def _fetch_drive_models(self):
        self.drives_name.clear()
        result = subprocess.run(
            ['wmic', 'diskdrive', 'get', 'DeviceID,Model'],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines()[1:]:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                self.disks["Disks"][f"{self._get_drive_id(parts[0])}"] = {
                    "device_id": parts[0][-1],  # "0"
                    "model": parts[1].strip(),
                }
                self.drives_name.append({
                    "device_id": parts[0][-1],  # "\\.\PHYSICALDRIVE0"
                    "model": parts[1].strip(),
                })
