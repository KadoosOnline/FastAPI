"""Refactored version of `legacy_report.py` (see the starter).

Typed, small functions, no global state, no magic dicts, testable.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from training_center.models import Course


@dataclass(frozen=True, slots=True)
class CourseReportLine:
    title: str
    enrolled: int
    capacity: int
    revenue: int

    @property
    def fill_rate(self) -> float:
        return self.enrolled / self.capacity


def report_lines(courses: Iterable[Course]) -> Iterator[CourseReportLine]:
    """A generator: produces one line at a time, even for thousands of courses."""
    for course in courses:
        enrolled = len(course.student_ids)
        yield CourseReportLine(
            title=course.title,
            enrolled=enrolled,
            capacity=course.capacity,
            revenue=enrolled * course.price,
        )


def total_revenue(lines: Iterable[CourseReportLine]) -> int:
    return sum(line.revenue for line in lines)


def format_report(lines: Iterable[CourseReportLine]) -> str:
    rows = [
        f'{line.title:<25} {line.enrolled:>3}/{line.capacity:<3} '
        f'{line.fill_rate:>6.0%} {line.revenue:>14,}'
        for line in lines
    ]
    return '\n'.join(rows)
