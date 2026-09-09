"""
UNIYO LMS - Telegram Bot
Handles student support, payments, password reset, certificates, and announcements
"""

import telebot
import os
import sys
import secrets
from datetime import datetime, timedelta

sys.path.insert(0, '.')

from core.db import Database
from core.helpers import hash_password, verify_password, generate_reset_token

# ============================================
# BOT CONFIGURATION
# ============================================

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
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

if BOT_TOKEN and ':' in BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
else:
    bot = None
    print("⚠ Telegram bot not initialized - invalid token")

db = Database()
db.connect()

# Track pending password reset requests
# {chat_id: {'phone': phone_number, 'new_password': generated_password, 'step': 'confirm'}}
password_reset_sessions = {}

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
/forgotpassword - Reset your password
/mycertificates - View your certificates
/announcements - Latest announcements
/vip - VIP competition info
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

*Q: I forgot my password. What do I do?*
A: Send /forgotpassword and follow the instructions!

*Q: How do I see my certificates?*
A: Send /mycertificates to see all your certificates!
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
# PASSWORD RESET
# ============================================

@bot.message_handler(commands=['forgotpassword'])
def forgot_password_start(message):
    """Start password reset process"""
    bot.reply_to(message, """
🔐 *PASSWORD RESET*

Please send your registered phone number in this format:
`09XXXXXXXX` or `07XXXXXXXX`

Example: `0912345678`
""", parse_mode='Markdown')
    
    # Track state
    password_reset_sessions[message.chat.id] = {'step': 'awaiting_phone'}


@bot.message_handler(func=lambda message: message.chat.id in password_reset_sessions and password_reset_sessions[message.chat.id].get('step') == 'awaiting_phone')
def process_phone_for_reset(message):
    """Process phone number for password reset"""
    phone = message.text.strip()
    
    # Validate phone format
    if not phone.startswith('09') and not phone.startswith('07'):
        bot.reply_to(message, "❌ Invalid phone format. Please send `09XXXXXXXX` or `07XXXXXXXX`", parse_mode='Markdown')
        return
    
    if len(phone) != 10:
        bot.reply_to(message, "❌ Phone must be 10 digits. Please try again.")
        return
    
    # Check if student exists
    student = db.query_one("SELECT id, full_name, phone FROM students WHERE phone = ? AND is_active = 1", (phone,))
    
    if not student:
        bot.reply_to(message, """
❌ *No account found* with this phone number.

Please register first at the UNIYO app or website.
""", parse_mode='Markdown')
        del password_reset_sessions[message.chat.id]
        return
    
    # Generate new password
    new_password = secrets.token_urlsafe(6).replace('-', '').replace('_', '')[:8]
    # Ensure it meets requirements (at least 8 chars with letters and numbers)
    while len(new_password) < 8:
        new_password += secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789')
    
    # Save pending reset
    password_reset_sessions[message.chat.id] = {
        'step': 'confirm',
        'phone': phone,
        'student_id': student['id'],
        'full_name': student['full_name'],
        'new_password': new_password
    }
    
    bot.reply_to(message, f"""
👤 *Account Found:*

Name: {student['full_name']}
Phone: {phone}

🔑 *New Password:* `{new_password}`

Do you want to reset your password to this new password?

Reply *YES* to confirm or *NO* to cancel.
""", parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.chat.id in password_reset_sessions and password_reset_sessions[message.chat.id].get('step') == 'confirm')
def confirm_password_reset(message):
    """Confirm password reset"""
    session_data = password_reset_sessions.get(message.chat.id, {})
    response = message.text.strip().upper()
    
    if response == 'YES':
        # Update password
        new_hash = hash_password(session_data['new_password'])
        db.execute("UPDATE students SET password_hash = ? WHERE id = ?", (new_hash, session_data['student_id']))
        
        bot.reply_to(message, f"""
✅ *Password Reset Successful!*

Your new password is: `{session_data['new_password']}`

Please login with:
📱 Phone: {session_data['phone']}
🔑 Password: {session_data['new_password']}

*Recommendation:* Change your password after login in Settings.
""", parse_mode='Markdown')
        
        # Send notification to admin
        try:
            admin_msg = f"""
🔐 *PASSWORD RESET VIA BOT*

Student: {session_data['full_name']}
Phone: {session_data['phone']}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            bot.send_message(ADMIN_TELEGRAM_ID, admin_msg, parse_mode='Markdown')
        except:
            pass
        
        del password_reset_sessions[message.chat.id]
    
    elif response == 'NO':
        bot.reply_to(message, "❌ Password reset cancelled.")
        del password_reset_sessions[message.chat.id]
    
    else:
        bot.reply_to(message, "Please reply *YES* to confirm or *NO* to cancel.", parse_mode='Markdown')


# ============================================
# MY CERTIFICATES
# ============================================

@bot.message_handler(commands=['mycertificates'])
def my_certificates_start(message):
    """Start certificate lookup"""
    bot.reply_to(message, """
📜 *MY CERTIFICATES*

Please send your registered phone number to see your certificates.

Example: `0912345678`
""", parse_mode='Markdown')
    
    password_reset_sessions[message.chat.id] = {'step': 'awaiting_cert_phone'}


@bot.message_handler(func=lambda message: message.chat.id in password_reset_sessions and password_reset_sessions[message.chat.id].get('step') == 'awaiting_cert_phone')
def process_cert_phone(message):
    """Process phone number for certificate lookup"""
    phone = message.text.strip()
    
    student = db.query_one("SELECT id, full_name FROM students WHERE phone = ? AND is_active = 1", (phone,))
    
    if not student:
        bot.reply_to(message, "❌ No account found with this phone number.")
        del password_reset_sessions[message.chat.id]
        return
    
    # Get certificates
    certificates = db.query('''
        SELECT certificate_number, certificate_type, title, issue_date, rank
        FROM certificates
        WHERE student_id = ?
        ORDER BY issue_date DESC
        LIMIT 10
    ''', (student['id'],))
    
    if not certificates:
        bot.reply_to(message, f"""
📜 *CERTIFICATES for {student['full_name']}*

No certificates yet!

Complete worksheets or win VIP competitions to earn certificates!
""", parse_mode='Markdown')
    else:
        cert_text = f"📜 *CERTIFICATES for {student['full_name']}*\n\n"
        
        for i, cert in enumerate(certificates, 1):
            cert_type = cert['certificate_type']
            emoji = '🏆' if 'vip' in cert_type else '📜'
            title = cert['title']
            number = cert['certificate_number'][:20]
            issue_date = cert['issue_date'][:10]
            rank = f" Rank #{cert['rank']}" if cert.get('rank') else ''
            
            cert_text += f"{i}. {emoji} *{title}*\n"
            cert_text += f"   📋 No: `{number}`\n"
            cert_text += f"   📅 Issued: {issue_date}{rank}\n\n"
        
        cert_text += "\nTo view full certificates, login to the app."
        
        bot.reply_to(message, cert_text, parse_mode='Markdown')
    
    del password_reset_sessions[message.chat.id]


# ============================================
# ANNOUNCEMENTS
# ============================================

@bot.message_handler(commands=['announcements'])
def send_announcements(message):
    """Send latest announcements"""
    announcements = db.query('''
        SELECT title, message, priority, created_at
        FROM announcements
        WHERE is_active = 1
        ORDER BY created_at DESC
        LIMIT 5
    ''')
    
    if not announcements:
        bot.reply_to(message, "📢 *No announcements at this time.*", parse_mode='Markdown')
        return
    
    announce_text = "📢 *LATEST ANNOUNCEMENTS*\n\n"
    
    for i, announcement in enumerate(announcements, 1):
        title = announcement['title']
        msg = announcement['message'][:150]
        created = announcement['created_at'][:10]
        priority = announcement['priority']
        
        emoji = '🔴' if priority == 'high' else ('🟡' if priority == 'normal' else '🟢')
        
        announce_text += f"{i}. {emoji} *{title}*\n"
        announce_text += f"   {msg}\n"
        announce_text += f"   📅 {created}\n\n"
    
    bot.reply_to(message, announce_text, parse_mode='Markdown')


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
/forgotpassword - Reset password
/mycertificates - View certificates
/announcements - Latest announcements
""")


# ============================================
# ADMIN NOTIFICATION FUNCTIONS
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
