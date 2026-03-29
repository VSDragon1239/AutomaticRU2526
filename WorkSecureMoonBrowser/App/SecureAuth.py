import bcrypt
import pyotp
import json
import logging
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureAuthSystem:
    def __init__(self, storage_file: str = "users.json", master_password: str = None):
        self.storage_file = storage_file
        self.logger = logging.getLogger(__name__)

        # Настройка логирования
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

        # Инициализация шифрования на основе мастер-пароля
        if not master_password:
            raise ValueError("Мастер-пароль обязателен!")

        self.fernet = self._derive_key(master_password)
        self.users = self._load_users()

    def _derive_key(self, password: str) -> Fernet:
        """Генерация ключа шифрования из мастер-пароля"""
        # Соль фиксирована для переносимости между запусками (можно вынести в конфиг)
        salt = b'MoonBrowser_Salt_Secure_v1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)

    def _encrypt_data(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Ошибка _decrypt_data: {e} - Неверный ключ")
            # Если ключ неверен, вернется ошибка или мусор
            return ""

    def _load_users(self) -> dict:
        if not os.path.exists(self.storage_file):
            return {}
        try:
            with open(self.storage_file, 'r') as f:
                raw_data = json.load(f)
                self.logger.error(f"Данные файла: {raw_data.items()}")
                users = {}
                for u, d in raw_data.items():
                    # Расшифровка
                    p_hash = self._decrypt_data(d.get('password_hash', ''))
                    t_secret = self._decrypt_data(d.get('totp_secret', ''))

                    # Если расшифровка вернула пустоту (неверный ключ), данные невалидны
                    if not p_hash or not t_secret:
                        self.logger.error(f"Ошибка расшифровки данных для {u}. Неверный мастер-пароль?")
                        continue

                    users[u] = {
                        'password_hash': p_hash,
                        'totp_secret': t_secret,
                        'email': d.get('email'),
                        'backup_codes': d.get('backup_codes', [])
                    }
                return users
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
            return {}

    def _save_users(self):
        try:
            raw_data = {}
            for u, d in self.users.items():
                raw_data[u] = {
                    'password_hash': self._encrypt_data(d['password_hash']),
                    'totp_secret': self._encrypt_data(d['totp_secret']),
                    'email': d.get('email'),
                    'backup_codes': d.get('backup_codes', [])
                }
            with open(self.storage_file, 'w') as f:
                json.dump(raw_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Save error: {e}")

    def register_user(self, username: str, password: str, email: str = "user@local") -> dict:
        if username in self.users:
            return {'success': False, 'message': 'Пользователь существует'}

        # Генерация 2FA
        totp_secret = pyotp.random_base32()
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        self.users[username] = {
            'password_hash': password_hash,
            'totp_secret': totp_secret,
            'email': email,
            'backup_codes': []
        }
        self._save_users()

        uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(name=username, issuer_name="MoonSecureBrowser")
        return {'success': True, 'uri': uri}

    def authenticate(self, username: str, password: str, two_factor_code: str) -> dict:
        if username not in self.users:
            return {'success': False, 'message': 'Пользователь не найден'}

        u_data = self.users[username]

        # Проверка пароля (bcrypt)
        if not bcrypt.checkpw(password.encode(), u_data['password_hash'].encode()):
            return {'success': False, 'message': 'Неверный пароль'}

        # Проверка 2FA
        totp = pyotp.TOTP(u_data['totp_secret'])
        if not totp.verify(two_factor_code, valid_window=1):
            # Проверка резервных кодов (если есть)
            if two_factor_code in u_data.get('backup_codes', []):
                u_data['backup_codes'].remove(two_factor_code)
                self._save_users()
            else:
                return {'success': False, 'message': 'Неверный код 2FA'}

        return {'success': True, 'message': 'OK'}