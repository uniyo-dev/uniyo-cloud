"""
UNIYO LMS - Exam Question Type Definitions
Defines structured question objects for PDF generation
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Question:
    """Base question class"""
    number: int
    text: str
    marks: float = 1
    question_type: str = "unknown"  # mcq, true_false, matching, blank, short_answer, essay
    sub_questions: List['Question'] = field(default_factory=list)
    raw_html: str = ""

    def get_height_mm(self) -> float:
        """Calculate approximate height in mm for this question"""
        base_height = 15  # Base question text + padding
        base_height += min(len(self.text) / 80, 4) * 5  # Text wrapping
        return base_height


@dataclass
class MCQQuestion(Question):
    """Multiple Choice Question"""
    options: List[Tuple[str, str]] = field(default_factory=list)  # [(letter, text), ...]
    
    def __post_init__(self):
        self.question_type = "mcq"
    
    def get_height_mm(self) -> float:
        """MCQ with 4 options ≈ 35mm"""
        base = 15  # Question text
        options_height = len(self.options) * 6  # Each option ~6mm
        answer_row = 8  # Answer row
        padding = 6  # Top + bottom padding
        return base + options_height + answer_row + padding


@dataclass
class TrueFalseQuestion(Question):
    """True/False Question"""
    
    def __post_init__(self):
        self.question_type = "true_false"
    
    def get_height_mm(self) -> float:
        """T/F ≈ 20mm"""
        return 20


@dataclass
class MatchingQuestion(Question):
    """Matching Question - Column A with Column B"""
    column_a: List[str] = field(default_factory=list)
    column_b: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.question_type = "matching"
    
    def get_height_mm(self) -> float:
        """Matching with N pairs ≈ 30 + 10*N mm"""
        base = 30  # Header + question text
        rows = max(len(self.column_a), len(self.column_b))
        return base + (rows * 10) + 15  # +15 for padding


@dataclass
class BlankQuestion(Question):
    """Fill in the Blank Question"""
    blanks: List[str] = field(default_factory=list)  # ["a) text ...", "b) text ..."]
    
    def __post_init__(self):
        self.question_type = "blank"
    
    def get_height_mm(self) -> float:
        """Fill-in ≈ 15mm per blank + 15mm header"""
        base = 15
        return base + (len(self.blanks) * 15) + 10


@dataclass
class ShortAnswerQuestion(Question):
    """Short Answer Question"""
    answer_lines: int = 5  # Number of lines for answer
    
    def __post_init__(self):
        self.question_type = "short_answer"
    
    def get_height_mm(self) -> float:
        """Short answer ≈ 15mm + 8mm per line"""
        base = 15
        return base + (self.answer_lines * 8) + 10


@dataclass
class EssayQuestion(Question):
    """Essay Question"""
    answer_lines: int = 15  # Number of lines for essay
    
    def __post_init__(self):
        self.question_type = "essay"
    
    def get_height_mm(self) -> float:
        """Essay ≈ 20mm + 8mm per line"""
        base = 20
        return base + (self.answer_lines * 8) + 10


@dataclass
class Section:
    """A section of the exam (e.g., Section A: MCQ)"""
    title: str
    instructions: str
    section_type: str  # mcq, true_false, matching, blank, short_answer, essay, mixed
    questions: List[Question] = field(default_factory=list)
    
    def get_total_height_mm(self) -> float:
        """Total height of all questions in section"""
        return sum(q.get_height_mm() for q in self.questions)
    
    def get_question_count(self) -> int:
        return len(self.questions)


@dataclass
class ExamData:
    """Complete exam structure"""
    university: str
    course_code: str
    course_title: str
    year: int
    exam_type: str  # Final, Mid, Quiz
    duration_minutes: int
    total_marks: int
    total_questions: int
    sections: List[Section] = field(default_factory=list)
    has_answer_key: bool = False
    
    def get_all_questions(self) -> List[Question]:
        """Flatten all questions"""
        all_q = []
        for section in self.sections:
            all_q.extend(section.questions)
        return all_q
