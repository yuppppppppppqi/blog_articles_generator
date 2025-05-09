import os

TITLE_DIR = os.path.join(os.path.dirname(__file__), "title_results")
BODY_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "body_prompts")
os.makedirs(BODY_PROMPT_DIR, exist_ok=True)

# テンプレート
PROMPT_TEMPLATE = """# 出力はロシア語で書いてください。

以下のタイトルにふさわしいロシア語のブログ記事本文を生成してください。
タイトル: {title}

制約:
・SEOを意識し、検索されやすい自然なロシア語で書いてください。
・情報提供を目的とした記事にしてください。
・セールス色や過度な誇張は避けてください。
・本文のみを出力してください。前後に余計な説明や記号は不要です。
・2000文字程度を目安にしてください。
"""

for fname in os.listdir(TITLE_DIR):
    if fname.startswith("title_ru_") and fname.endswith(".txt"):
        area = fname[len("title_ru_"):-len(".txt")]
        with open(os.path.join(TITLE_DIR, fname), encoding="utf-8") as f:
            title = f.read().strip()
        prompt = PROMPT_TEMPLATE.format(title=title)
        out_path = os.path.join(BODY_PROMPT_DIR, f"body_prompt_ru_{area}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"{out_path} に本文生成用プロンプトを出力しました。") 