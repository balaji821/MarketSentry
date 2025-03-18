import requests
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import *
from io import BytesIO
from PyPDF2 import PdfReader
from google import genai

payload = {}
headers = {
'Referer': 'https://www.bseindia.com/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
}

def get_scrip_for_symbol(symbol):
    url = f'https://api.bseindia.com/BseIndiaAPI/api/PeerSmartSearch/w?Type=SS&text={symbol}'
    response = requests.request("GET", url, headers=headers, data=payload)
    results = response.text.split("</li>")
    pattern = "liclick\('([0-9]+)'"
    for result in results:
        if f"<strong>{symbol}</strong>" not in result:
            continue
        match = re.search(pattern, result)
        return match.group(1)
        


# Function to fetch PDF documents from BSE's site
def fetch_updates(symbol):
    scrip = get_scrip_for_symbol(symbol)
    print(f"Scrip for {symbol}: {scrip}")
    # today = datetime.now().strftime('%Y%m%d')
    today = '20250317'
    url = f'https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=-1&strPrevDate={today}&strScrip={scrip}&strSearch=P&strToDate={today}&strType=C&subcategory=-1'
    response = requests.request("GET", url, headers=headers, data=payload)
    url_prefix = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"
    if response.status_code == 200:
        data = response.json()
        updates = [{"headline":entry.get('HEADLINE'),"url":url_prefix + entry.get('ATTACHMENTNAME')} for entry in data.get('Table', []) if entry.get('NSURL') and entry.get('HEADLINE')]
        return updates
    return []

def get_pdf_text(url):
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        pdf_file = BytesIO(response.content)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    else:
        return None

def get_combined_pdf_text(updates):
    combined_text = ""
    for update in updates:
        text = get_pdf_text(update['url'])
        if text:
            combined_text += f'''
-------------------HEADLINE-----------------------
{update['headline']}
-------------------CONTENT------------------------
{text}
-------------------END OF CONTENT-----------------


'''
    return combined_text


# Function to summarize PDF documents using Google GenAI
def summarize_updates(updates):
    client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)
    combined_text = get_combined_pdf_text(updates)
    # print(f'Generating summary for:\n{combined_text}')
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f'''The below are the Announcements from a Listed Company. Summarize the important stuff from an inverstors' perspective.
            Be crisp and clear. Use as few words as possible but make sure you cover the important points. At the end, add a few lines conveying your opinion on the company's future prospects.
             
              ${combined_text}'''
        ]
    )
    # print(f'Summary response: {response}')
    return response.text

# Function to send email with the summary
def send_email(summary):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = 'Daily Market Summary'
    msg.attach(MIMEText(summary, 'plain'))

    server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
    server.starttls()
    server.login(EMAIL_SMTP_USERNAME, EMAIL_SMTP_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, text)
    server.quit()

# Main function to orchestrate the process
def main():
    for symbol in SYMBOLS:
        updates = fetch_updates(symbol)
        summary = summarize_updates(updates)
        send_email(summary)

# Test function to verify the scraped data
def test_fetch_pdfs():
    for symbol in SYMBOLS:
        updates = fetch_updates(scrip)
        # if updates:
        #     # print(f'Updates for {scrip}:\n{updates}')
        #     # print(f'Combined text for {scrip}:\n{get_combined_pdf_text(updates)}')
        #     print(f'Summary for {scrip}:\n{summarize_updates(updates)}')
        # else:
        #     print(f'No PDF URLs found for {scrip}')

if __name__ == '__main__':
    test_fetch_pdfs()
