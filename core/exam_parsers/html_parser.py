"""
UNIYO LMS - Exam HTML Parser
Parses exam HTML files and converts to structured Question objects

HTML Structure:
<div class="exam-question" data-type="mcq" data-question-id="9" data-correct="B) Scarcity" data-points="1.5">
    <p class="question-text">9. What is the fundamental economic problem?</p>
    <div class="options">
        <button class="option" data-answer="A) Unlimited wants">A) Unlimited wants</button>
        ...
    </div>
    <p class="explanation-text">The correct answer is B because...</p>
</div>
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from .question_types import (
    Question, MCQQuestion, TrueFalseQuestion, MatchingQuestion,
    BlankQuestion, ShortAnswerQuestion, EssayQuestion,
    Section, ExamData
)
from .matching_parser import parse_matching_question


class ExamHTMLParser:
    """Parses exam HTML and creates structured ExamData object"""
    
    def __init__(self, html_content: str):
        self.html = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def parse(self, exam_meta: Dict[str, Any]) -> ExamData:
        """
        Main parse method
        
        Args:
            exam_meta: dict with university, course_code, course_title, year, 
                      exam_type, duration_minutes, total_marks, total_questions
        
        Returns:
            ExamData object
        """
        # Parse all exam questions
        raw_questions = self.soup.find_all('div', class_='exam-question')
        
        # Group by section
        sections = self._group_into_sections(raw_questions)
        
        # Create ExamData
        exam = ExamData(
            university=exam_meta.get('university', 'University'),
            course_code=exam_meta.get('course_code', 'CODE'),
            course_title=exam_meta.get('course_title', 'Course'),
            year=exam_meta.get('year', 2024),
            exam_type=exam_meta.get('exam_type', 'Final'),
            duration_minutes=exam_meta.get('duration_minutes', 120),
            total_marks=exam_meta.get('total_marks', 100),
            total_questions=len(raw_questions),
            sections=sections
        )
        
        return exam
    
    def _group_into_sections(self, raw_questions: List) -> List[Section]:
        """
        Group questions into sections by question type
        Order: true_false, mcq, matching, blank, short_answer, essay
        """
        # Group by question type
        questions_by_type = {}
        
        for elem in raw_questions:
            q = self._parse_question(elem)
            if q is None:
                continue
            
            qtype = q.question_type
            if qtype not in questions_by_type:
                questions_by_type[qtype] = []
            questions_by_type[qtype].append(q)
        
        # Create sections in a specific order
        section_order = [
            ('true_false', 'True or False', 'Write TRUE or FALSE for each statement.'),
            ('mcq', 'Multiple Choice', 'Choose the best answer. Circle A, B, C, or D.'),
            ('matching', 'Matching', 'Match Column A with Column B.'),
            ('blank', 'Fill in the Blanks', 'Complete each sentence with the correct word.'),
            ('short_answer', 'Short Answer', 'Answer in 3-5 sentences.'),
            ('essay', 'Essay', 'Write detailed answers with examples.'),
        ]
        
        sections = []
        section_letter = ord('A')
        
        for qtype, title, instructions in section_order:
            if qtype in questions_by_type and questions_by_type[qtype]:
                section = Section(
                    title=f"SECTION {chr(section_letter)}: {title.upper()}",
                    instructions=instructions,
                    section_type=qtype,
                    questions=questions_by_type[qtype]
                )
                sections.append(section)
                section_letter += 1
        
        return sections
    
    def _parse_question(self, elem) -> Question:
        """Parse a single exam-question div into a Question object"""
        qtype = elem.get('data-type', '')
        qid = int(elem.get('data-question-id', 0))
        correct = elem.get('data-correct', '')
        points = float(elem.get('data-points', 1))
        
        # Get question text
        text_elem = elem.find('p', class_='question-text')
        if not text_elem:
            return None
        question_text = text_elem.get_text(strip=True)
        # Remove leading number like "1. "
        question_text = re.sub(r'^\d+\.\s*', '', question_text)
        
        # Get explanation
        explanation_elem = elem.find('p', class_='explanation-text')
        explanation = explanation_elem.get_text(strip=True) if explanation_elem else ''
        
        # Get options
        options = []
        options_container = elem.find('div', class_='options')
        if options_container:
            for option_btn in options_container.find_all('button', class_='option'):
                answer = option_btn.get('data-answer', '')
                label = option_btn.get_text(strip=True)
                # Extract letter (e.g., "A) text" → "A")
                letter_match = re.match(r'^([A-Z])\)', label)
                letter = letter_match.group(1) if letter_match else label[:1]
                # Get option text (remove "A) ")
                opt_text = re.sub(r'^[A-Z]\)\s*', '', label)
                options.append((letter, opt_text))
        
        # Create question based on type
        if qtype == 'true_false':
            return TrueFalseQuestion(
                number=qid,
                text=question_text,
                marks=points,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        elif qtype == 'mcq':
            return MCQQuestion(
                number=qid,
                text=question_text,
                marks=points,
                options=options,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        elif qtype == 'matching':
            # Parse matching columns
            column_a, column_b = self._parse_matching_columns(elem)
            return MatchingQuestion(
                number=qid,
                text=question_text,
                marks=points,
                column_a=column_a,
                column_b=column_b,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        elif qtype == 'blank':
            # Parse blanks
            blanks = self._parse_blanks(elem)
            return BlankQuestion(
                number=qid,
                text=question_text,
                marks=points,
                blanks=blanks,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        elif qtype == 'short_answer':
            lines = max(4, int(points * 1.5))
            return ShortAnswerQuestion(
                number=qid,
                text=question_text,
                marks=points,
                answer_lines=lines,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        elif qtype == 'essay':
            lines = max(10, int(points * 1.5))
            return EssayQuestion(
                number=qid,
                text=question_text,
                marks=points,
                answer_lines=lines,
                correct_answer=correct,
                explanation=explanation,
                raw_html=str(elem)
            )
        
        else:
            # Fallback: generic question
            return Question(
                number=qid,
                text=question_text,
                marks=int(points) if points else 1,
                raw_html=str(elem)
            )
    
    def _parse_matching_columns(self, elem) -> tuple:
        """Parse matching question columns using dedicated parser"""
        from .matching_parser import parse_matching_question
        return parse_matching_question(elem)
    
    def _parse_blanks(self, elem) -> List[str]:
        """Parse fill-in-the-blank sub-questions"""
        blanks = []
        
        # Look for list items with blanks
        for li in elem.find_all('li'):
            text = li.get_text(strip=True)
            if text:
                blanks.append(text)
        
        # If no list items, look for paragraphs with a), b), etc.
        if not blanks:
            for p in elem.find_all('p'):
                text = p.get_text(strip=True)
                if re.match(r'^[a-z]\)', text):
                    blanks.append(text)
        
        return blanks


def parse_exam_html(html_content: str, exam_meta: Dict[str, Any]) -> ExamData:
    """Convenience function"""
    parser = ExamHTMLParser(html_content)
    return parser.parse(exam_meta)
