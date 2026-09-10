"""
UNIYO LMS - Past Exam PDF Generator
Generates A4 portrait exam PDFs with UNIYO branding

Layout Rules:
- Atomic questions (never split)
- Smart pagination (fill pages, no waste)
- Repeat header/footer on every page
- A4 portrait with 15mm margins
"""

from pathlib import Path
from datetime import datetime
from typing import List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.paths import CERTIFICATES_DIR, BASE_DIR
from core.exam_parsers.question_types import (
    ExamData, Section, Question,
    MCQQuestion, TrueFalseQuestion, MatchingQuestion,
    BlankQuestion, ShortAnswerQuestion, EssayQuestion
)


# ============================================
# CONFIGURATION
# ============================================

# Page dimensions (A4 portrait)
PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 × 841.89 points

# Margins
MARGIN_TOP = 25 * mm
MARGIN_BOTTOM = 15 * mm
MARGIN_LEFT = 18 * mm
MARGIN_RIGHT = 18 * mm

# Content area
CONTENT_LEFT = MARGIN_LEFT
CONTENT_RIGHT = PAGE_WIDTH - MARGIN_RIGHT
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT
CONTENT_TOP = PAGE_HEIGHT - MARGIN_TOP
CONTENT_BOTTOM = MARGIN_BOTTOM

# Colors (UNIYO brand)
COLOR_PRIMARY = HexColor('#6D28D9')      # Violet
COLOR_SECONDARY = HexColor('#4C1D95')    # Dark violet
COLOR_GOLD = HexColor('#F59E0B')         # Gold
COLOR_TEXT = HexColor('#0B0F19')         # Almost black
COLOR_TEXT_MUTED = HexColor('#64748B')   # Gray
COLOR_BORDER = HexColor('#9CA3AF')       # Light gray
COLOR_LINE = HexColor('#D1D5DB')         # Very light gray
COLOR_WATERMARK = HexColor('#F3F4F6')    # Very light
COLOR_GREEN = HexColor('#22C55E')        # Answer key
COLOR_BG_LIGHT = HexColor('#F8FAFC')     # Light background

# Fonts
FONTS_DIR = BASE_DIR / 'assets' / 'fonts'
if FONTS_DIR.exists():
    try:
        pdfmetrics.registerFont(TTFont('Poppins', str(FONTS_DIR / 'Poppins-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Poppins-Bold', str(FONTS_DIR / 'Poppins-Bold.ttf')))
    except:
        pass

def _font(name: str, default: str = 'Helvetica'):
    """Get registered font or fallback"""
    try:
        if name in pdfmetrics.getRegisteredFontNames():
            return name
    except:
        pass
    return default


# ============================================
# MAIN GENERATOR CLASS
# ============================================

class ExamPDFGenerator:
    """
    Generates professional A4 exam PDFs with smart pagination.
    """
    
    def __init__(self, exam: ExamData, output_path: Optional[Path] = None):
        self.exam = exam
        self.include_answers = False
        self._custom_output_path = output_path
        self.output_path = output_path or self._default_output_path()
        self.c = None
        self.current_y = CONTENT_TOP
        self.page_number = 0
        
    def _default_output_path(self) -> Path:
        """Generate default output path"""
        cert_id = f"{self.exam.course_code}_{self.exam.year}_{self.exam.exam_type}"
        cert_id = cert_id.replace('/', '_').replace('\\', '_').replace(' ', '_')
        suffix = '_KEY' if self.include_answers else ''
        return CERTIFICATES_DIR / f"EXAM_{cert_id}{suffix}.pdf"
    
    def generate(self, include_answers: bool = False) -> Optional[Path]:
        """
        Main entry point.
        
        Args:
            include_answers: If True, generates answer key version
        
        Returns:
            Path to generated PDF
        """
        self.include_answers = include_answers
        
        # Recalculate output path with the new include_answers flag
        if self._custom_output_path is None:
            self.output_path = self._default_output_path()
        
        self._ensure_output_dir()
        
        # Create canvas
        self.c = canvas.Canvas(
            str(self.output_path),
            pagesize=A4,
            pageCompression=1
        )
        
        # Set PDF metadata
        self.c.setTitle(f"UNIYO Exam - {self.exam.course_title} ({self.exam.year})")
        self.c.setAuthor("UNIYO - University Made for YOU")
        self.c.setSubject(f"{self.exam.exam_type} Exam - {self.exam.course_code}")
        
        # Draw cover page
        self._draw_cover_page()
        
        # Draw all sections
        for section in self.exam.sections:
            self._draw_section(section)
        
        # Draw end page
        self._draw_end_page()
        
        # Save
        self.c.save()
        
        return self.output_path
    
    def _ensure_output_dir(self):
        """Create output directory if needed"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # ============================================
    # PAGE MANAGEMENT
    # ============================================
    
    def _new_page(self):
        """Start a new page with header and footer"""
        if self.c is None:
            return
        self.c.showPage()
        self.page_number += 1
        self._draw_header()
        self._draw_footer()
        self.current_y = CONTENT_TOP
    
    def _needs_new_page(self, required_height: float) -> bool:
        """Check if we need to move to a new page"""
        return (self.current_y - required_height) < CONTENT_BOTTOM
    
    # ============================================
    # HEADER / FOOTER
    # ============================================
    
    def _draw_header(self):
        """Draw page header (logo, barcode, date)"""
        c = self.c
        c.saveState()
        
        # UNIYO Logo (top left)
        logo_path = BASE_DIR / 'assets' / 'certificates' / 'logos' / 'app_icon-192.png'
        if logo_path.exists():
            try:
                logo = ImageReader(str(logo_path))
                c.drawImage(logo, CONTENT_LEFT, PAGE_HEIGHT - 22 * mm, 14 * mm, 14 * mm, 
                           preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # UNIYO text
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(CONTENT_LEFT + 16 * mm, PAGE_HEIGHT - 14 * mm, "UNIYO")
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 6)
        c.drawString(CONTENT_LEFT + 16 * mm, PAGE_HEIGHT - 18 * mm, "University Made for YOU")
        
        # Phone number (top center)
        phone = "0923093416"
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 8)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 13 * mm, phone)
        
        # Barcode (visual)
        self._draw_barcode(PAGE_WIDTH / 2 - 15 * mm, PAGE_HEIGHT - 20 * mm, 30 * mm, 5 * mm, phone)
        
        # Date (top right)
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        today = datetime.now().strftime('%d %b %Y')
        c.drawRightString(CONTENT_RIGHT, PAGE_HEIGHT - 12 * mm, today)
        
        c.setFont('Helvetica', 6)
        c.drawRightString(CONTENT_RIGHT, PAGE_HEIGHT - 16 * mm, "Printed")
        
        # Divider line
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(1)
        c.line(CONTENT_LEFT, PAGE_HEIGHT - 24 * mm, CONTENT_RIGHT, PAGE_HEIGHT - 24 * mm)
        
        # Course context line
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        context = f"{self.exam.course_title} ({self.exam.course_code}) • {self.exam.exam_type.upper()} EXAM {self.exam.year}"
        c.drawString(CONTENT_LEFT, PAGE_HEIGHT - 28 * mm, context)
        
        c.restoreState()
    
    def _draw_footer(self):
        """Draw page footer (page number, contact)"""
        c = self.c
        c.saveState()
        
        # Divider line
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, 12 * mm, CONTENT_RIGHT, 12 * mm)
        
        # Page info (left)
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        page_info = f"UNIYO • Page {self.page_number} • {self.exam.course_code} {self.exam.exam_type} {self.exam.year}"
        c.drawString(CONTENT_LEFT, 8 * mm, page_info)
        
        # Contact (right)
        c.setFont('Helvetica', 7)
        c.drawRightString(CONTENT_RIGHT, 8 * mm, "t.me/challengepr")
        
        c.restoreState()
    
    def _draw_barcode(self, x: float, y: float, width: float, height: float, data: str):
        """Draw a visual barcode (not a real scannable barcode)"""
        import random
        c = self.c
        c.saveState()
        c.setFillColor(black)
        
        random.seed(data)
        bar_x = x
        while bar_x < x + width:
            bar_w = random.choice([0.5, 1, 1.5]) * mm
            if bar_x + bar_w > x + width:
                bar_w = (x + width) - bar_x
            c.rect(bar_x, y, bar_w, height, fill=True, stroke=False)
            bar_x += bar_w + 0.3 * mm
        
        c.restoreState()
    
    # ============================================
    # COVER PAGE
    # ============================================
    
    def _draw_cover_page(self):
        """Draw the cover page (page 1)"""
        self.page_number = 1
        self.current_y = CONTENT_TOP
        
        c = self.c
        
        # ============ TOP SECTION: Logo + Barcode + Date ============
        # UNIYO Logo (large, top-left area)
        logo_path = BASE_DIR / 'assets' / 'certificates' / 'logos' / 'app_icon-192.png'
        if logo_path.exists():
            try:
                logo = ImageReader(str(logo_path))
                c.drawImage(logo, CONTENT_LEFT, PAGE_HEIGHT - 50 * mm, 25 * mm, 25 * mm,
                           preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # UNIYO branding
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(CONTENT_LEFT + 30 * mm, PAGE_HEIGHT - 38 * mm, "UNIYO")
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 9)
        c.drawString(CONTENT_LEFT + 30 * mm, PAGE_HEIGHT - 44 * mm, "University Made for YOU")
        
        # Phone barcode (top right)
        phone = "0923093416"
        barcode_x = CONTENT_RIGHT - 50 * mm
        barcode_y = PAGE_HEIGHT - 42 * mm
        
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(barcode_x + 25 * mm, PAGE_HEIGHT - 34 * mm, phone)
        
        self._draw_barcode(barcode_x, barcode_y, 50 * mm, 8 * mm, phone)
        
        # Print date
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 8)
        today = datetime.now().strftime('%d %b %Y')
        c.drawRightString(CONTENT_RIGHT, PAGE_HEIGHT - 50 * mm, f"Printed: {today}")
        
        # Divider
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(1.5)
        c.line(CONTENT_LEFT, PAGE_HEIGHT - 55 * mm, CONTENT_RIGHT, PAGE_HEIGHT - 55 * mm)
        
        # ============ UNIVERSITY + EXAM TYPE ============
        y = PAGE_HEIGHT - 75 * mm
        
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(PAGE_WIDTH / 2, y, self.exam.university.upper())
        
        y -= 8 * mm
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(1.5)
        c.line(PAGE_WIDTH / 2 - 40 * mm, y, PAGE_WIDTH / 2 + 40 * mm, y)
        
        y -= 12 * mm
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 16)
        exam_title = f"{self.exam.exam_type.upper()} EXAMINATION"
        c.drawCentredString(PAGE_WIDTH / 2, y, exam_title)
        
        # ============ EXAM DETAILS ============
        y -= 20 * mm
        
        details = [
            ("Subject:", self.exam.course_title),
            ("Course:", self.exam.course_code),
            ("Year:", str(self.exam.year)),
            ("Duration:", f"{self.exam.duration_minutes} minutes"),
            ("Total Marks:", str(self.exam.total_marks)),
            ("Questions:", str(self.exam.total_questions)),
        ]
        
        c.setFont('Helvetica', 10)
        for label, value in details:
            c.setFillColor(COLOR_TEXT_MUTED)
            c.setFont('Helvetica-Bold', 10)
            c.drawString(PAGE_WIDTH / 2 - 40 * mm, y, label)
            
            c.setFillColor(COLOR_TEXT)
            c.setFont('Helvetica', 10)
            c.drawString(PAGE_WIDTH / 2 - 5 * mm, y, value)
            
            y -= 7 * mm
        
        # ============ INSTRUCTIONS BOX ============
        y -= 10 * mm
        
        box_height = 50 * mm
        box_y = y - box_height
        
        c.setFillColor(COLOR_BG_LIGHT)
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(CONTENT_LEFT + 10 * mm, box_y, CONTENT_WIDTH - 20 * mm, box_height, 3 * mm,
                   fill=True, stroke=True)
        
        # Instructions header
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(CONTENT_LEFT + 15 * mm, y - 8 * mm, "INSTRUCTIONS TO CANDIDATES")
        
        # Instructions list
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica', 9)
        instructions = [
            "1. Write your name in the space provided.",
            "2. Answer ALL questions in the exam booklet.",
            "3. Use black or blue ink only.",
            "4. Mobile phones must be switched off.",
            "5. No calculators or electronic devices.",
        ]
        
        inst_y = y - 15 * mm
        for inst in instructions:
            c.drawString(CONTENT_LEFT + 15 * mm, inst_y, inst)
            inst_y -= 5 * mm
        
        # ============ STUDENT INFO BOX ============
        y = box_y - 10 * mm
        student_box_height = 40 * mm
        student_box_y = y - student_box_height
        
        c.setFillColor(white)
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(1)
        c.roundRect(CONTENT_LEFT + 10 * mm, student_box_y, CONTENT_WIDTH - 20 * mm, student_box_height, 3 * mm,
                   fill=True, stroke=True)
        
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(CONTENT_LEFT + 15 * mm, y - 8 * mm, "STUDENT INFORMATION")
        
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica', 10)
        
        fields = [
            ("Full Name:", 15),
            ("Student ID:", 24),
            ("Phone:", 33),
        ]
        
        field_y = y - 15 * mm
        for label, offset in fields:
            c.drawString(CONTENT_LEFT + 15 * mm, field_y, label)
            c.setStrokeColor(COLOR_LINE)
            c.setLineWidth(0.5)
            c.line(CONTENT_LEFT + 40 * mm, field_y - 1 * mm, CONTENT_RIGHT - 15 * mm, field_y - 1 * mm)
            field_y -= 8 * mm
        
        # ============ GOOD LUCK ============
        c.setFillColor(COLOR_GOLD)
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(PAGE_WIDTH / 2, student_box_y - 8 * mm, "Good Luck! 🎓")
        
        # Footer for cover page
        self._draw_footer()
    
    # ============================================
    # SECTION RENDERING
    # ============================================
    
    def _draw_section(self, section: Section):
        """
        Draw a section with smart pagination.
        Section header on new page if needed.
        """
        c = self.c
        
        # Calculate header height
        header_height = 25 * mm
        
        # Check if we need a new page for section header
        if self._needs_new_page(header_height + 50 * mm):
            self._new_page()
        
        # Draw section header
        self._draw_section_header(section, self.current_y)
        self.current_y -= header_height
        
        # Draw each question (atomic - never split)
        for question in section.questions:
            question_height = question.get_height_mm() * mm
            
            # Check if question fits
            if self._needs_new_page(question_height):
                self._new_page()
                # Redraw section header in compact form
                self._draw_section_header_compact(section)
                self.current_y -= 12 * mm
            
            # Draw the question
            self._draw_question(question)
            self.current_y -= (question_height + 5 * mm)  # Add gap
    
    def _draw_section_header(self, section: Section, y: float):
        """Draw full section header at top of page"""
        c = self.c
        
        # Section title
        c.setFillColor(COLOR_SECONDARY)
        c.setFont('Helvetica-Bold', 13)
        c.drawString(CONTENT_LEFT, y - 8 * mm, section.title)
        
        # Underline
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(1)
        c.line(CONTENT_LEFT, y - 11 * mm, CONTENT_RIGHT, y - 11 * mm)
        
        # Instructions
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Oblique', 9)
        c.drawString(CONTENT_LEFT, y - 16 * mm, section.instructions)
        
        # Bottom divider
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, y - 20 * mm, CONTENT_RIGHT, y - 20 * mm)
    
    def _draw_section_header_compact(self, section: Section):
        """Draw compact section header when continued on new page"""
        c = self.c
        y = self.current_y
        
        # Compact title
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(CONTENT_LEFT, y - 5 * mm, f"{section.title} (continued)")
        
        # Divider
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, y - 8 * mm, CONTENT_RIGHT, y - 8 * mm)
    
    # ============================================
    # QUESTION DISPATCHER
    # ============================================
    
    def _draw_question(self, question: Question):
        """Dispatch to correct question renderer"""
        if isinstance(question, MCQQuestion):
            self._draw_mcq(question)
        elif isinstance(question, TrueFalseQuestion):
            self._draw_true_false(question)
        elif isinstance(question, MatchingQuestion):
            self._draw_matching(question)
        elif isinstance(question, BlankQuestion):
            self._draw_blank(question)
        elif isinstance(question, ShortAnswerQuestion):
            self._draw_short_answer(question)
        elif isinstance(question, EssayQuestion):
            self._draw_essay(question)
        else:
            self._draw_generic_question(question)
    
    # ============================================
    # QUESTION RENDERERS (Real implementations)
    # ============================================
    
    def _draw_mcq(self, question: MCQQuestion):
        """
        Draw Multiple Choice Question.
        Structure:
            Q1. Question text...                     [2 marks]
                Ⓐ Option 1
                Ⓑ Option 2
                Ⓒ Option 3
                Ⓓ Option 4
                Answer:  ⓐ  ⓑ  ⓒ  ⓓ
        """
        c = self.c
        y = self.current_y
        
        # Question text (bold, wrapped)
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped_lines = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        
        for line in wrapped_lines:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks (gold, top-right)
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Options
        y -= 1 * mm
        options_start_y = y
        
        letters = ['Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ']
        for i, (letter, opt_text) in enumerate(question.options[:4]):
            symbol = letters[i] if i < len(letters) else f"({letter})"
            
            c.setFillColor(COLOR_TEXT)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(CONTENT_LEFT + 6 * mm, y, symbol)
            
            c.setFont('Helvetica', 9)
            opt_wrapped = self._wrap_text(opt_text, 'Helvetica', 9, CONTENT_WIDTH - 20 * mm)
            
            # First line with symbol
            if opt_wrapped:
                c.drawString(CONTENT_LEFT + 12 * mm, y, opt_wrapped[0])
                y -= 4.5 * mm
                
                # Continuation lines
                for line in opt_wrapped[1:]:
                    c.drawString(CONTENT_LEFT + 12 * mm, y, line)
                    y -= 4.5 * mm
            
            y -= 1 * mm  # Gap between options
        
        # Answer row
        y -= 2 * mm
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(CONTENT_LEFT + 6 * mm, y, "Answer:")
        
        c.setFont('Helvetica', 10)
        c.setFillColor(COLOR_TEXT)
        answer_symbols = '    ⓐ    ⓑ    ⓒ    ⓓ'
        c.drawString(CONTENT_LEFT + 22 * mm, y, answer_symbols)
        
        # If answer key mode, draw the correct answer in green
        if self.include_answers and hasattr(question, 'correct_answer'):
            c.setFillColor(COLOR_GREEN)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(CONTENT_LEFT + 70 * mm, y, f"✓ {question.correct_answer}")
    
    def _draw_true_false(self, question: TrueFalseQuestion):
        """
        Draw True/False Question.
        Structure:
            Q21. Statement text...                    [1 mark]
                 Answer:    Ⓣ TRUE      Ⓕ FALSE
        """
        c = self.c
        y = self.current_y
        
        # Question text (bold, wrapped)
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks (top-right)
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Answer row
        y -= 2 * mm
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(CONTENT_LEFT + 6 * mm, y, "Answer:")
        
        c.setFont('Helvetica', 10)
        c.setFillColor(COLOR_TEXT)
        c.drawString(CONTENT_LEFT + 22 * mm, y, "Ⓣ TRUE        Ⓕ FALSE")
        
        # Answer key mode
        if self.include_answers and hasattr(question, 'correct_answer'):
            c.setFillColor(COLOR_GREEN)
            c.setFont('Helvetica-Bold', 9)
            c.drawString(CONTENT_LEFT + 70 * mm, y, f"✓ {question.correct_answer}")
    
    def _draw_matching(self, question: MatchingQuestion):
        """
        Draw Matching Question.
        Structure:
            Q31. Match Column A with Column B.        [5 marks]
                
                  COLUMN A              COLUMN B
                  ─────────             ─────────
                  1. Item ____          A. Item
                  2. Item ____          B. Item
        """
        c = self.c
        y = self.current_y
        
        # Question text
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Column headers
        y -= 3 * mm
        col_a_x = CONTENT_LEFT + 6 * mm
        col_b_x = CONTENT_LEFT + CONTENT_WIDTH / 2 + 5 * mm
        col_width = CONTENT_WIDTH / 2 - 8 * mm
        
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 9)
        c.drawString(col_a_x, y, "COLUMN A")
        c.drawString(col_b_x, y, "COLUMN B")
        
        y -= 2 * mm
        c.setStrokeColor(COLOR_PRIMARY)
        c.setLineWidth(0.5)
        c.line(col_a_x, y, col_a_x + col_width, y)
        c.line(col_b_x, y, col_b_x + col_width, y)
        
        # Rows
        y -= 5 * mm
        rows = max(len(question.column_a), len(question.column_b))
        
        for i in range(rows):
            c.setFillColor(COLOR_TEXT)
            c.setFont('Helvetica', 9)
            
            # Column A
            if i < len(question.column_a):
                text_a = f"{i+1}. {question.column_a[i]}"
                wrapped_a = self._wrap_text(text_a, 'Helvetica', 9, col_width - 15 * mm)
                if wrapped_a:
                    c.drawString(col_a_x, y, wrapped_a[0])
                    for line in wrapped_a[1:]:
                        y -= 4 * mm
                        c.drawString(col_a_x, y, line)
            
            # Blank for answer
            c.setFillColor(COLOR_TEXT_MUTED)
            c.drawString(col_a_x + col_width - 12 * mm, y, "____")
            
            # Column B
            c.setFillColor(COLOR_TEXT)
            if i < len(question.column_b):
                letter = chr(ord('A') + i)
                text_b = f"{letter}. {question.column_b[i]}"
                wrapped_b = self._wrap_text(text_b, 'Helvetica', 9, col_width - 5 * mm)
                if wrapped_b:
                    c.drawString(col_b_x, y, wrapped_b[0])
                    for line in wrapped_b[1:]:
                        y -= 4 * mm
                        c.drawString(col_b_x, y, line)
            
            y -= 8 * mm
    
    def _draw_blank(self, question: BlankQuestion):
        """
        Draw Fill in the Blank Question.
        Structure:
            Q41. Complete the following:              [5 marks]
                 a) Text with _______________ to fill
                 b) Text with _______________ to fill
        """
        c = self.c
        y = self.current_y
        
        # Question text
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Sub-items
        y -= 2 * mm
        if question.blanks:
            for i, item in enumerate(question.blanks):
                c.setFillColor(COLOR_TEXT)
                c.setFont('Helvetica', 9)
                
                # Letter
                letter = f"{chr(ord('a') + i)})"
                c.setFont('Helvetica-Bold', 9)
                c.drawString(CONTENT_LEFT + 6 * mm, y, letter)
                
                c.setFont('Helvetica', 9)
                wrapped = self._wrap_text(item, 'Helvetica', 9, CONTENT_WIDTH - 20 * mm)
                for line in wrapped:
                    c.drawString(CONTENT_LEFT + 14 * mm, y, line)
                    y -= 4.5 * mm
                
                # Blank line
                c.setStrokeColor(COLOR_TEXT_MUTED)
                c.setLineWidth(0.4)
                c.line(CONTENT_LEFT + 14 * mm, y + 1 * mm, CONTENT_LEFT + 80 * mm, y + 1 * mm)
                
                y -= 5 * mm
        else:
            # No sub-items, use main text with blank
            c.setFont('Helvetica', 9)
            c.setFillColor(COLOR_TEXT)
            c.drawString(CONTENT_LEFT + 6 * mm, y, question.text + " _______________________")
            y -= 8 * mm
    
    def _draw_short_answer(self, question: ShortAnswerQuestion):
        """
        Draw Short Answer Question.
        Structure:
            Q46. Question text...                     [5 marks]
                 ┌─────────────────────────────────┐
                 │ ________________________________│
                 │ ________________________________│
                 │ ________________________________│
                 └─────────────────────────────────┘
        """
        c = self.c
        y = self.current_y
        
        # Question text
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Answer lines
        y -= 5 * mm
        lines = question.answer_lines if hasattr(question, 'answer_lines') else 5
        
        for i in range(lines):
            c.setStrokeColor(COLOR_LINE)
            c.setLineWidth(0.4)
            c.line(CONTENT_LEFT + 6 * mm, y, CONTENT_RIGHT - 6 * mm, y)
            y -= 7 * mm
    
    def _draw_essay(self, question: EssayQuestion):
        """
        Draw Essay Question.
        Same as short answer but more lines.
        """
        c = self.c
        y = self.current_y
        
        # Question text
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
        
        # Answer lines
        y -= 5 * mm
        lines = question.answer_lines if hasattr(question, 'answer_lines') else 15
        
        for i in range(lines):
            c.setStrokeColor(COLOR_LINE)
            c.setLineWidth(0.4)
            c.line(CONTENT_LEFT + 6 * mm, y, CONTENT_RIGHT - 6 * mm, y)
            y -= 7 * mm
    
    def _draw_generic_question(self, question: Question):
        """Draw generic question (fallback)"""
        c = self.c
        y = self.current_y
        
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 10)
        text = f"Q{question.number}. {question.text}"
        wrapped = self._wrap_text(text, 'Helvetica-Bold', 10, CONTENT_WIDTH - 25 * mm)
        for line in wrapped:
            c.drawString(CONTENT_LEFT, y, line)
            y -= 5 * mm
        
        # Marks
        marks_text = f"[{self._format_marks(question.marks)}]"
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(COLOR_GOLD)
        c.drawRightString(CONTENT_RIGHT, self.current_y, marks_text)
    
    # ============================================
    # UTILITY HELPERS
    # ============================================
    
    def _wrap_text(self, text: str, font: str, size: int, max_width: float) -> list:
        """Wrap text into lines that fit within max_width"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            width = stringWidth(test_line, font, size)
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _format_marks(self, marks) -> str:
        """Format marks: 1.5 → '1.5 marks', 1 → '1 mark'"""
        if marks == int(marks):
            marks = int(marks)
            return f"{marks} mark{'s' if marks != 1 else ''}"
        return f"{marks} marks"
    
    # ============================================
    # END PAGE
    # ============================================
    
    def _draw_end_page(self):
        """Draw end of exam page"""
        # Start fresh page
        self._new_page()
        
        c = self.c
        y = self.current_y - 50 * mm
        
        # Divider
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(2)
        c.line(PAGE_WIDTH / 2 - 60 * mm, y, PAGE_WIDTH / 2 + 60 * mm, y)
        
        # END OF EXAM
        y -= 15 * mm
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(PAGE_WIDTH / 2, y, "END OF EXAMINATION")
        
        # Divider
        y -= 10 * mm
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(2)
        c.line(PAGE_WIDTH / 2 - 60 * mm, y, PAGE_WIDTH / 2 + 60 * mm, y)
        
        # Good luck
        y -= 20 * mm
        c.setFillColor(COLOR_GOLD)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(PAGE_WIDTH / 2, y, "✨ GOOD LUCK! ✨")
        
        # Summary box
        y -= 30 * mm
        summary_height = len(self.exam.sections) * 7 * mm + 25 * mm
        summary_y = y - summary_height
        
        c.setFillColor(COLOR_BG_LIGHT)
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.roundRect(CONTENT_LEFT + 20 * mm, summary_y, CONTENT_WIDTH - 40 * mm, summary_height, 3 * mm,
                   fill=True, stroke=True)
        
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(CONTENT_LEFT + 25 * mm, y - 8 * mm, "📋 EXAM SUMMARY")
        
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica', 9)
        section_y = y - 15 * mm
        for section in self.exam.sections:
            questions = section.questions
            if questions:
                q_range = f"Q{questions[0].number}-Q{questions[-1].number}"
                total_marks = sum(q.marks for q in questions)
                marks_str = f"{int(total_marks) if total_marks == int(total_marks) else total_marks} marks"
                line = f"{section.title.split(':')[0]}: {section.title.split(':', 1)[1].strip()[:25]}    {q_range}    {marks_str}"
                c.drawString(CONTENT_LEFT + 25 * mm, section_y, line)
                section_y -= 6 * mm
        
        # Total
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(CONTENT_LEFT + 25 * mm, section_y - 2 * mm, 
                    f"TOTAL: {self.exam.total_questions} questions    {self.exam.total_marks} marks")
        
        # Contact info at bottom
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 9)
        bottom_y = MARGIN_BOTTOM + 30 * mm
        c.drawCentredString(PAGE_WIDTH / 2, bottom_y, "UNIYO - University Made for YOU")
        c.drawCentredString(PAGE_WIDTH / 2, bottom_y - 5 * mm, "📱 0923093416  •  💬 t.me/challengepr")
        c.drawCentredString(PAGE_WIDTH / 2, bottom_y - 10 * mm, "🌐 uniyo-cloud.onrender.com")


# ============================================
# PUBLIC FUNCTION
# ============================================

def generate_exam_pdf(exam: ExamData, include_answers: bool = False, 
                      output_path: Optional[Path] = None) -> Optional[Path]:
    """
    Generate a past exam PDF.
    
    Args:
        exam: ExamData object
        include_answers: If True, generate answer key version
        output_path: Optional custom output path
    
    Returns:
        Path to generated PDF or None if failed
    """
    try:
        generator = ExamPDFGenerator(exam, output_path)
        return generator.generate(include_answers=include_answers)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
