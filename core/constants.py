"""
UNIYO LMS - Constants & Static Data
"""

UNIVERSITY_SHORT_NAMES = {
    "Addis Ababa University": "AAU",
    "Addis Ababa Science and Technology University": "AASTU",
    "Adama Science and Technology University": "ASTU",
    "Arba Minch University": "AMU",
    "Bahir Dar University": "BDU",
    "Debre Berhan University": "DBU",
    "Debre Markos University": "DMU",
    "Dire Dawa University": "DDU",
    "Gondar University": "UOG",
    "Hawassa University": "HU",
    "Haramaya University": "HRU",
    "Jigjiga University": "JJU",
    "Jimma University": "JU",
    "Mekelle University": "MU",
    "Wollega University": "WU",
    "Wollo University": "WLU",
    "Wolaita Sodo University": "WSU",
    "Mizan-Tepi University": "MTU",
    "Ambo University": "AU",
    "Assosa University": "ASU",
    "Bule Hora University": "BHU",
    "Dilla University": "DU",
    "Gambella University": "GU",
    "Kotebe University of Education": "KUE",
    "Mettu University": "MEU",
    "Nekemte University": "NU",
    "Raya University": "RU",
    "Samara University": "SU",
    "Wachamo University": "WCU",
    "Werabe University": "WRU",
    "Wolkite University": "WKU",
    "Yeka University": "YU",
    "Ethiopian Technical University": "ETU",
    "Aksum University": "AKU",
    "Debark University": "DBK",
    "Dembi Dolo University": "DDU",
    "Fitche University": "FU",
    "Injibara University": "IU",
    "Jinka University": "JKU",
    "Kebri Dehar University": "KDU",
    "Madda Walabu University": "MWU",
    "Oda Bultum University": "OBU",
    "Robe University": "RBU",
    "Salale University": "SLU",
    "Shire University": "SHU",
    "Wachemo University": "WCH",
    "Woldia University": "WDU",
}

UNIVERSITIES_LIST = sorted(UNIVERSITY_SHORT_NAMES.keys())

COURSES = [
    {"code": "Econ1011", "title": "Economics", "credit_hours": 3, "semester": 1, "stream": "Common"},
    {"code": "FLEn1011", "title": "Communicative English Language Skills I", "credit_hours": 3, "semester": 1, "stream": "Common"},
    {"code": "FLEn1012", "title": "Communicative English Language Skills II", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "GlTr1012", "title": "Global Trends", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "Anth1012", "title": "Social Anthropology", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "Hist1012", "title": "History of Ethiopia and the Horn", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "GeES1011", "title": "Geography of Ethiopia and the Horn", "credit_hours": 3, "semester": 1, "stream": "Common"},
    {"code": "EmTe1012", "title": "Introduction to Emerging Technologies", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "SPsc1011", "title": "Physical Fitness", "credit_hours": 2, "semester": 1, "stream": "Common"},
    {"code": "LoCT1011", "title": "Logic and Critical Thinking", "credit_hours": 3, "semester": 1, "stream": "Common"},
    {"code": "Psych1011", "title": "General Psychology", "credit_hours": 3, "semester": 1, "stream": "Common"},
    {"code": "MCiE1012", "title": "Moral and Civic Education", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "Incl1012", "title": "Inclusiveness", "credit_hours": 2, "semester": 2, "stream": "Common"},
    {"code": "MGMT1012", "title": "Entrepreneurship", "credit_hours": 3, "semester": 2, "stream": "Common"},
    {"code": "Math1012", "title": "Mathematics for Natural Sciences", "credit_hours": 4, "semester": 1, "stream": "Natural"},
    {"code": "Math1011", "title": "Mathematics for Social Sciences", "credit_hours": 3, "semester": 1, "stream": "Social"},
]

PAYMENT_CONFIG = {
    "amount": 200.00,
    "currency": "ETB",
    "methods": {
        "telebirr": {"account": "0923093416", "name": "challengepr"},
        "cbe": {"account": "1000536461381", "name": "Chalachew Agegn"},
        "abyssinia": {"account": "Available on request", "name": "Chalachew Agegn"},
        "abay": {"account": "Available on request", "name": "Chalachew Agegn"},
        "awash": {"account": "Available on request", "name": "Chalachew Agegn"}
    },
    "contact": "@challengepr",
    "telegram_url": "https://t.me/challengepr"
}

ADMIN_ROLES = {
    "super_admin": {
        "label": "Super Admin",
        "permissions": {
            "manage_admins": True, "manage_content": True, "verify_payments": True,
            "manage_vip": True, "issue_certificates": True, "view_analytics": True,
            "manage_students": True, "send_announcements": True,
        }
    },
    "content_manager": {
        "label": "Content Manager",
        "permissions": {
            "manage_admins": False, "manage_content": True, "verify_payments": False,
            "manage_vip": True, "issue_certificates": False, "view_analytics": False,
            "manage_students": False, "send_announcements": True,
        }
    },
    "payment_verifier": {
        "label": "Payment Verifier",
        "permissions": {
            "manage_admins": False, "manage_content": False, "verify_payments": True,
            "manage_vip": False, "issue_certificates": False, "view_analytics": False,
            "manage_students": True, "send_announcements": False,
        }
    }
}

SUPPORTED_LANGUAGES = {
    "en": "English",
    "am": "አማርኛ",
    "om": "Afaan Oromoo",
}

FONT_SIZES = {"small": 14, "medium": 16, "large": 18, "xlarge": 20, "xxlarge": 22}

VIP_DURATIONS = [3, 8, 12, 24]

GRADE_MAPPING = {
    (95, 100): "A+", (90, 94): "A", (85, 89): "A-",
    (80, 84): "B+", (70, 79): "B", (60, 69): "C+",
    (50, 59): "C", (0, 49): "F"
}

def get_letter_grade(percentage):
    for (min_score, max_score), grade in GRADE_MAPPING.items():
        if min_score <= percentage <= max_score:
            return grade
    return "F"
