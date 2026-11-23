"""Dummy users for the API.

Run manually:
    python -m app.seed          # add users only if the table is empty
    python -m app.seed --reset  # delete all users and seed again
"""
import argparse
import random

from sqlmodel import Session, delete, func, select

from app.config import SEED_COUNT
from app.database import engine, init_db
from app.models import User

FIRST_NAMES = [
    "Ali", "Ahmed", "Sara", "Ayesha", "Hamza", "Fatima", "Usman", "Zainab",
    "Bilal", "Hira", "Omar", "Maryam", "Hassan", "Noor", "Imran", "Sana",
    "John", "Emma", "Liam", "Olivia", "Noah", "Ava", "Lucas", "Mia",
]
LAST_NAMES = [
    "Khan", "Malik", "Raza", "Sheikh", "Butt", "Qureshi", "Chaudhry", "Iqbal",
    "Smith", "Johnson", "Brown", "Taylor", "Wilson", "Clark", "Lewis", "Walker",
]


def make_users(count: int, seed: int = 42) -> list[User]:
    rng = random.Random(seed)
    users, used = [], set()
    while len(users) < count:
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        email = f"{first}.{last}{rng.randint(1, 999)}@example.com".lower()
        if email in used:
            continue
        used.add(email)
        users.append(User(
            name=f"{first} {last}",
            email=email,
            age=rng.randint(18, 65),
            is_active=rng.random() > 0.2,
        ))
    return users


def seed_if_empty(count: int = SEED_COUNT) -> int:
    """Insert dummy users when the table is empty. Returns how many were added."""
    with Session(engine) as session:
        existing = session.exec(select(func.count()).select_from(User)).one()
        if existing:
            return 0
        session.add_all(make_users(count))
        session.commit()
        return count


def reset(count: int = SEED_COUNT) -> int:
    with Session(engine) as session:
        session.exec(delete(User))
        session.commit()
    return seed_if_empty(count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed dummy users")
    parser.add_argument("--reset", action="store_true", help="delete all users first")
    parser.add_argument("--count", type=int, default=SEED_COUNT)
    args = parser.parse_args()

    init_db()
    added = reset(args.count) if args.reset else seed_if_empty(args.count)
    print(f"added {added} users" if added else "users table not empty, nothing added")
