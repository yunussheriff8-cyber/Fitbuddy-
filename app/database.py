"""SQLAlchemy models and database helper functions (SQLite)."""
import os
from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(PROJECT_ROOT, 'fitbuddy.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(200), nullable=False)
    intensity = Column(String(20), nullable=False)
    schedule = Column(Integer, default=7)


class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)


def init_db() -> None:
    """Create tables if they do not exist yet."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------- users
def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str) -> None:
    """Create the user, or update their details if the ID already exists."""
    with SessionLocal() as db:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            db.add(
                User(
                    id=user_id,
                    name=name,
                    age=age,
                    weight=weight,
                    goal=goal,
                    intensity=intensity,
                    schedule=7,  # 7-day plan
                )
            )
        db.commit()


def get_user(user_id: int) -> Optional[User]:
    with SessionLocal() as db:
        return db.query(User).filter(User.id == user_id).first()


def get_all_users() -> list:
    with SessionLocal() as db:
        return db.query(User).order_by(User.id).all()


def delete_user(user_id: int) -> bool:
    """Delete a user and their plans. Returns True if the user existed."""
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).delete()
        db.delete(user)
        db.commit()
        return True


# ---------------------------------------------------------------- plans
def save_plan(user_id: int, plan: str) -> None:
    """Store a freshly generated plan.

    If the user already has a plan, it is replaced and any earlier
    feedback update is cleared (a new plan starts a new history).
    """
    with SessionLocal() as db:
        workout = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if workout:
            workout.original_plan = plan
            workout.updated_plan = None
        else:
            db.add(WorkoutPlan(user_id=user_id, original_plan=plan))
        db.commit()


def update_plan(user_id: int, updated_text: str) -> None:
    """Save the feedback-based revision next to the original plan."""
    with SessionLocal() as db:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()


def get_original_plan(user_id: int) -> Optional[str]:
    with SessionLocal() as db:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None


def get_current_plan(user_id: int) -> Optional[str]:
    """Latest version of the plan: the update if there is one, else the original."""
    with SessionLocal() as db:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if not plan:
            return None
        return plan.updated_plan or plan.original_plan


def get_all_plans() -> list:
    with SessionLocal() as db:
        return db.query(WorkoutPlan).all()
