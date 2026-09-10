"""
UNIYO LMS - Exam Question Type Definitions
Defines structured question objects for PDF generation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass(kw_only=True)
class Question:
    """Base question class - all fields keyword-only"""
    number: int
    text: str
    marks: float = 1
    question_type: str = "unknown"
    correct_answer: str = ""
    explanation: str = ""
    sub_questions: List['Question'] = field(default_factory=list)
    raw_html: str = ""

    def get_height_mm(self) -> float:
        """Calculate approximate height in mm for this question"""
        base_height = 15
        base_height += min(len(self.text) / 80, 4) * 5
        return base_height


@dataclass(kw_only=True)
class MCQQuestion(Question):
    """Multiple Choice Question"""
    options: List[Tuple[str, str]] = field(default_factory=list)
    question_type: str = "mcq"

    def get_height_mm(self) -> float:
        base = 15
        options_height = len(self.options) * 6
        answer_row = 8
        padding = 6
        return base + options_height + answer_row + padding


@dataclass(kw_only=True)
class TrueFalseQuestion(Question):
    """True/False Question"""
    question_type: str = "true_false"

    def get_height_mm(self) -> float:
        return 20


@dataclass(kw_only=True)
class MatchingQuestion(Question):
    """Matching Question"""
    column_a: List[str] = field(default_factory=list)
    column_b: List[str] = field(default_factory=list)
    question_type: str = "matching"

    def get_height_mm(self) -> float:
        base = 30
        rows = max(len(self.column_a), len(self.column_b))
        return base + (rows * 10) + 15


@dataclass(kw_only=True)
class BlankQuestion(Question):
    """Fill in the Blank Question"""
    blanks: List[str] = field(default_factory=list)
    question_type: str = "blank"

    def get_height_mm(self) -> float:
        base = 15
        return base + (len(self.blanks) * 15) + 10


@dataclass(kw_only=True)
class ShortAnswerQuestion(Question):
    """Short Answer Question"""
    answer_lines: int = 5
    question_type: str = "short_answer"

    def get_height_mm(self) -> float:
        base = 15
        return base + (self.answer_lines * 8) + 10


@dataclass(kw_only=True)
class EssayQuestion(Question):
    """Essay Question"""
    answer_lines: int = 15
    question_type: str = "essay"

    def get_height_mm(self) -> float:
        base = 20
        return base + (self.answer_lines * 8) + 10


@dataclass(kw_only=True)
class Section:
    """A section of the exam"""
    title: str
    instructions: str
    section_type: str
    questions: List[Question] = field(default_factory=list)

    def get_total_height_mm(self) -> float:
        return sum(q.get_height_mm() for q in self.questions)

    def get_question_count(self) -> int:
        return len(self.questions)


@dataclass(kw_only=True)
class ExamData:
    """Complete exam structure"""
    university: str
    course_code: str
    course_title: str
    year: int
    exam_type: str
    duration_minutes: int
    total_marks: int
    total_questions: int
    sections: List[Section] = field(default_factory=list)
    has_answer_key: bool = False

    def get_all_questions(self) -> List[Question]:
        all_q = []
        for section in self.sections:
            all_q.extend(section.questions)
        return all_q
