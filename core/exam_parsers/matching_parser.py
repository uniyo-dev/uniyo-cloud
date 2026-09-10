"""
UNIYO LMS - Matching Question Parser
Handles various HTML formats for matching questions
"""

import re
from bs4 import BeautifulSoup
from typing import List, Tuple


def parse_matching_question(elem) -> Tuple[List[str], List[str]]:
    """
    Parse matching question from HTML element.
    
    Supports multiple formats:
    
    Format 1: Structured columns
        <div class="column-a">
            <li>Adam Smith</li>
            ...
        </div>
        <div class="column-b">
            <li>Welfare economics</li>
            ...
        </div>
    
    Format 2: Table-based
        <table>
            <tr><th>Column A</th><th>Column B</th></tr>
            <tr><td>Adam Smith</td><td>Welfare economics</td></tr>
            ...
        </table>
    
    Format 3: Lists
        <ol class="left-column">
            <li>Adam Smith</li>
        </ol>
        <ol class="right-column">
            <li>Welfare economics</li>
        </ol>
    
    Returns:
        (column_a, column_b) - Two lists of strings
    """
    soup = BeautifulSoup(str(elem), 'html.parser')
    
    column_a = []
    column_b = []
    
    # ===== Format 1: Structured divs =====
    col_a_elem = soup.find(class_=re.compile(r'column-a|col-a|left-col|column_a', re.I))
    col_b_elem = soup.find(class_=re.compile(r'column-b|col-b|right-col|column_b', re.I))
    
    if col_a_elem:
        column_a = _extract_items(col_a_elem)
    
    if col_b_elem:
        column_b = _extract_items(col_b_elem)
    
    # ===== Format 2: Table-based =====
    if not column_a or not column_b:
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            col_a_from_table = []
            col_b_from_table = []
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Skip header row
                    text_a = cells[0].get_text(strip=True)
                    text_b = cells[1].get_text(strip=True)
                    
                    if not any(x in text_a.lower() for x in ['column a', 'col a', 'item', 'a.']):
                        col_a_from_table.append(text_a)
                        col_b_from_table.append(text_b)
            
            if col_a_from_table and not column_a:
                column_a = col_a_from_table
            if col_b_from_table and not column_b:
                column_b = col_b_from_table
    
    # ===== Format 3: Lists =====
    if not column_a or not column_b:
        lists = soup.find_all(['ol', 'ul'])
        if len(lists) >= 2:
            first_list = lists[0]
            second_list = lists[1]
            
            list_a = _extract_items(first_list)
            list_b = _extract_items(second_list)
            
            if not column_a and list_a:
                column_a = list_a
            if not column_b and list_b:
                column_b = list_b
    
    # ===== Format 4: Inline matching with numbers and letters =====
    if not column_a or not column_b:
        full_text = soup.get_text()
        # Try to find "1. X ___ A. Y" format
        pairs = re.findall(r'(\d+)\.\s+(.+?)\s+_{2,}\s+([A-Z])\.\s+(.+?)(?=\d+\.|$)', full_text, re.DOTALL)
        if pairs:
            for num, text_a, letter, text_b in pairs:
                column_a.append(text_a.strip())
                column_b.append(text_b.strip())
    
    return column_a, column_b


def _extract_items(elem) -> List[str]:
    """Extract list items from element"""
    items = []
    
    # Try list items first
    for li in elem.find_all('li'):
        text = li.get_text(strip=True)
        # Remove number/letter prefix
        text = re.sub(r'^[\dA-Z][\.\)]\s*', '', text)
        if text:
            items.append(text)
    
    # If no list items, try paragraphs or divs
    if not items:
        for p in elem.find_all(['p', 'div'], recursive=False):
            text = p.get_text(strip=True)
            text = re.sub(r'^[\dA-Z][\.\)]\s*', '', text)
            if text:
                items.append(text)
    
    return items


def parse_matching_from_html(elem) -> dict:
    """
    Full parser for matching questions.
    
    Returns:
        dict with 'column_a' and 'column_b' keys
    """
    col_a, col_b = parse_matching_question(elem)
    return {
        'column_a': col_a,
        'column_b': col_b
    }
