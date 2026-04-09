from passlib.context import CryptContext

# Argon2: без лимита bcrypt в 72 байта и без биндинга к несовместимым версиям bcrypt на Windows.
# Старые хэши вида $2b$... (bcrypt) нужно перевыпустить при смене алгоритма или оставить отдельный путь миграции.
_pwd = CryptContext(
    schemes=["argon2"],
    default="argon2",
    deprecated="auto",
)


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)
