from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hasht ein Klartext-Passwort.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vergleicht ein Klartext-Passwort mit einem gehashten Passwort.
    """
    return pwd_context.verify(plain_password, hashed_password)
