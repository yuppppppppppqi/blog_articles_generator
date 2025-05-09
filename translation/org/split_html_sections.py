import re
import os

# スクリプトのディレクトリ
base_dir = os.path.dirname(os.path.abspath(__file__))

# org配下の全ディレクトリを対象にする
for entry in os.listdir(base_dir):
    target_dir = os.path.join(base_dir, entry)
    if not os.path.isdir(target_dir):
        continue
    input_path = os.path.join(target_dir, 'en.html')
    if not os.path.isfile(input_path):
        continue
    output_dir = os.path.join(target_dir, 'split_sections')
    os.makedirs(output_dir, exist_ok=True)

    # ファイル読み込み
    with open(input_path, encoding='utf-8') as f:
        html = f.read()

    # h2タグで分割
    h2_pattern = r'(<h2 class="wp-block-heading">.*?</h2>)'
    h2_matches = list(re.finditer(h2_pattern, html, re.DOTALL))

    # セクションの開始・終了インデックスを決定
    splits = [0]
    splits += [m.start() for m in h2_matches]
    splits += [len(html)]

    # イントロ
    intro_path = os.path.join(output_dir, 'intro.html')
    intro = html[splits[0]:splits[1]].strip()
    with open(intro_path, 'w', encoding='utf-8') as f:
        f.write(intro)

    # 各セクション
    section_path = os.path.join(output_dir, 'section{}.html')
    for i in range(1, len(h2_matches)+1):
        section = html[splits[i]:splits[i+1]].strip()
        with open(section_path.format(i), 'w', encoding='utf-8') as f:
            f.write(section)

    # コンクルージョン
    conclusion_path = os.path.join(output_dir, 'conclusion.html')
    conclusion = html[splits[-2]:splits[-1]].strip()
    with open(conclusion_path, 'w', encoding='utf-8') as f:
        f.write(conclusion)

    print(f'Done for {entry}!') 