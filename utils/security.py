import bcrypt


def _to_bytes(password: str) -> bytes:
    """bcrypt 只处理前 72 字节，这里按字节截断（中文 1 个字 = 3 字节）"""
    return password.encode("utf-8")[:72]


# 密码加密
def get_hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


# 密码校验（登录时用）
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_to_bytes(password), hashed_password.encode("utf-8"))
