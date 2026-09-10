"""
UNIYO LMS - Exam Answer Key PDF Generator
Generates a dedicated answer key with answers and explanations
"""

from pathlib import Path
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from core.paths import CERTIFICATES_DIR, BASE_DIR
from core.exam_parsers.question_types import ExamData, Section, Question


# ============================================
# CONFIGURATION
# ============================================
PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_TOP = 32 * mm  # Space for header
MARGIN_BOTTOM = 15 * mm
MARGIN_LEFT = 18 * mm
MARGIN_RIGHT = 18 * mm

CONTENT_LEFT = MARGIN_LEFT
CONTENT_RIGHT = PAGE_WIDTH - MARGIN_RIGHT
CONTENT_WIDTH = CONTENT_RIGHT - CONTENT_LEFT
CONTENT_TOP = PAGE_HEIGHT - MARGIN_TOP
CONTENT_BOTTOM = MARGIN_BOTTOM

# Colors
COLOR_PRIMARY = HexColor('#6D28D9')
COLOR_SECONDARY = HexColor('#4C1D95')
COLOR_GOLD = HexColor('#F59E0B')
COLOR_TEXT = HexColor('#0B0F19')
COLOR_TEXT_MUTED = HexColor('#64748B')
COLOR_BORDER = HexColor('#9CA3AF')
COLOR_LINE = HexColor('#D1D5DB')
COLOR_BG_LIGHT = HexColor('#F8FAFC')
COLOR_GREEN = HexColor('#16A34A')  # Success/Correct answer
COLOR_BG_ANSWER = HexColor('#F0FDF4')  # Light green bg


class ExamAnswerKeyGenerator:
    """Generate dedicated answer key PDF with answers + explanations"""
    
    def __init__(self, exam: ExamData, output_path: Optional[Path] = None):
        self.exam = exam
        self.output_path = output_path or self._default_output_path()
        self.c = None
        self.current_y = CONTENT_TOP
        self.page_number = 0
    
    def _default_output_path(self) -> Path:
        cert_id = f"{self.exam.course_code}_{self.exam.year}_{self.exam.exam_type}"
        cert_id = cert_id.replace('/', '_').replace('\\', '_').replace(' ', '_')
        return CERTIFICATES_DIR / f"EXAM_{cert_id}_ANSWER_KEY.pdf"
    
    def generate(self) -> Optional[Path]:
        """Main entry point"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.c = canvas.Canvas(
            str(self.output_path),
            pagesize=A4,
            pageCompression=1
        )
        
        # Metadata
        self.c.setTitle(f"UNIYO Answer Key - {self.exam.course_title}")
        self.c.setAuthor("UNIYO - University Made for YOU")
        self.c.setSubject(f"Answer Key - {self.exam.course_code}")
        
        # Draw cover page
        self._draw_cover_page()
        
        # Page break
        self.c.showPage()
        self.page_number += 1
        self._draw_header()
        self._draw_footer()
        self.current_y = CONTENT_TOP
        
        # Draw each section's answers
        for section in self.exam.sections:
            self._draw_section(section)
        
        # End page
        self._draw_end_page()
        
        self.c.save()
        return self.output_path
    
    # ============================================
    # HEADER / FOOTER
    # ============================================
    
    def _draw_header(self):
        """Page header with UNIYO branding"""
        c = self.c
        c.saveState()
        
        # Logo
        logo = self._load_logo()
        if logo:
            try:
                c.drawImage(logo, CONTENT_LEFT, PAGE_HEIGHT - 22 * mm, 
                           14 * mm, 14 * mm, preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # UNIYO
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 12)
        c.drawString(CONTENT_LEFT + 16 * mm, PAGE_HEIGHT - 14 * mm, "UNIYO")
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 6)
        c.drawString(CONTENT_LEFT + 16 * mm, PAGE_HEIGHT - 18 * mm, "Answer Key")
        
        # Answer Key Badge (top center)
        c.setFillColor(COLOR_GREEN)
        c.setFont('Helvetica-Bold', 10)
        c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 13 * mm, "🔑 ANSWER KEY")
        
        # Date (top right)
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        today = datetime.now().strftime('%d %b %Y')
        c.drawRightString(CONTENT_RIGHT, PAGE_HEIGHT - 12 * mm, today)
        
        # Divider
        c.setStrokeColor(COLOR_GREEN)
        c.setLineWidth(1)
        c.line(CONTENT_LEFT, PAGE_HEIGHT - 24 * mm, CONTENT_RIGHT, PAGE_HEIGHT - 24 * mm)
        
        # Course context
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        context = f"{self.exam.course_title} ({self.exam.course_code}) • {self.exam.exam_type.upper()} EXAM {self.exam.year} • ANSWER KEY"
        c.drawString(CONTENT_LEFT, PAGE_HEIGHT - 28 * mm, context)
        
        c.restoreState()
    
    def _draw_footer(self):
        """Page footer"""
        c = self.c
        c.saveState()
        
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, 12 * mm, CONTENT_RIGHT, 12 * mm)
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 7)
        page_info = f"UNIYO • Answer Key • Page {self.page_number} • {self.exam.course_code} {self.exam.year}"
        c.drawString(CONTENT_LEFT, 8 * mm, page_info)
        
        c.drawRightString(CONTENT_RIGHT, 8 * mm, "CONFIDENTIAL")
        
        c.restoreState()
    
    def _load_logo(self):
        """Load UNIYO logo"""
        from io import BytesIO
        
        logo_candidates = [
            BASE_DIR / 'static' / 'icons' / 'uniyo_favicon_32.svg',
            BASE_DIR / 'static' / 'icons' / 'uniyo_favicon_16.svg',
        ]
        
        for logo_path in logo_candidates:
            if not logo_path.exists():
                continue
            try:
                if logo_path.suffix.lower() == '.svg':
                    from core.exam_parsers.svg_utils import svg_to_png_bytes
                    svg_content = logo_path.read_text(encoding='utf-8')
                    png_buffer = svg_to_png_bytes(svg_content, output_width=400, background_color="white")
                    if png_buffer:
                        return ImageReader(png_buffer)
                else:
                    return ImageReader(str(logo_path))
            except:
                continue
        
        return None
    
    # ============================================
    # COVER PAGE
    # ============================================
    
    def _draw_cover_page(self):
        """Answer Key cover page"""
        self.page_number = 1
        c = self.c
        
        # Logo
        logo = self._load_logo()
        if logo:
            try:
                c.drawImage(logo, CONTENT_LEFT, PAGE_HEIGHT - 50 * mm, 25 * mm, 25 * mm,
                           preserveAspectRatio=True, mask='auto')
            except:
                pass
        
        # UNIYO
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 20)
        c.drawString(CONTENT_LEFT + 30 * mm, PAGE_HEIGHT - 38 * mm, "UNIYO")
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 9)
        c.drawString(CONTENT_LEFT + 30 * mm, PAGE_HEIGHT - 44 * mm, "University Made for YOU")
        
        # Date
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 8)
        today = datetime.now().strftime('%d %b %Y')
        c.drawRightString(CONTENT_RIGHT, PAGE_HEIGHT - 50 * mm, f"Printed: {today}")
        
        # Divider
        c.setStrokeColor(COLOR_GREEN)
        c.setLineWidth(1.5)
        c.line(CONTENT_LEFT, PAGE_HEIGHT - 55 * mm, CONTENT_RIGHT, PAGE_HEIGHT - 55 * mm)
        
        # Title
        y = PAGE_HEIGHT - 90 * mm
        
        c.setFillColor(COLOR_GREEN)
        c.setFont('Helvetica-Bold', 36)
        c.drawCentredString(PAGE_WIDTH / 2, y, "ANSWER KEY")
        
        y -= 12 * mm
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 18)
        c.drawCentredString(PAGE_WIDTH / 2, y, self.exam.university.upper())
        
        y -= 10 * mm
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(1.5)
        c.line(PAGE_WIDTH / 2 - 40 * mm, y, PAGE_WIDTH / 2 + 40 * mm, y)
        
        y -= 15 * mm
        c.setFillColor(COLOR_PRIMARY)
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(PAGE_WIDTH / 2, y, f"{self.exam.exam_type.upper()} EXAMINATION")
        
        # Exam details
        y -= 25 * mm
        details = [
            ("Subject:", self.exam.course_title),
            ("Course:", self.exam.course_code),
            ("Year:", str(self.exam.year)),
            ("Total Questions:", str(self.exam.total_questions)),
            ("Total Marks:", str(self.exam.total_marks)),
        ]
        
        for label, value in details:
            c.setFillColor(COLOR_TEXT_MUTED)
            c.setFont('Helvetica-Bold', 11)
            c.drawString(PAGE_WIDTH / 2 - 40 * mm, y, label)
            
            c.setFillColor(COLOR_TEXT)
            c.setFont('Helvetica', 11)
            c.drawString(PAGE_WIDTH / 2 - 5 * mm, y, value)
            
            y -= 8 * mm
        
        # Confidential warning box
        y -= 15 * mm
        box_height = 40 * mm
        box_y = y - box_height
        
        c.setFillColor(HexColor('#FEF3C7'))
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(1.5)
        c.roundRect(CONTENT_LEFT + 20 * mm, box_y, CONTENT_WIDTH - 40 * mm, box_height, 3 * mm,
                   fill=True, stroke=True)
        
        c.setFillColor(HexColor('#92400E'))
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(PAGE_WIDTH / 2, y - 10 * mm, "⚠️ CONFIDENTIAL DOCUMENT")
        
        c.setFillColor(HexColor('#78350F'))
        c.setFont('Helvetica', 10)
        c.drawCentredString(PAGE_WIDTH / 2, y - 18 * mm, "This answer key is for authorized users only.")
        c.drawCentredString(PAGE_WIDTH / 2, y - 24 * mm, "Do not share or distribute this document.")
        
        # Footer
        self._draw_footer()
    
    # ============================================
    # SECTION RENDERING
    # ============================================
    
    def _draw_section(self, section: Section):
        """Draw all answers for a section"""
        # Check space for section header
        header_height = 20 * mm
        if self._needs_new_page(header_height + 30 * mm):
            self._new_page()
        
        # Section header
        self._draw_section_header(section)
        self.current_y -= header_height
        
        # Track if we've already shown a continuation header on this page
        shown_continuation_on_page = False
        last_page_number = self.page_number
        
        # Draw each answer
        for question in section.questions:
            # Calculate height needed
            answer_height = self._calculate_answer_height(question)
            
            if self._needs_new_page(answer_height):
                self._new_page()
                shown_continuation_on_page = False  # Reset for new page
                last_page_number = self.page_number
            
            # Show continuation header only ONCE per new page
            if (last_page_number == self.page_number and 
                not shown_continuation_on_page and
                self.page_number > 1):
                # Only show continuation if we're NOT on the first page of the section
                self._draw_section_continuation(section)
                self.current_y -= 12 * mm
                shown_continuation_on_page = True
            
            # Draw the answer
            self._draw_answer(question)
    
    def _draw_section_header(self, section: Section):
        """Draw section header"""
        c = self.c
        y = self.current_y
        
        # Section title
        c.setFillColor(COLOR_SECONDARY)
        c.setFont('Helvetica-Bold', 13)
        c.drawString(CONTENT_LEFT, y - 8 * mm, section.title)
        
        # Underline
        c.setStrokeColor(COLOR_GOLD)
        c.setLineWidth(1)
        c.line(CONTENT_LEFT, y - 11 * mm, CONTENT_RIGHT, y - 11 * mm)
        
        # Count
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Oblique', 9)
        c.drawString(CONTENT_LEFT, y - 16 * mm, f"{section.get_question_count()} questions")
        
        # Divider
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, y - 20 * mm, CONTENT_RIGHT, y - 20 * mm)
    
    def _draw_section_continuation(self, section: Section):
        """Compact continuation header"""
        c = self.c
        y = self.current_y
        
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Bold', 10)
        c.drawString(CONTENT_LEFT, y - 5 * mm, f"{section.title} (continued)")
        
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.5)
        c.line(CONTENT_LEFT, y - 8 * mm, CONTENT_RIGHT, y - 8 * mm)
    
    # ============================================
    # ANSWER RENDERING
    # ============================================
    
    def _calculate_answer_height(self, question: Question) -> float:
        """Calculate height needed for this answer + explanation"""
        base = 20 * mm  # Question number + answer line
        
        # Explanation height
        if question.explanation:
            # ~70 chars per line at 9pt
            exp_lines = max(1, len(question.explanation) // 70 + 1)
            base += exp_lines * 5 * mm
        
        base += 5 * mm  # Bottom padding
        
        return base
    
    def _draw_answer(self, question: Question):
        """Draw answer + explanation for one question"""
        c = self.c
        y = self.current_y
        
        # ===== ANSWER LINE =====
        # Question number
        c.setFillColor(COLOR_TEXT)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(CONTENT_LEFT, y - 5 * mm, f"Q{question.number}.")
        
        # Correct answer (green, prominent)
        answer_text = question.correct_answer or "No answer provided"
        c.setFillColor(COLOR_GREEN)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(CONTENT_LEFT + 15 * mm, y - 5 * mm, f"✓  {answer_text}")
        
        y -= 10 * mm
        
        # ===== EXPLANATION =====
        if question.explanation:
            # Light green background box
            exp_lines = self._wrap_text(question.explanation, 'Helvetica', 9, CONTENT_WIDTH - 20 * mm)
            exp_height = len(exp_lines) * 4.5 * mm + 6 * mm
            
            c.setFillColor(COLOR_BG_ANSWER)
            c.setStrokeColor(HexColor('#BBF7D0'))
            c.setLineWidth(0.3)
            c.roundRect(
                CONTENT_LEFT + 5 * mm,
                y - exp_height + 2 * mm,
                CONTENT_WIDTH - 10 * mm,
                exp_height,
                2 * mm,
                fill=True,
                stroke=True
            )
            
            # Explanation label
            c.setFillColor(COLOR_GREEN)
            c.setFont('Helvetica-Bold', 8)
            c.drawString(CONTENT_LEFT + 8 * mm, y - 3 * mm, "Explanation:")
            
            # Explanation text
            c.setFillColor(COLOR_TEXT)
            c.setFont('Helvetica', 9)
            
            exp_y = y - 8 * mm
            for line in exp_lines:
                c.drawString(CONTENT_LEFT + 8 * mm, exp_y, line)
                exp_y -= 4.5 * mm
            
            y -= exp_height + 2 * mm
        
        # Divider between questions
        y -= 3 * mm
        c.setStrokeColor(COLOR_LINE)
        c.setLineWidth(0.3)
        c.line(CONTENT_LEFT, y, CONTENT_RIGHT, y)
        y -= 5 * mm
        
        self.current_y = y
    
    # ============================================
    # UTILITIES
    # ============================================
    
    def _new_page(self):
        """Start new page with header and footer"""
        if self.c is None:
            return
        self.c.showPage()
        self.page_number += 1
        self._draw_header()
        self._draw_footer()
        self.current_y = CONTENT_TOP
    
    def _needs_new_page(self, required_height: float) -> bool:
        """Check if content needs new page"""
        return (self.current_y - required_height) < CONTENT_BOTTOM
    
    def _wrap_text(self, text: str, font: str, size: int, max_width: float) -> list:
        """Wrap text into lines"""
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
    
    def _draw_end_page(self):
        """Draw end page"""
        self._new_page()
        
        c = self.c
        y = self.current_y - 80 * mm
        
        # Divider
        c.setStrokeColor(COLOR_GREEN)
        c.setLineWidth(2)
        c.line(PAGE_WIDTH / 2 - 60 * mm, y, PAGE_WIDTH / 2 + 60 * mm, y)
        
        # End text
        y -= 15 * mm
        c.setFillColor(COLOR_GREEN)
        c.setFont('Helvetica-Bold', 22)
        c.drawCentredString(PAGE_WIDTH / 2, y, "END OF ANSWER KEY")
        
        # Divider
        y -= 10 * mm
        c.setStrokeColor(COLOR_GREEN)
        c.setLineWidth(2)
        c.line(PAGE_WIDTH / 2 - 60 * mm, y, PAGE_WIDTH / 2 + 60 * mm, y)
        
        # Warning
        y -= 30 * mm
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica-Oblique', 11)
        c.drawCentredString(PAGE_WIDTH / 2, y, "This document contains exam answers.")
        
        y -= 7 * mm
        c.drawCentredString(PAGE_WIDTH / 2, y, "Please handle responsibly.")
        
        # Contact
        y -= 40 * mm
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont('Helvetica', 9)
        c.drawCentredString(PAGE_WIDTH / 2, y, "UNIYO - University Made for YOU")
        
        y -= 6 * mm
        c.drawCentredString(PAGE_WIDTH / 2, y, "📱 0923093416  •  💬 t.me/challengepr")


# ============================================
# PUBLIC FUNCTION
# ============================================

def generate_answer_key(exam: ExamData, output_path: Optional[Path] = None) -> Optional[Path]:
    """Generate dedicated answer key PDF"""
    try:
        generator = ExamAnswerKeyGenerator(exam, output_path)
        return generator.generate()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None
