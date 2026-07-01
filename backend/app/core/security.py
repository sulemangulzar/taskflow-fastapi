from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_hashed_password(password) -> str:
    return pwd_context.hash(password)


def verify_password(password, hashed_password) -> bool:
    return pwd_context.verify(password, hashed_password)
