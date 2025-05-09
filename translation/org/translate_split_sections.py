import os
import glob
import csv
import google.generativeai as genai
from dotenv import load_dotenv

# .envの自動読み込み
load_dotenv()

API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEYが.envにありません")

MODEL_ID = "gemini-2.5-flash-preview-04-17"
genai.configure(api_key=API_KEY)

# 翻訳対象のセクションファイル名リスト（今はintro.htmlだけ）
section_targets = ["intro.html"]

# org配下の全split_sectionsディレクトリを探索
base_dir = os.path.dirname(os.path.abspath(__file__))
org_dir = base_dir
for entry in os.listdir(org_dir):
    target_dir = os.path.join(org_dir, entry)
    split_dir = os.path.join(target_dir, "split_sections")
    if not os.path.isdir(split_dir):
        continue
    ru_dir = os.path.join(target_dir, "ru")
    os.makedirs(ru_dir, exist_ok=True)
    # focus_keywords.csvのパス
    keywords_path = os.path.join(target_dir, "focus_keywords.csv")
    ru_primary = None
    ru_secondary = None
    if os.path.isfile(keywords_path):
        with open(keywords_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["language"].strip() == "ru":
                    ru_primary = row.get("Primary Focus Keyword", "").strip()
                    ru_secondary = row.get("Secondary Focus Keyword", "").strip() if "Secondary Focus Keyword" in row else None
                    break
    html_files = sorted(glob.glob(os.path.join(split_dir, "*.html")))
    for html_path in html_files:
        if os.path.basename(html_path) not in section_targets:
            continue
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        # intro.htmlのみキーワードをプロンプトに含める
        if os.path.basename(html_path) == "intro.html" and ru_primary:
            if ru_secondary:
                keyword_text = f"Primary Focus Keyword: {ru_primary}\nSecondary Focus Keyword: {ru_secondary}"
            else:
                keyword_text = f"Primary Focus Keyword: {ru_primary}"
            prompt = f"Translate the following HTML content into Russian. Use the following keywords in the translation: {keyword_text}. Only output valid HTML.\n\n{content}"
        else:
            prompt = f"Translate the following HTML content into Russian. Only output valid HTML.\n\n{content}"
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(prompt)
        out_name = "ru_" + os.path.basename(html_path)
        out_path = os.path.join(ru_dir, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(response.text.strip())
        print(f"{out_path} saved.") 