import hashlib
import hmac
import os


def hash_password(password: str):
    # Генерируем случайную соль (16 байт)
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        600000
    )
    return salt + key


def verify_password(stored_password_bytes: bytes, provided_password_str: str):
    # 1. Извлекаем соль (первые 16 байт)
    salt = stored_password_bytes[:16]

    # 2. Извлекаем сам хеш
    stored_key = stored_password_bytes[16:]

    # 3. Хешируем введенный пароль с ТЕМ ЖЕ алгоритмом, солью и итерациями
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password_str.encode('utf-8'),
        salt,
        600000
    )

    return hmac.compare_digest(stored_key, new_key)
