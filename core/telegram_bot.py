"""
UNIYO LMS - Telegram Bot
Handles student support, payments, and notifications
"""

import telebot
import os
import sys
from datetime import datetime

sys.path.insert(0, '.')

from core.db import Database

# ============================================
# BOT CONFIGURATION
# ============================================

# ⚠️ REPLACE WITH YOUR BOT TOKEN FROM BOTFATHER
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Your admin Telegram user ID (get from @userinfobot)
ADMIN_TELEGRAM_ID = os.environ.get("TELEGRAM_ADMIN_ID", "")

# Payment information
PAYMENT_INFO = """
💳 PAYMENT OPTIONS:

📱 Telebirr: 0923093416
   Name: challengepr

🏦 CBE: 1000536461381
   Name: Chalachew Agegn

After payment, send:
1. Your transaction number
2. Your phone number
3. Screenshot (optional)

You'll be approved within 24 hours!
"""

# ============================================
# BOT INITIALIZATION
# ============================================

# Only initialize if token is valid
if BOT_TOKEN and ':' in BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
else:
    bot = None
    print("⚠ Telegram bot not initialized - invalid token")
db = Database()
db.connect()

# ============================================
# BOT COMMANDS
# ============================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Welcome message when user starts bot"""
    welcome_text = f"""
🎓 *Welcome to UNIYO!*

Hi {message.chat.first_name}! 👋

UNIYO is Ethiopia's #1 Freshman Learning Platform!

*What we offer:*
✅ Complete lessons for all 16 courses
✅ Practice questions with explanations
✅ Weekly VIP Competition
✅ Certificates for top performers
✅ Offline access

*Commands:*
/start - Welcome message
/price - Payment information
/courses - List of courses
/faq - Frequently asked questions
/contact - Contact admin

*How to get started:*
1. Send /price for payment info
2. Pay via Telebirr or CBE
3. Send your transaction number here
4. Get approved and start learning!
"""

    bot.reply_to(message, welcome_text, parse_mode='Markdown')


@bot.message_handler(commands=['price'])
def send_price(message):
    """Send payment information"""
    bot.reply_to(message, PAYMENT_INFO, parse_mode='Markdown')


@bot.message_handler(commands=['courses'])
def send_courses(message):
    """Send course list"""
    courses_text = """
📚 *ALL 16 FRESHMAN COURSES:*

1. Economics (Econ1011)
2. Logic & Critical Thinking (LoCT1011)
3. Math for Natural Sciences (Math1012)
4. Math for Social Sciences (Math1011)
5. Communicative English I (FLEn1011)
6. Communicative English II (FLEn1012)
7. Global Trends (GlTr1012)
8. Social Anthropology (Anth1012)
9. History of Ethiopia (Hist1012)
10. Geography of Ethiopia (GeES1011)
11. Emerging Technologies (EmTe1012)
12. Physical Fitness (SPsc1011)
13. General Psychology (Psych1011)
14. Moral & Civic Education (MCiE1012)
15. Inclusiveness (Incl1012)
16. Entrepreneurship (MGMT1012)

*ALL for only 200 ETB!*
"""

    bot.reply_to(message, courses_text, parse_mode='Markdown')


@bot.message_handler(commands=['faq'])
def send_faq(message):
    """Send FAQ"""
    faq_text = """
❓ *FREQUENTLY ASKED QUESTIONS:*

*Q: How much does UNIYO cost?*
A: 200 ETB one-time payment for ALL courses!

*Q: How do I pay?*
A: Telebirr (0923093416) or CBE (1000536461381)

*Q: How do I access after payment?*
A: Send your transaction number here!

*Q: Does it work offline?*
A: YES! Download lessons and study anywhere!

*Q: Can I get a certificate?*
A: YES! Complete worksheets or win VIP competitions!
"""

    bot.reply_to(message, faq_text, parse_mode='Markdown')


@bot.message_handler(commands=['contact'])
def send_contact(message):
    """Send contact information"""
    contact_text = """
📞 *CONTACT US:*

Telegram: @challengepr
Bot: @UNIYO_Support_Bot

For payment confirmation or support,
send your transaction number here!
"""

    bot.reply_to(message, contact_text, parse_mode='Markdown')


@bot.message_handler(commands=['vip'])
def send_vip_info(message):
    """Send VIP competition information"""
    vip_text = """
🏆 *VIP WEEKLY COMPETITION!*

EVERY SUNDAY!

*Top 5 Monthly Winners:*
🥇 1st: GOLD Certificate
🥈 2nd: SILVER Certificate
🥉 3rd: BRONZE Certificate
🏆 4th & 5th: DISTINCTION

*How to participate:*
1. Join UNIYO Premium
2. Login every Sunday
3. Take the VIP exam
4. Compete with students nationwide!

Ready to WIN? 🏆
"""

    bot.reply_to(message, vip_text, parse_mode='Markdown')


# ============================================
# HANDLE PAYMENT CONFIRMATIONS
# ============================================

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle all other messages (likely payment confirmations)"""
    
    text = message.text or ""
    
    # Check if message looks like a transaction number
    if any(word in text.upper() for word in ['TXN', 'TRANSACTION', 'PAID', 'SENT']):
        # Forward to admin
        admin_notification = f"""
💰 *NEW PAYMENT SUBMISSION*

From: {message.chat.first_name} (@{message.chat.username or 'no_username'})
User ID: {message.chat.id}

Message:
{text}
"""

        bot.send_message(ADMIN_TELEGRAM_ID, admin_notification, parse_mode='Markdown')
        
        bot.reply_to(message, """
✅ *Payment Received!*

Thank you for your payment!
Your submission has been forwarded to our admin.

⏳ You'll be approved within 24 hours.

If you need faster approval, contact: @challengepr
""", parse_mode='Markdown')
    
    else:
        # Generic response
        bot.reply_to(message, """
Thank you for your message! 🙏

For payment confirmation, please send:
1. Your transaction number
2. Your phone number

Or use these commands:
/start - Welcome
/price - Payment info
/courses - Course list
/faq - FAQ
/contact - Contact admin
""")


# ============================================
# ADMIN NOTIFICATION FUNCTION
# ============================================

def notify_admin_payment(student_name, phone, transaction_number, method):
    """Notify admin about new payment"""
    try:
        message = f"""
💰 *NEW PAYMENT NOTIFICATION*

Student: {student_name}
Phone: {phone}
Method: {method}
Transaction: {transaction_number}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        bot.send_message(ADMIN_TELEGRAM_ID, message, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Error sending admin notification: {e}")
        return False


def notify_student_approved(telegram_id, student_name):
    """Notify student that they're approved"""
    try:
        message = f"""
✅ *PREMIUM ACCESS APPROVED!*

Congratulations {student_name}! 🎉

Your UNIYO Premium access is now ACTIVE!

You can now access:
📚 All 16 courses
📝 All practice questions
🏆 VIP competitions

Happy studying! 🎓
"""
        bot.send_message(telegram_id, message, parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"Error sending student notification: {e}")
        return False


# ============================================
# RUN BOT
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("UNIYO Telegram Bot Starting...")
    print("=" * 50)
    print("Bot is running... Press Ctrl+C to stop")
    print("=" * 50)
    
    bot.polling(none_stop=True)
