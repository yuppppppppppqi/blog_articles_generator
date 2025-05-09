import os
import sys
import re
from dotenv import load_dotenv
import google.generativeai as genai
import unidecode

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
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

MODEL_ID = "gemini-2.5-flash-preview-04-17"
genai.configure(api_key=API_KEY)

PROMPT_DIR = os.path.join(os.path.dirname(__file__), "intro_prompts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "intro_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

slugify = lambda s: re.sub(r"[^A-Za-z0-9_]", "", unidecode.unidecode(s.replace(" ", "_")))

prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.startswith("body_intro_prompt_ru_") and f.endswith(".txt")]

for prompt_file in sorted(prompt_files):
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)
    m = re.match(r"body_intro_prompt_ru_(.+)\.txt", prompt_file)
    if not m:
        continue
    slug = slugify(m.group(1))
    output_path = os.path.join(OUTPUT_DIR, f"intro_ru_{slug}.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    model = genai.GenerativeModel(MODEL_ID)
    response = model.generate_content(prompt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response.text.strip())
    print(f"生成結果を {output_path} に保存しました。") 