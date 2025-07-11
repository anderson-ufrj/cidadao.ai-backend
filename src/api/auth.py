"""
Authentication and authorization module for Cidadão.AI
Handles JWT tokens, user management, and security
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

@dataclass
class User:
    """User model"""
    id: str
    email: str
    name: str
    role: str
    is_active: bool = True
    created_at: datetime = None
    last_login: datetime = None

class AuthManager:
    """Handles authentication and JWT token management"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'cidadao-ai-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
        self.refresh_token_expire_days = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
        
        # In-memory user store (replace with database in production)
        self.users_db = {
            'admin@cidadao.ai': {
                'id': 'user_1',
                'email': 'admin@cidadao.ai',
                'name': 'Administrador',
                'password_hash': self._hash_password('admin123'),
                'role': 'admin',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            'analyst@cidadao.ai': {
                'id': 'user_2',
                'email': 'analyst@cidadao.ai', 
                'name': 'Analista',
                'password_hash': self._hash_password('analyst123'),
                'role': 'analyst',
                'is_active': True,
                'created_at': datetime.utcnow()
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user_data = self.users_db.get(email)
        if not user_data:
            return None
            
        if not self._verify_password(password, user_data['password_hash']):
            return None
            
        if not user_data['is_active']:
            return None
            
        # Update last login
        self.users_db[email]['last_login'] = datetime.utcnow()
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            role=user_data['role'],
            is_active=user_data['is_active'],
            created_at=user_data['created_at'],
            last_login=user_data['last_login']
        )
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'sub': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            'sub': user.id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        payload = self.verify_token(token)
        
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_email = payload.get('email')
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user_data = self.users_db.get(user_email)
        if not user_data or not user_data['is_active']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            role=user_data['role'],
            is_active=user_data['is_active'],
            created_at=user_data['created_at'],
            last_login=user_data.get('last_login')
        )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Find user by ID
        user_data = None
        for email, data in self.users_db.items():
            if data['id'] == user_id:
                user_data = data
                break
        
        if not user_data or not user_data['is_active']:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            role=user_data['role'],
            is_active=user_data['is_active']
        )
        
        return self.create_access_token(user)
    
    def register_user(self, email: str, password: str, name: str, role: str = 'analyst') -> User:
        """Register new user"""
        if email in self.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = f"user_{len(self.users_db) + 1}"
        password_hash = self._hash_password(password)
        
        user_data = {
            'id': user_id,
            'email': email,
            'name': name,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        self.users_db[email] = user_data
        
        return User(
            id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            role=user_data['role'],
            is_active=user_data['is_active'],
            created_at=user_data['created_at']
        )
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        # Find user by ID
        user_data = None
        user_email = None
        for email, data in self.users_db.items():
            if data['id'] == user_id:
                user_data = data
                user_email = email
                break
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not self._verify_password(old_password, user_data['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password"
            )
        
        # Update password
        self.users_db[user_email]['password_hash'] = self._hash_password(new_password)
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        for email, data in self.users_db.items():
            if data['id'] == user_id:
                self.users_db[email]['is_active'] = False
                return True
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    def get_all_users(self) -> list[User]:
        """Get all users (admin only)"""
        users = []
        for data in self.users_db.values():
            users.append(User(
                id=data['id'],
                email=data['email'],
                name=data['name'],
                role=data['role'],
                is_active=data['is_active'],
                created_at=data['created_at'],
                last_login=data.get('last_login')
            ))
        return users

# Global auth manager instance
auth_manager = AuthManager()

# FastAPI security scheme
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = None) -> User:
    """FastAPI dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return auth_manager.get_current_user(credentials.credentials)

def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(user: User) -> User:
        if user.role != required_role and user.role != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return user
    return role_checker

def require_admin(user: User = None) -> User:
    """Require admin role"""
    if user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return user