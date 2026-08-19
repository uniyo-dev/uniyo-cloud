"""
UNIYO LMS - Input Validators
"""

import re

def validate_phone(phone):
    if not phone:
        return False, "Phone number is required"
    phone = phone.strip().replace(' ', '').replace('-', '')
    pattern = r'^(09|07)[0-9]{8}$'
    if not re.match(pattern, phone):
        return False, "Phone must start with 09 or 07 followed by 8 digits"
    return True, phone

def validate_password(password):
    if not password:
        return False, "Password is required"
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter (A-Z or a-z)"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number (0-9)"
    return True, password

def validate_name(name, field_name="Name"):
    if not name:
        return False, f"{field_name} is required"
    name = name.strip()
    if len(name) < 2:
        return False, f"{field_name} must be at least 2 characters"
    if not re.match(r'^[A-Za-z\s]+$', name):
        return False, f"{field_name} can only contain letters"
    return True, name

def validate_telegram_username(username):
    if not username:
        return True, None
    username = username.strip().replace('@', '')
    if not re.match(r'^[A-Za-z0-9_]{5,}$', username):
        return False, "Invalid Telegram username"
    return True, username

def validate_email(email):
    if not email:
        return True, None
    email = email.strip()
    if not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        return False, "Invalid email address"
    return True, email

def validate_transaction_number(transaction_number):
    if not transaction_number:
        return False, "Transaction number is required"
    transaction_number = transaction_number.strip().upper()
    if len(transaction_number) < 5:
        return False, "Transaction number must be at least 5 characters"
    return True, transaction_number

def validate_amount(amount):
    try:
        amount = float(amount)
        if amount <= 0:
            return False, "Amount must be greater than zero"
        return True, amount
    except:
        return False, "Invalid amount"

def validate_registration(data):
    errors = []
    valid, first_name = validate_name(data.get('first_name'), "First name")
    if not valid:
        errors.append(first_name)
    valid, father_name = validate_name(data.get('father_name'), "Father name")
    if not valid:
        errors.append(father_name)
    if data.get('sex') not in ['Male', 'Female']:
        errors.append("Please select your sex")
    valid, phone = validate_phone(data.get('phone'))
    if not valid:
        errors.append(phone)
    if not data.get('university'):
        errors.append("Please select your university")
    if data.get('stream') not in ['Natural', 'Social']:
        errors.append("Please select your stream")
    valid, password = validate_password(data.get('password'))
    if not valid:
        errors.append(password)
    if data.get('password') != data.get('confirm_password'):
        errors.append("Passwords do not match")
    if data.get('telegram_username'):
        valid, telegram = validate_telegram_username(data.get('telegram_username'))
        if not valid:
            errors.append(telegram)
    if data.get('email'):
        valid, email = validate_email(data.get('email'))
        if not valid:
            errors.append(email)
    return len(errors) == 0, errors
