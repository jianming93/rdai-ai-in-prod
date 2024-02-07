import os
import time
import logging

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)
import schedule
import requests
import chromadb

REQUEST_PATH = (
    f'{os.environ["CRYPTOPANIC_URL"]}/?auth_token={os.environ["CRYPTOPANIC_API_TOKEN"]}'
)
CLIENT = chromadb.HttpClient(
    host=os.environ["VECTOR_STORE_URL"], port=os.environ["VECTOR_STORE_PORT"]
)


def scheduled_feed_request():
    news_payload_response = requests.get(REQUEST_PATH)
    news_payload_response.raise_for_status()
    logging.info(news_payload_response.json())


if __name__ == "__main__":
    schedule.every(int(os.environ["REQUEST_INTERVAL"])).seconds.do(
        scheduled_feed_request
    )
    while True:
        schedule.run_pending()
        time.sleep(1)
