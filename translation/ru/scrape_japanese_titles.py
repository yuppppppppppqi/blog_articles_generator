import requests
from bs4 import BeautifulSoup

URLS = [
    "https://my-bangkok-life.com/ja/",
    "https://my-bangkok-life.com/ja/page/2/",
    "https://my-bangkok-life.com/ja/page/3/",
]

OUTPUT_PATH = "translation/ru/japanese_titles.txt"

def extract_titles_from_url(url):
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    # 記事タイトルはh2タグで、特定のクラスが付いている場合もあるが、今回はh2全取得
    titles = [h2.get_text(strip=True) for h2 in soup.find_all("h2")]
    return titles

title_set = set()
for url in URLS:
    titles = extract_titles_from_url(url)
    for t in titles:
        # 記事タイトルっぽいものだけフィルタ（「おすすめ」や「フットマッサージ」などを含むもの）
        if "フットマッサージ" in t and "おすすめ" in t:
            title_set.add(t)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for title in sorted(title_set):
        f.write(title + "\n")

print(f"{OUTPUT_PATH} に日本語記事タイトルを保存しました。") 