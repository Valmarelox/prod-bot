#!/usr/bin/env python3.12

import sys
from json import load as load_json
import requests


def main(config_path: str):
    with open(config_path) as f:
        config = load_json(f)
    api_url = config["api_url"]["value"]
    bot_token = config["bot_token"]["value"]
    secret_token = config["telegram_webhook_secret"]["value"]
    res = requests.post(f"https://api.telegram.org/bot{bot_token}/setWebhook", data={"url": api_url, "secret_token": secret_token})
    assert res.status_code == 200
    assert res.json()["ok"] == True


if __name__ == '__main__':
    main(sys.argv[1])