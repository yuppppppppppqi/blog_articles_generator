import os
import sys
import re
import argparse
from translation.common.utils import ensure_dir
from dotenv import load_dotenv
import google.generativeai as genai
import unidecode

# .envの自動読み込み
load_dotenv()

# Gemini API (Google Generative AI SDK)

# GEMINI_API_KEYがなければ、.env内の他のAPIキーらしき値を使う
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    # よくあるAPIキー名の候補
    candidates = [
        "API_KEY", "GOOGLE_API_KEY", "GOOGLE_MAPS_API_KEY", "OPENAI_API_KEY"
    ]
    for key in candidates:
        if os.environ.get(key):
            API_KEY = os.environ.get(key)
            print(f"INFO: {key} をGemini APIキーとして仮利用します。")
            break
if not API_KEY:
    print("ERROR: .envに有効なAPIキーが見つかりません。GEMINI_API_KEYまたは他のAPIキーをセットしてください。")
    sys.exit(1)

# Gemini 2.5 FlashモデルID
MODEL_ID = "gemini-2.5-flash-preview-04-17"

genai.configure(api_key=API_KEY)

parser = argparse.ArgumentParser()
parser.add_argument("--section", type=str, default="title", choices=["title", "intro", "conclusion", "reviews", "summary"], help="生成するセクション")
parser.add_argument("--area", type=str, default=None, help="特定エリアのみ処理する場合")
parser.add_argument("--only-section", action="store_true", help="タイトル生成をスキップし、指定セクションのみ生成")
args = parser.parse_args()

SECTION_CONFIG = {
    "title": {
        "PROMPT_DIR": "title_prompts",
        "OUTPUT_DIR": "title_results",
        "PREFIX": "title_ru_",
        "PROMPT_PREFIX": "title_prompt_ru_",
    },
    "intro": {
        "PROMPT_DIR": "intro_prompts",
        "OUTPUT_DIR": "intro_results",
        "PREFIX": "intro_ru_",
        "PROMPT_PREFIX": "body_intro_prompt_ru_",
    },
    "conclusion": {
        "PROMPT_DIR": "conclusion_prompts",
        "OUTPUT_DIR": "conclusion_results",
        "PREFIX": "conclusion_ru_",
        "PROMPT_PREFIX": "body_conclusion_prompt_ru_",
    },
    "reviews": {
        "PROMPT_DIR": "../temp",  # translation/temp
        "OUTPUT_DIR": "reviews_results",
        "PREFIX": "reviews_ru_",
        "PROMPT_PREFIX": "prompt_to_translate_reviews.txt",
    },
    "summary": {
        "PROMPT_DIR": "../temp",  # translation/temp
        "OUTPUT_DIR": "summary_results",
        "PREFIX": "summary_ru_",
        "PROMPT_PREFIX": "prompt_to_translate_summary.txt",
    },
}

conf = SECTION_CONFIG[args.section]
PROMPT_DIR = os.path.join(os.path.dirname(__file__), conf["PROMPT_DIR"])
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), conf["OUTPUT_DIR"])
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ローマ字・英数字・アンダースコアのみのslugを作る
slugify = lambda s: re.sub(r"[^A-Za-z0-9_]", "", unidecode.unidecode(s.replace(" ", "_")))

if args.section in ["reviews", "summary"]:
    import glob
    if args.area:
        pattern = os.path.join(PROMPT_DIR, args.area, "sections", "*", "ru", conf["PROMPT_PREFIX"])
    else:
        pattern = os.path.join(PROMPT_DIR, "*", "sections", "*", "ru", conf["PROMPT_PREFIX"])
    prompt_files = glob.glob(pattern)
else:
    if args.area:
        prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.startswith(conf["PROMPT_PREFIX"]) and f.endswith(".txt") and args.area in f]
    else:
        prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.startswith(conf["PROMPT_PREFIX"]) and f.endswith(".txt")]
    prompt_files = [os.path.join(PROMPT_DIR, f) for f in prompt_files]

for prompt_path in sorted(prompt_files):
    if args.section in ["reviews", "summary"]:
        # ファイル名からプロジェクト名・セクション番号を抽出
        m = re.search(r"temp/(.+?)/sections/(\d+)/ru/" + conf["PROMPT_PREFIX"], prompt_path)
        if m:
            project = m.group(1)
            section = m.group(2)
            slug = slugify(f"{project}_{section}")
        else:
            slug = slugify(os.path.basename(prompt_path))
        output_path = os.path.join(OUTPUT_DIR, f"{conf['PREFIX']}{slug}.txt")
    else:
        m = re.match(rf"{re.escape(conf['PROMPT_PREFIX'])}(.+)\.txt", os.path.basename(prompt_path))
        if not m:
            continue
        slug = slugify(m.group(1))
        output_path = os.path.join(OUTPUT_DIR, f"{conf['PREFIX']}{slug}.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    model = genai.GenerativeModel(MODEL_ID)
    response = model.generate_content(prompt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text.strip())
    print(f"生成結果を {output_path} に保存しました。") 