# MarketSentry

MarketSentry is a Python project that fetches daily market updates from BSE's site, summarizes the updates using the Google GenAI API, and sends the summarized updates via email.

## Features

- Fetches PDF documents from BSE's site for specified stock scrips.
- Summarizes the PDF documents using the Google GenAI API.
- Sends the summarized updates via email.

## Requirements

- Python 3.9+
- `requests` library
- `smtplib` library
- `google-genai` library
- `beautifulsoup4` library
- `PyPDF2` library

## Installation

1. Clone the repository:

```bash
$ git clone <repository_url>
$ cd MarketSentry
```

2. Create a virtual environment and activate it:

```bash
$ python -m venv .venv
$ .venv\Scripts\activate
```

3. Install the required libraries:

```bash
$ pip install -r requirements.txt
```

## Configuration

Update the `config.py` file with your API keys, email configuration details, and stock scrips:

```python
# config.py

SYMBOLS = [
    'ASHOKLEY',  # ASHOK LEYLAND
    'CIPLA',  # CIPLA
    'DRREDDY',  # DR. REDDY'S LABORATORIES
    'FEDERALBNK',  # FEDERAL BANK
    'IDFCFIRSTB',  # IDFC FIRST BANK
    'INDUSINDBK',  # INDUSIND BANK
    'INFY',  # INFOSYS
    'ITC',  # ITC LIMITED
    'ITCHOTELS',  # ITC HOTELS
    'JYOTHYLAB',  # JYOTHY LABS
    'KTKBANK',  # KARNATAKA BANK
    'MANAPPURAM',  # MANAPPURAM FINANCE
    'MHRIL',  # MAHINDRA HOLIDAYS & RESORTS
    'MUTHOOTFIN',  # MUTHOOT FINANCE
    'NATCOPHARM',  # NATCO PHARMA
    'SOUTHBANK',  # SOUTH INDIAN BANK
    'SUNPHARMA',  # SUN PHARMACEUTICALS
    'TATACHEM',  # TATA CHEMICALS
    'TATACONSUM',  # TATA CONSUMER PRODUCTS
    'TATAMOTORS',  # TATA MOTORS
    'TATASTEEL',  # TATA STEEL
    'TCS',  # TATA CONSULTANCY SERVICES
    'TMB',  # TAMILNAD MERCANTILE BANK
    'ZYDUSLIFE'  # ZYDUS LIFESCIENCES
]

GOOGLE_GENAI_API_KEY = 'your_google_genai_api_key'
EMAIL_SENDER = 'your_email@example.com'
EMAIL_RECIPIENTS = ['recipient1@example.com', 'recipient2@example.com']
EMAIL_SMTP_SERVER = 'smtp.example.com'
EMAIL_SMTP_PORT = 587
EMAIL_SMTP_USERNAME = 'your_smtp_username'
EMAIL_SMTP_PASSWORD = 'your_smtp_password'
```

## Usage

To run the script and receive daily market summaries, use the following command:

```bash
$ python src/main.py
```

## Testing

To test the scraped data, you can use the test function provided in the `market_sentry.py` script:

```bash
$ python src/main.py
```

This will fetch the PDF URLs for the specified scrips and print them.

## License

This project is licensed under the MIT License.