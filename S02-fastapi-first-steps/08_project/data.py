"""A fake database: two dictionaries and an id counter."""

COURSES: dict[int, dict] = {
    1: {'id': 1, 'title': 'Python Basics', 'price': 2_500_000, 'capacity': 20, 'level': 'beginner'},
    2: {'id': 2, 'title': 'FastAPI', 'price': 4_800_000, 'capacity': 12, 'level': 'advanced'},
    3: {'id': 3, 'title': 'HTML and CSS', 'price': 1_900_000, 'capacity': 25, 'level': 'beginner'},
}

USERS: dict[int, dict] = {
    1: {'id': 1, 'email': 'teacher@kadoos.ir', 'full_name': 'Ali Teacher', 'role': 'instructor'},
    2: {'id': 2, 'email': 'sara@example.com', 'full_name': 'Sara Ahmadi', 'role': 'student'},
}


def next_id(table: dict[int, dict]) -> int:
    return max(table, default=0) + 1
