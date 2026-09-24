"""Duplicates and broken rules: check first, and still handle `IntegrityError`.

Two layers:
1. Check in the service ("is this email taken?") -> a friendly 409 message.
2. The database constraint is the safety net. Two requests can pass the check
   at the same moment; only the database can stop the second one. So catch
   `IntegrityError`, `rollback()`, and answer 409 too.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import User, engine, reset_database


class DuplicateEmailError(Exception):
    pass


def register(session: Session, email: str, full_name: str, check_first: bool = True) -> User:
    email = email.lower()
    if check_first and session.scalar(select(User).where(User.email == email)):
        raise DuplicateEmailError(f'{email} is already registered (checked in Python)')
    user = User(email=email, full_name=full_name)
    session.add(user)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateEmailError(f'{email} is already registered (database said no)') from error
    return user


def main() -> None:
    reset_database()
    with Session(engine) as session:
        print(register(session, 'reza@example.com', 'Reza'))
        for check_first in (True, False):
            try:
                register(session, 'SARA@example.com', 'Sara again', check_first=check_first)
            except DuplicateEmailError as error:
                print(error)
        print('the session still works:', register(session, 'nima@example.com', 'Nima'))


if __name__ == '__main__':
    main()
