import os
import re
import json
import html
import urllib.request
from html.parser import HTMLParser

URL = "https://goldapple.ru/19000116114-resveratrol-345na-intensive-repair-cream"
STATE_FILE = ".cache/status.json"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def fetch_page():
    req = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError("Страница недоступна")
        return response.read().decode("utf-8", errors="replace")


def check_stock(source):
    parser = TextExtractor()
    parser.feed(source)
    text = " ".join(parser.parts).lower()
    text = re.sub(r"\s+", " ", html.unescape(text))

    if "19000116114" not in text or "345 relief cream" not in text:
        raise RuntimeError("Не удалось подтвердить нужный товар")

    if "нет в наличии" in text:
        return "out_of_stock"

    buy_markers = ("в корзину", "добавить в корзину")
    if any(marker in text for marker in buy_markers):
        return "in_stock"

    raise RuntimeError("Не удалось достоверно определить наличие")


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    data = json.dumps({
        "chat_id": chat_id,
        "text": message
    }).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        result = json.loads(response.read())
        if not result.get("ok"):
            raise RuntimeError("Telegram не принял сообщение")


def main():
    os.makedirs(".cache", exist_ok=True)

    previous = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            previous = json.load(f).get("status")

    current = check_stock(fetch_page())

    if current == "in_stock" and previous != "in_stock":
        send_telegram(
            "🎉 DR. ALTHEA 345 СНОВА В НАЛИЧИИ!\n\n"
            "Проверь товар прямо сейчас:\n" + URL
        )

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": current}, f)

    print("Проверка завершена:", current)


if __name__ == "__main__":
    main()
