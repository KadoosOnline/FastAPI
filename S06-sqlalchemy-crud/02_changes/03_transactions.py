"""Transactions: several changes that succeed or fail TOGETHER.

Everything between two commits is one transaction. If something fails in the
middle, `rollback()` undoes ALL of it -- the database never shows half a job.

    with Session(engine) as session, session.begin():
        ...          # commit at the end, rollback if an exception escapes

Here a teacher leaves: their courses move to another teacher AND their
account is deleted. If moving the courses fails, the account must stay.

A common mistake: calling `session.begin()` on a session that has already
run a query. The query silently started a transaction ("autobegin"), so
SQLAlchemy raises "A transaction is already begun on this Session".
One unit of work = one short session.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import Course, User, engine, reset_database


def hand_over(old_id: int, new_id: int, fail_half_way: bool = False) -> None:
    with Session(engine) as session, session.begin():
        for course in session.scalars(select(Course).where(Course.instructor_id == old_id)):
            course.instructor_id = new_id
            if fail_half_way:
                raise RuntimeError('network failure after moving one course')
        old = session.get(User, old_id)
        assert old is not None
        session.delete(old)


def report() -> None:
    with Session(engine) as session:
        users = session.scalar(select(func.count()).select_from(User))
        ali = session.scalar(select(func.count()).where(Course.instructor_id == 1))
        print(f'  users={users}, courses of Ali={ali}')


def main() -> None:
    reset_database()
    report()
    try:
        hand_over(old_id=1, new_id=2, fail_half_way=True)
    except RuntimeError as error:
        print('failed:', error)
    report()  # nothing changed: the first course was moved back by the rollback

    hand_over(old_id=1, new_id=2)
    print('done')
    report()


if __name__ == '__main__':
    main()
