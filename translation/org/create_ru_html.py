import os
import glob
import re

# org配下の全split_sectionsディレクトリを探索
base_dir = os.path.dirname(os.path.abspath(__file__))
org_dir = base_dir
output_base = os.path.join(base_dir, '../output')

for entry in os.listdir(org_dir):
    target_dir = os.path.join(org_dir, entry)
    split_dir = os.path.join(target_dir, "ru")
    if not os.path.isdir(split_dir):
        continue
    # ファイルパスを明示的な順序でリスト化
    intro_path = os.path.join(split_dir, "ru_intro.html")
    conclusion_path = os.path.join(split_dir, "ru_conclusion.html")
    section_paths = sorted(glob.glob(os.path.join(split_dir, "ru_section*.html")))
    html_files = []
    if os.path.isfile(intro_path):
        html_files.append(intro_path)
    html_files.extend(section_paths)
    if os.path.isfile(conclusion_path):
        html_files.append(conclusion_path)
    merged = ""
    for html_path in html_files:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            # バッククオートや```htmlなどのコードブロック記法を除去
            content = re.sub(r"```+\s*html?\s*|```+", "", content, flags=re.IGNORECASE)
            merged += content + "\n"
    # 出力先
    output_dir = os.path.join(output_base, entry)
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "ru.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(merged.strip())
    print(f"{out_path} created.") 