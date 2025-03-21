import os

# Configuration file for MarketSentry

# List of stocks to monitor
SYMBOLS = [
    "ASHOKLEY",
    "CIPLA",
    "DRREDDY",
    "FEDERALBNK",
    "IDFCFIRSTB",
    "INDUSINDBK",
    "INFY",
    "ITC",
    "ITCHOTELS",
    "JYOTHYLAB",
    "KTKBANK",
    "MANAPPURAM",
    "MHRIL",
    "MUTHOOTFIN",
    "NATCOPHARM",
    "SOUTHBANK",
    "SUNPHARMA",
    "TATACHEM",
    "TATACONSUM",
    "TATAMOTORS",
    "TATASTEEL",
    "TCS",
    "TMB",
    "ZYDUSLIFE"
]

# API keys and other configurations
GOOGLE_GENAI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
EMAIL_SENDER = 'balaji2000001@gmail.com'
EMAIL_RECIPIENTS = ['balajis8201@gmail.com','balaji.srinis@zohocorp.com']
EMAIL_SMTP_SERVER = 'smtp.gmail.com'
EMAIL_SMTP_PORT = 587
EMAIL_SMTP_USERNAME = 'balaji2000001'
EMAIL_SMTP_PASSWORD = os.getenv('GOOGLE_SMTP_PASS')
