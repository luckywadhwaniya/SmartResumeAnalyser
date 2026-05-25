import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secret key for generating tokens (In a real app, hide this in a .env file!)
SECRET_KEY = "super-secret-resume-analyzer-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Tokens last for 7 days

# Password hashing engine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    """Checks if a typed password matches the scrambled database password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Scrambles a password before saving it to the database."""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """Creates the secure JWT VIP badge for the user."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Acts as the bouncer: checks the user's token before letting them save/fetch data."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")