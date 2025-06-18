import bcrypt, jwt, datetime
from ..core.config import settings

def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_pw(pw: str, pw_hash: str) -> bool:
    return bcrypt.checkpw(pw.encode(), pw_hash.encode())

def make_token(uid: int) -> str:
    now = datetime.datetime.utcnow()
    payload = {"sub": uid, "iat": now, "exp": now + datetime.timedelta(minutes=settings.JWT_EXP_MIN)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def parse_token(tok: str) -> int:
    return jwt.decode(tok, settings.JWT_SECRET, algorithms=["HS256"])["sub"]
