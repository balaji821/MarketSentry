from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_RECIPIENTS, EMAIL_SENDER, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD
import json

def send_mail(summary: dict):    
    date = datetime.now().strftime('%Y-%m-%d')

    #DEBUG
    # with open('summary.json', 'w', encoding="utf-8") as f:
    #     f.write(json.dumps(summary, indent=4))

    overall_observations = []
    if 'overall_observations' in summary:
        overall_observations = summary['overall_observations']

    html_text = ""
    if 'news_list' in summary:
        news_list = summary['news_list']
        for news in news_list:
            symbol = news['symbol']
            announcement_summary = news['announcement_summary']
            personal_opinion = news['personal_opinion']
            html_text += f"<h2>{symbol}</h2>\n"
            html_text += f"<strong>Announcement Summary:</strong><br>\n\t{announcement_summary}<br><br>\n"
            html_text += f"<strong>Personal Opinion:</strong><br>\n\t{personal_opinion}<br><br><hr><br>\n\n\n"

    if 'overall_observations' in summary:
        overall_observations = summary['overall_observations']
        html_text += "<strong>Overall Observations:</strong><br>\n\t"
        html_text += "<ul>\n"
        for observation in overall_observations:
            html_text += f"<li>{observation}</li>\n"
        html_text += "</ul>\n"
    
    # with open('htmltext.html', 'w', encoding="utf-8") as f:
    #     f.write(html_text)

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
    with open('summary.json', 'r', encoding="utf-8") as f:
        send_mail(json.loads(f.read()))