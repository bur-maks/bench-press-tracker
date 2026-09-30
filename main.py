# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime, timedelta
import os

import bcrypt
import uvicorn

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Security
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt

from pydantic import BaseModel, Field

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    func
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base
)


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./bench.db"
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000"
    ).split(",")
    if origin.strip()
]


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Bench Press API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# =========================================================
# DATABASE
# =========================================================

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(
        String,
        unique=True,
        nullable=False
    )
    email = Column(
        String,
        unique=True,
        nullable=False
    )
    password_hash = Column(
        String,
        nullable=False
    )
    height = Column(
        Float,
        nullable=True
    )
    weight = Column(
        Float,
        nullable=True
    )
    age = Column(
        Integer,
        nullable=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class BenchRecord(Base):
    __tablename__ = "bench_records"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    weight = Column(
        Float,
        nullable=False
    )

    reps = Column(
        Integer,
        nullable=False
    )

    one_rm = Column(
        Float,
        nullable=False
    )

    date = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# REQUEST MODELS
# =========================================================

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: str = Field(
        min_length=3,
        max_length=120
    )

    password: str = Field(
        min_length=4,
        max_length=128
    )

    height: float = Field(
        default=0,
        ge=0,
        le=300
    )

    weight: float = Field(
        default=0,
        ge=0,
        le=500
    )

    age: int = Field(
        default=0,
        ge=0,
        le=120
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class BenchRequest(BaseModel):
    weight: float = Field(
        gt=0,
        le=1000
    )

    reps: int = Field(
        ge=1,
        le=36
    )


class UpdateProfileRequest(BaseModel):
    height: float = Field(
        default=0,
        ge=0,
        le=300
    )

    weight: float = Field(
        default=0,
        ge=0,
        le=500
    )

    age: int = Field(
        default=0,
        ge=0,
        le=120
    )


class CalculateRequest(BaseModel):
    weight: float = Field(
        gt=0,
        le=1000
    )

    reps: int = Field(
        ge=1,
        le=36
    )


# =========================================================
# AUTH
# =========================================================

security = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    password: str,
    hashed: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization required",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# =========================================================
# CALCULATIONS
# =========================================================

def calculate_1rm(
    weight: float,
    reps: int
) -> float:

    if reps < 37:
        return round(
            weight * (
                36 / (37 - reps)
            ),
            1
        )

    return weight


def calculate_relative_score(
    bench_kg: float,
    body_weight: float,
    height_cm: float
) -> float:

    if body_weight <= 0 or height_cm <= 0:
        return 0

    return round(
        (bench_kg / body_weight)
        * (height_cm / 170),
        3
    )


# =========================================================
# SITE
# =========================================================

@app.get(
    "/",
    include_in_schema=False
)
def serve_home():
    return FileResponse(
        STATIC_DIR / "index_fixed.html"
    )


@app.get(
    "/site",
    include_in_schema=False
)
def serve_site():
    return FileResponse(
        STATIC_DIR / "index_fixed.html"
    )


@app.get("/api/health")
def health():
    return {
        "message": "Bench Press API works!",
        "status": "ok"
    }


# =========================================================
# REGISTER
# =========================================================

@app.post("/api/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    username = data.username.strip()
    email = data.email.strip().lower()

    if not username.replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Username may contain only letters, numbers and _"
        )

    existing_username = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed = get_password_hash(
        data.password
    )

    user = User(
        username=username,
        email=email,
        password_hash=hashed,
        height=(
            data.height
            if data.height > 0
            else None
        ),
        weight=(
            data.weight
            if data.weight > 0
            else None
        ),
        age=(
            data.age
            if data.age > 0
            else None
        )
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    return {
        "message":
        f"User {username} registered!"
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.username
            == data.username.strip()
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": user.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================================================
# ADD BENCH
# =========================================================

@app.post("/api/bench")
def add_bench(
    data: BenchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    one_rm = calculate_1rm(
        data.weight,
        data.reps
    )

    record = BenchRecord(
        user_id=user.id,
        weight=data.weight,
        reps=data.reps,
        one_rm=one_rm
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "Record saved!",
        "1rm": one_rm
    }


# =========================================================
# PROFILE
# =========================================================

@app.get("/api/profile")
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    best = (
        db.query(BenchRecord)
        .filter(
            BenchRecord.user_id == user.id
        )
        .order_by(
            BenchRecord.one_rm.desc()
        )
        .first()
    )

    count = (
        db.query(BenchRecord)
        .filter(
            BenchRecord.user_id == user.id
        )
        .count()
    )

    return {
        "username": user.username,
        "email": user.email,
        "height": user.height,
        "weight": user.weight,
        "age": user.age,

        "best_bench":
            best.weight
            if best else None,

        "best_reps":
            best.reps
            if best else None,

        "best_1rm":
            best.one_rm
            if best else None,

        "total_records":
            count,

        "created_at":
            user.created_at.isoformat()
    }


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.post("/api/update_profile")
def update_profile(
    data: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if data.height > 0:
        user.height = data.height

    if data.weight > 0:
        user.weight = data.weight

    if data.age > 0:
        user.age = data.age

    db.commit()

    return {
        "message": "Profile updated!"
    }


# =========================================================
# PROGRESS
# =========================================================

@app.get("/api/progress")
def get_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    records = (
        db.query(BenchRecord)
        .filter(
            BenchRecord.user_id == user.id
        )
        .order_by(
            BenchRecord.date.asc()
        )
        .all()
    )

    return [
        {
            "date":
                record.date.isoformat(),

            "one_rm":
                record.one_rm,

            "weight":
                record.weight,

            "reps":
                record.reps
        }
        for record in records
    ]


# =========================================================
# RATING
# =========================================================

@app.get("/api/rating")
def get_rating(
    db: Session = Depends(get_db)
):

    results = (
        db.query(
            User.username,
            User.weight,
            User.height,
            func.max(
                BenchRecord.weight
            ).label("real_1rm")
        )
        .join(
            BenchRecord,
            BenchRecord.user_id == User.id
        )
        .filter(
            BenchRecord.reps == 1
        )
        .group_by(
            User.id,
            User.username,
            User.weight,
            User.height
        )
        .all()
    )

    absolute_rating = []

    for result in results:
        absolute_rating.append({
            "username":
                result.username,

            "real_1rm":
                result.real_1rm,

            "weight":
                result.weight,

            "height":
                result.height
        })

    absolute_rating.sort(
        key=lambda item:
            item["real_1rm"],
        reverse=True
    )

    relative_rating = []

    for result in results:

        if (
            result.weight
            and result.height
        ):
            relative_score = (
                calculate_relative_score(
                    result.real_1rm,
                    result.weight,
                    result.height
                )
            )
        else:
            relative_score = 0

        relative_rating.append({
            "username":
                result.username,

            "real_1rm":
                result.real_1rm,

            "weight":
                result.weight,

            "height":
                result.height,

            "relative_score":
                relative_score
        })

    relative_rating.sort(
        key=lambda item:
            item["relative_score"],
        reverse=True
    )

    return {
        "absolute":
            absolute_rating[:10],

        "relative":
            relative_rating[:10]
    }


# =========================================================
# 1RM CALCULATOR
# =========================================================

@app.post("/api/calculate")
def calculate_1rm_formulas(
    data: CalculateRequest
):

    weight = data.weight
    reps = data.reps

    results = {}

    # Epley
    results["Epley"] = round(
        weight * (
            1 + 0.0333 * reps
        ),
        1
    )

    # Brzycki
    results["Brzycki"] = round(
        weight * (
            36 / (37 - reps)
        ),
        1
    )

    # Landers
    results["Landers"] = round(
        weight * (
            100
            / (
                101.3
                - 2.67123 * reps
            )
        ),
        1
    )

    # Lombardi
    results["Lombardi"] = round(
        weight * (
            reps ** 0.10
        ),
        1
    )

    # O'Conner
    max_reps = min(
        reps,
        10
    )

    results["O'Conner"] = round(
        weight * (
            1
            + 0.025 * max_reps
        ),
        1
    )

    values = list(
        results.values()
    )

    average = round(
        sum(values)
        / len(values),
        1
    )

    return {
        "formulas": results,
        "average": average,
        "min": min(values),
        "max": max(values),
        "range": round(
            max(values)
            - min(values),
            1
        ),
        "weight": weight,
        "reps": reps
    }


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    host = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    port = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )

    uvicorn.run(
        app,
        host=host,
        port=port
    )