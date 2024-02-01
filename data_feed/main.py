import os
import schedule

REQUEST_PATH = f'{os.environ["CRYPTOPANIC_URL"]}/?auth_token={os.environ["CRYPTOPANIC_API_TOKEN"]}'

if __name__=="__main__":
