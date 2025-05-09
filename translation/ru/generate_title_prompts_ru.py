import os
import csv
import re
from datetime import datetime

# translation/ru/ 配下に保存
RU_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "title_prompts")
os.makedirs(RU_OUTPUT_DIR, exist_ok=True)
JP_TITLES_PATH = os.path.join(os.path.dirname(__file__), "japanese_titles.txt")
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")

# 日本語タイトルを読み込む
def load_japanese_titles():
    if not os.path.exists(JP_TITLES_PATH):
        return []
    with open(JP_TITLES_PATH, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# 年号（例: 2025）を抽出（参考タイトルから取得、なければ今年を使う）
def extract_year(title):
    m = re.search(r"20[0-9]{2}", title)
    if m:
        return m.group(0)
    return str(datetime.now().year)

jp_titles = load_japanese_titles()

# プロジェクトディレクトリを列挙
project_dirs = [d for d in os.listdir(PROJECT_ROOT) if d.endswith("_2025") and os.path.isdir(os.path.join(PROJECT_ROOT, d))]

for project in sorted(project_dirs):
    csv_path = os.path.join(PROJECT_ROOT, project, "data_input", "focus_keywords.csv")
    if not os.path.exists(csv_path):
        print(f"[SKIP] {csv_path} が見つかりません")
        continue
    # ru行を抽出
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            reader.fieldnames = [h.strip() for h in reader.fieldnames]
        ru_row = None
        for row in reader:
            if row["language"].strip() == "ru":
                ru_row = row
                break
        if not ru_row:
            print(f"[SKIP] {csv_path} にロシア語行がありません")
            continue
        primary_kw = ru_row["Primary Focus Keyword"].strip()
        secondary_kw = ru_row["Secondary Focus Keyword"].strip()
        # セカンダリーキーワード（エリア名）で一致するタイトルを探す
        reference_title = next((t for t in jp_titles if secondary_kw in t), jp_titles[0] if jp_titles else "")
        year = extract_year(reference_title)
        prompt = f"""# 出力はロシア語で書いてください。

以下のキーワードを必ず含めて、魅力的なブログ記事タイトルをロシア語で考えてください。
キーワード: {primary_kw}, {secondary_kw}

参考タイトル（日本語）: {reference_title}

制約:
・タイトルには必ず「おすすめ10選」や「トップ10」「{year}年」などの要素を含めてください。
・ランキング感や年号を自然に盛り込んでください。
・参考タイトルの方向性や雰囲気、バズワード感を意識してください（直訳は避けてください）。
・SEOを意識し、検索されやすい自然なロシア語タイトルにしてください。
・30文字以内で簡潔にまとめてください。
・セールス色や過度な誇張は避けてください。
・タイトルのみを出力してください。前後に余計な説明や記号は不要です。
"""
        # translation/ru/title_prompts/title_prompt_ru_{area}.txt に保存
        area_slug = secondary_kw.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(RU_OUTPUT_DIR, f"title_prompt_ru_{area_slug}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"{output_path} にタイトル生成用プロンプトを出力しました。") 