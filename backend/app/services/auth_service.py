from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserLogin, UserRegister
from app.utils.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserRegister) -> User:
        existing = (
            self.db.query(User)
            .filter((User.username == data.username) | (User.email == data.email))
            .first()
        )
        if existing:
            raise ValueError("Username or email already exists")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            is_admin=False,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, data: UserLogin) -> dict:
        user = self.db.query(User).filter(User.username == data.username).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise ValueError("Incorrect username or password")

        token = create_access_token({"sub": str(user.id), "is_admin": user.is_admin})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
