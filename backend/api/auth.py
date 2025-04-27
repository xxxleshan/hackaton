from fastapi import APIRouter, HTTPException, Body
from db.queries import create_user, get_user_by_email
from config import JWT_SECRET, JWT_ALGORITHM
import hashlib, secrets
from jose import jwt
from fastapi import APIRouter, HTTPException, Body, Header
from jose import JWTError, jwt
from db.queries import create_user, get_user_by_email, get_user_by_id
from config import JWT_SECRET, JWT_ALGORITHM
import hashlib, secrets

router = APIRouter(prefix="/auth", tags=["auth"])


def hash_password(password: str, salt: str) -> str:
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return pwd_hash.hex()


@router.post("/register", summary="Регистрация пользователя")
def register(body: dict = Body(...)):
    first_name = body.get('first_name')
    middle_name = body.get('middle_name')
    last_name = body.get('last_name')
    email = body.get('email')
    phone = body.get('phone')
    password = body.get('password')
    dob = body.get('date_of_birthday')
    if not all([first_name, last_name, email, phone, password, dob]):
        raise HTTPException(400, 'Не все обязательные поля заполнены')

    user = get_user_by_email(email)
    if user:
        raise HTTPException(400, 'Пользователь уже существует')

    salt = secrets.token_hex(16)
    pwd_hash = hash_password(password, salt)
    number_hash = hashlib.sha256(phone.encode()).hexdigest()
    create_user(first_name, middle_name, last_name, email, number_hash, pwd_hash, salt, dob)
    return {"status": "ok", "message": "Пользователь создан"}


@router.post("/login", summary="Авторизация пользователя")
def login(body: dict = Body(...)):
    email = body.get('email')
    password = body.get('password')
    if not all([email, password]):
        raise HTTPException(400, 'Email и пароль обязательны')

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(401, 'Неверные учетные данные')
    user_id, pwd_hash, salt = user
    if hash_password(password, salt) != pwd_hash:
        raise HTTPException(401, 'Неверные учетные данные')

    token = jwt.encode({'user_id': user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user_id(authorization: str = Header(None)) -> int:
    """
    Зависимость для получения user_id из заголовка Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(401, "Authorization header missing")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(401, "Bad authorization format")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(401, "Token missing user_id")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    return int(user_id)

