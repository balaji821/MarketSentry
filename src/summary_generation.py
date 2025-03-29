from typing import Dict
from google import genai
from config import GOOGLE_GENAI_API_KEY
from pydantic import BaseModel

PROMPT_TEMPLATE = '''
The below are the Announcements from a Listed Indian Company. Summarize the important stuff from an inverstors' perspective.
Be crisp and clear. Use as few words as possible but make sure you cover the important points.
Provide your personal opinion on the announcement and how it might affect the stock price in the future.

Also, provide an overall observation, covering major lookouts from all the announcements.



{news_content}
'''

# OUTPUT JSON SCHEMA
class STOCK_NEWS(BaseModel):
    symbol: str
    announcement_summary: str
    personal_opinion: str

class NEWS(BaseModel):
    news_list: list[STOCK_NEWS]
    overall_observations: list[str]


client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)

def generate_summary(news: Dict[str, str]) -> Dict[str, str]:
    news_content = "\n\n".join(news.values())
    prompt = PROMPT_TEMPLATE.format(news_content=news_content)

    # with open('prompt.txt', 'w', encoding="utf-8") as f:
    #     f.write(prompt)

    config = {
        'response_mime_type': 'application/json',
        'response_schema': NEWS,
        'temperature': 0.1,
    }

    summary = get_model_response(prompt, config)
    return summary

def get_model_response(prompt: str, config: dict = None) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config=config
    )
    return response.text

if __name__ == "__main__":
    with open('prompt.txt', 'r') as f:
        prompt = f.read()
        # print(prompt)
        config = {
            'response_mime_type': 'application/json',
            'response_schema': NEWS,
            'temperature': 0.1,
        }
        print(get_model_response(prompt, config=config))