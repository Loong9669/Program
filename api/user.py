from sqlalchemy.orm import Session
from models.user import User


def get_user(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    return {"username": user.username, "hashed_password": user.password} if user else None

def create_user(db: Session, username: str, password: str):
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
