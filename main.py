from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, create_engine, select
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt
import hashlib
import base64

# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/healthtrack_db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

# ============================================================
# MODELS
# ============================================================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    role: str = "patient"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "patient"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime
    is_active: bool

# ============================================================
# AUTH - Using bcrypt directly
# ============================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Ensure password is within 72 bytes limit
    if len(password.encode('utf-8')) > 72:
        # If longer than 72 bytes, use SHA256 hash then bcrypt
        sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
        # Base64 encode to ensure valid characters
        password_for_bcrypt = base64.b64encode(sha256_hash).decode('utf-8')
        # Truncate to 72 bytes
        password_for_bcrypt = password_for_bcrypt[:72]
    else:
        password_for_bcrypt = password
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_for_bcrypt.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        # Ensure password is within 72 bytes limit
        if len(plain_password.encode('utf-8')) > 72:
            sha256_hash = hashlib.sha256(plain_password.encode('utf-8')).digest()
            password_for_bcrypt = base64.b64encode(sha256_hash).decode('utf-8')
            password_for_bcrypt = password_for_bcrypt[:72]
        else:
            password_for_bcrypt = plain_password
        
        return bcrypt.checkpw(
            password_for_bcrypt.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# ============================================================
# CREATE TABLES
# ============================================================

try:
    SQLModel.metadata.create_all(engine)
    print("✓ Tables created successfully!")
except Exception as e:
    print(f"✗ Error creating tables: {e}")

# ============================================================
# APP
# ============================================================

app = FastAPI(title="HealthTrack API", version="1.0.0")

# ============================================================
# REGISTER
# ============================================================

@app.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    # Check username
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    
    # Check email
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    
    user.last_login = datetime.utcnow()
    session.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role
        }
    }

# ============================================================
# USERS
# ============================================================

@app.get("/users/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users", response_model=list[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    return session.exec(select(User).offset(skip).limit(limit)).all()

@app.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
def root():
    return {
        "message": "Welcome to HealthTrack API",
        "version": "1.0.0",
        "docs": "/docs"
    }
