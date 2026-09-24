"""The Training Center core, in plain Python (session 1 project).

No web framework yet. We model users and courses, store them in a generic
repository, and put the business rules in a service. In session 2 the same
ideas move behind FastAPI endpoints; in session 5 the repository's dict is
replaced by a real database. The rules and the exceptions stay the same.

    models.py        dataclasses + enums      (what the data looks like)
    exceptions.py    our error hierarchy      (what can go wrong)
    repository.py    generic in-memory store  (where the data lives)
    services.py      business rules           (what is allowed)
    decorators.py    @log_calls, @timed, @retry
    transactions.py  all-or-nothing changes   (a context manager)
    reports.py       the refactored report of example 12 (a generator)
"""
