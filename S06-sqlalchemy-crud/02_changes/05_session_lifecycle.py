"""What the Session remembers: identity map, flush, commit, refresh, expire.

* Identity map: inside one session, `get(Course, 1)` twice gives the SAME
  Python object (and the second time, no SQL at all).
* flush(): send pending changes to the database WITHOUT ending the
  transaction (useful to get an `id` early).
* commit(): flush + end the transaction. By default all objects are then
  "expired": the next attribute access reloads them from the database.
* refresh(obj): reload one object now.

Run with echo on and watch when SQL is sent.
"""

from sqlalchemy.orm import Session

from models import Course, engine, reset_database


def main() -> None:
    reset_database()
    engine.echo = True
    with Session(engine) as session:
        print('\n--- get twice')
        first = session.get(Course, 1)
        second = session.get(Course, 1)
        print('same object?', first is second)

        print('\n--- add + flush')
        new = Course(title='Docker', price=3_000_000, level='intermediate', instructor_id=1)
        session.add(new)
        print('id before flush:', new.id)
        session.flush()
        print('id after flush :', new.id)

        print('\n--- commit expires everything')
        session.commit()
        print('reading new.title triggers a SELECT:', new.title)

        print('\n--- rollback throws away un-committed changes')
        new.price = 1
        session.rollback()
        print('price after rollback:', new.price)


if __name__ == '__main__':
    main()
