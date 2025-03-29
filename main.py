from src.news_collection import fetch_watchlist_updates, constructWatchlist
from src.summary_generation import generate_summary
from src.mailing_module import send_mail
from src.config import logger
import json

WATCHLIST : dict[str, str] = json.loads(open('watchlist.json', 'r').read())

def event_handler(event, context):
    # date = datetime.datetime.now().strftime('%d%m')
    # if event['pwd'] != f'b@|@j1{date}':
    #     return {'statusCode': 401, 'message': 'Unauthorized'}

    watchlist = WATCHLIST
    mail = True
    if event and 'list' in event and event['list']:
        watchlist = constructWatchlist(event['list'].split(','), WATCHLIST)
    if event and 'ignore_mail' in event and event['ignore_mail']:
        mail = False
    
    updates = fetch_watchlist_updates(watchlist)
    # print(updates)
    summary = generate_summary(updates)
    summary = json.loads(summary)
    print(summary)
    if mail:
        send_mail(summary)
        logger.info('Sent emails successfully')
    
    return summary

if __name__ == "__main__":
    event_handler(None, None)