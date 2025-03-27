from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_RECIPIENTS, EMAIL_SENDER, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD
from json2html import *
import json

def send_mail(summary: dict):    
    date = datetime.now().strftime('%Y-%m-%d')

    overall_observations = []
    if 'overall_observations' in summary:
        overall_observations = summary['overall_observations']

    html_text = json2html.convert(summary['news_list'])

    with open('htmltext.html', 'w', encoding="utf-8") as f:
        f.write(html_text)

    html_text = html_text + "\n\n<strong>Overal Observations:</strong>\n\t" + ("\n".join(overall_observations))

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['Subject'] = f'[{date}] MarketSentry Daily Digest'
    msg['To'] = ', '.join(EMAIL_RECIPIENTS)
    msg.attach(MIMEText(html_text, 'html'))

    server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENTS, text)
    server.quit()


if __name__ == '__main__':
    with open('news.json', 'r') as f:
        send_mail(json.loads(f.read()))