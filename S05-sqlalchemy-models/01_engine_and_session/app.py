"""The two main objects of SQLAlchemy: the Engine and the Session.

ENGINE  = "how to reach the database". Created ONCE per program. It owns a
          pool of connections. The URL says which database and which driver:

              sqlite:///training.db                           a file next to the script
              postgresql+psycopg://user:pass@localhost/db     PostgreSQL (example 05)

SESSION = "one conversation with the database". Short-lived: open it, do some
          work, commit, close. In FastAPI: one session per request.

`echo=True` prints every SQL statement SQLAlchemy sends -- keep it on while
learning; you will always know what really happens.

SQLite needs no installation: the database is a single file. We use it in
class; example 05 shows that PostgreSQL only needs a different URL.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///training.db', echo=True)


def main() -> None:
    # `with` = context manager: the session is closed even if an error happens.
    with Session(engine) as session:
        version = session.execute(text('select sqlite_version()')).scalar_one()
        print('SQLite version:', version)

        session.execute(
            text('create table if not exists notes (id integer primary key, body text)')
        )
        session.execute(text('insert into notes (body) values (:body)'), {'body': 'hello'})
        session.commit()

        rows = session.execute(text('select id, body from notes')).all()
        print(rows)


if __name__ == '__main__':
    main()
