"""
Authentication utilities for PolicyEdgeAI API.

This module handles authentication, authorization, and user management
for the PolicyEdgeAI platform.
"""
import os
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6")  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Authentication objects
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Data directory for user storage (mock DB)
DATA_DIR = os.path.join(os.getcwd(), "data", "users")
os.makedirs(DATA_DIR, exist_ok=True)
USER_DB_FILE = os.path.join(DATA_DIR, "users.json")

# Initialize user database if it doesn't exist
if not os.path.exists(USER_DB_FILE):
    with open(USER_DB_FILE, "w") as f:
        # Create initial admin user
        initial_users = {
            "admin": {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "hashed_password": pwd_context.hash("admin123"),  # Change in production
                "role": "admin",
                "disabled": False,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
        }
        json.dump(initial_users, f, indent=2)


# Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "user"
    disabled: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


class UserInDB(User):
    hashed_password: str


# Helper functions
def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash a password."""
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    """Get a user from the database."""
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
            
        if username in users:
            user_dict = users[username]
            # Convert string dates to datetime objects
            if user_dict.get("created_at"):
                user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"])
            if user_dict.get("last_login") and user_dict["last_login"] is not None:
                user_dict["last_login"] = datetime.fromisoformat(user_dict["last_login"])
            return UserInDB(**user_dict)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    
    return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
        
        users[username]["last_login"] = datetime.now().isoformat()
        
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        print(f"Error updating last login: {str(e)}")
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get the current user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Return user as dict for versatility
    user_dict = user.dict()
    del user_dict["hashed_password"]  # Don't include the hashed password
    
    return user_dict


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if current_user.get("disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# User management functions
def create_user(username: str, password: str, email: str, full_name: str, role: str = "user") -> User:
    """Create a new user."""
    # Check if user already exists
    if get_user(username):
        raise ValueError(f"User {username} already exists")
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = UserInDB(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hashed_password,
        created_at=datetime.now()
    )
    
    # Save to DB
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
        
        users[username] = new_user.dict()
        users[username]["created_at"] = users[username]["created_at"].isoformat()
        
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)
        
        # Return user without password
        user = User(**new_user.dict())
        return user
    
    except Exception as e:
        raise ValueError(f"Error creating user: {str(e)}")


def update_user(username: str, **updates) -> User:
    """Update user information."""
    user = get_user(username)
    if not user:
        raise ValueError(f"User {username} not found")
    
    # Handle password update separately
    new_password = updates.pop("password", None)
    if new_password:
        updates["hashed_password"] = get_password_hash(new_password)
    
    # Update user
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
        
        for key, value in updates.items():
            if hasattr(user, key):
                users[username][key] = value
        
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=2)
        
        # Get updated user
        updated_user = get_user(username)
        if not updated_user:
            raise ValueError("Error fetching updated user")
        
        # Return without password
        user_dict = updated_user.dict()
        del user_dict["hashed_password"]
        return User(**user_dict)
    
    except Exception as e:
        raise ValueError(f"Error updating user: {str(e)}")


def delete_user(username: str) -> bool:
    """Delete a user."""
    if not get_user(username):
        raise ValueError(f"User {username} not found")
    
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
        
        if username in users:
            del users[username]
            
            with open(USER_DB_FILE, "w") as f:
                json.dump(users, f, indent=2)
            
            return True
        
        return False
    
    except Exception as e:
        raise ValueError(f"Error deleting user: {str(e)}")


def list_users() -> list:
    """List all users."""
    try:
        with open(USER_DB_FILE, "r") as f:
            users = json.load(f)
        
        # Remove password hashes
        user_list = []
        for username, user_data in users.items():
            user_data = user_data.copy()
            user_data.pop("hashed_password", None)
            user_list.append(user_data)
        
        return user_list
    
    except Exception as e:
        raise ValueError(f"Error listing users: {str(e)}")