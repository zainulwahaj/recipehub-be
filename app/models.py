from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# --- Enums ---
class UserType(str, enum.Enum):
    REGULAR = "REGULAR"
    CHEF = "CHEF"

# --- SQLAlchemy Models ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    user_type = Column(String(20), default=UserType.REGULAR.value, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    ingredients = Column(JSON, nullable=False)
    steps = Column(JSON, nullable=False)
    time_minutes = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)
    source = Column(String, nullable=False)
    is_public = Column(Boolean, default=True)
    avg_rating = Column(Numeric(precision=3, scale=2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="recipes")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Pydantic Schemas ---

# User Schemas
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    user_type: Optional[UserType] = UserType.REGULAR

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    accessToken: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    user_type: UserType

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    accessToken: str
    user: UserResponse

# Recipe Schemas
class RecipeCreate(BaseModel):
    title: str
    description: str
    ingredients: List[str]
    steps: List[str]
    time_minutes: int
    difficulty: str
    tags: Optional[List[str]] = None
    is_public: bool = True

class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    time_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class AuthorInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class RecipeResponse(BaseModel):
    id: int
    title: str
    description: str
    ingredients: List[str]
    steps: List[str]
    time_minutes: int
    difficulty: str
    tags: Optional[List[str]]
    source: str
    is_public: bool
    avg_rating: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]
    author: AuthorInfo
    is_owner: Optional[bool] = None
    is_favorite: Optional[bool] = None
    user_rating: Optional[int] = None

    class Config:
        from_attributes = True

# Favorite Schemas
class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Rating Schemas
class RatingCreate(BaseModel):
    rating: int

class RatingResponse(BaseModel):
    user_rating: int
    avg_rating: Optional[Decimal]

# AI Schemas
class AIGenerateRequest(BaseModel):
    ingredients: List[str]
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    max_time_minutes: int = 30
    difficulty: str = "Easy"
    servings: int = 2

class AIGenerateResponse(BaseModel):
    recipe: RecipeResponse
