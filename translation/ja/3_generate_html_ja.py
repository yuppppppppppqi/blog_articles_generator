import os
import re
import sys
import csv # TSVファイルを扱うために追加

# --- 設定 (グローバル) ---
UPLOAD_DATE_PATH = "2025/05"  # WordPressのアップロードパス日付部分
WORDPRESS_BASE_URL = "https://my-bangkok-life.com/wp-content/uploads/"

# --- 画像・地図の自動割り当て用テンプレート ---
IMG_URL_TEMPLATE = "https://my-bangkok-life.com/wp-content/uploads/2025/05/foot-{}-{}.webp"
IMG_ALT_TEMPLATE = "foot {} {}"
MAP_IFRAME_TEMPLATE = "<iframe src='https://my-bangkok-life.com/wp-content/uploads/2025/05/foot-{}-map.html'></iframe>"  # 実際はplace_idを使う

# セクションごとの画像ファイル名・alt・place_id（英語版ロジックを流用）
SECTION_IMAGE_INFO = [
    # section番号, 画像ファイル名末尾, alt, place_id
    (1, "chiang-rai-1-naraya-massagerelax-chiangrai", "chiang rai 1 naraya massagerelax chiangrai", "ChIJ4yP2RJgB1zARjlTvIo8UM8Q"),
    (2, "chiang-rai-2-cho-kaew-thai-massage", "chiang rai 2 cho kaew thai massage", "ChIJC8u7vGcG1zARXtlzy268BeY"),
    (3, "chiang-rai-3-chiangrai-rising-sun-massage", "chiang rai 3 chiangrai rising sun massage", "ChIJgXJhu-EH1zARCdS05zMnV04"),
    (4, "chiang-rai-4-chamonpond-massage", "chiang rai 4 chamonpond massage", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (5, "chiang-rai-5-grand-spa", "chiang rai 5 grand spa", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (6, "chiang-rai-6-chiangrai-massage", "chiang rai 6 chiangrai massage", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (7, "chiang-rai-7-siamese-spa", "chiang rai 7 siamese spa", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (8, "chiang-rai-8-kham-paeng-massage", "chiang rai 8 kham paeng massage", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (9, "chiang-rai-9-chiangrai-spa", "chiang rai 9 chiangrai spa", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
    (10, "chiang-rai-10-chiangrai-massage", "chiang rai 10 chiangrai massage", "ChIJw7Qw1JcB1zARQn6vQwQwQwQ"),
]

# --- ユーティリティ関数 ---
def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        # print(f"Warning: File not found or could not read {filepath} - {e}")
        return ""

def write_file(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")

def get_section_numbers(sections_dir):
    if not os.path.exists(sections_dir) or not os.path.isdir(sections_dir):
        return []
    return sorted([int(d) for d in os.listdir(sections_dir) if d.isdigit() and os.path.isdir(os.path.join(sections_dir, d))])

def get_english_keywords_prefix(english_project_data_input_dir):
    focus_keywords_path = os.path.join(english_project_data_input_dir, 'focus_keywords.csv')
    if not os.path.exists(focus_keywords_path):
        # print(f"Warning: focus_keywords.csv not found at {focus_keywords_path}")
        return "foot-massage-default" # フォールバック
    try:
        with open(focus_keywords_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned_row = {k.strip(): v for k, v in row.items()}
                if cleaned_row.get('language') == 'en':
                    primary = cleaned_row.get('Primary Focus Keyword', '').strip()
                    secondary = cleaned_row.get('Secondary Focus Keyword', '').strip()
                    if primary and secondary:
                        return f"{primary.lower().replace(' ', '-')}-{secondary.lower().replace(' ', '-')}"
                    elif primary:
                        return primary.lower().replace(' ', '-')
        return "foot-massage-default" # 見つからなかった場合
    except Exception as e:
        # print(f"Error reading focus_keywords.csv: {e}")
        return "foot-massage-default"

def get_wordpress_image_filename(english_project_images_dir, english_prefix, target_chapter):
    if not os.path.exists(english_project_images_dir) or not os.path.isdir(english_project_images_dir):
        # print(f"  DEBUG: English project images directory not found or not a directory: {english_project_images_dir}")
        return None
    try:
        # all_files = os.listdir(english_project_images_dir)
        # print(f"    Files in images_dir: {all_files}")
        
        # 1. 通常のプレフィックスで検索
        expected_start = f"{english_prefix}-{target_chapter}-"
        # print(f"      Checking file with primary prefix: {expected_start}")
        for filename in os.listdir(english_project_images_dir):
            if filename.endswith('.webp'):
                # print(f"      Checking file: {filename} against expected_start: {expected_start}")
                if filename.startswith(expected_start):
                    # print(f"    Found matching file: {filename}")
                    return filename
        
        # 2. "massage-" を除いた代替プレフィックスで検索
        if "massage-" in english_prefix:
            alternative_prefix = english_prefix.replace("massage-", "")
            alternative_expected_start = f"{alternative_prefix}-{target_chapter}-"
            # print(f"      Checking file with alternative prefix: {alternative_expected_start}")
            for filename in os.listdir(english_project_images_dir):
                if filename.endswith('.webp'):
                    # print(f"      Checking file: {filename} against alternative_expected_start: {alternative_expected_start}")
                    if filename.startswith(alternative_expected_start):
                        # print(f"    Found matching file with alternative prefix: {filename}")
                        return filename
                        
        # print(f"  DEBUG: No matching .webp file found for prefix '{english_prefix}' (and alternative) and chapter {target_chapter}")
    except Exception as e:
        # print(f"  DEBUG: Error accessing images directory {english_project_images_dir}: {e}")
        pass
    return None # 見つからなければNone

def get_place_id_from_shops_tsv(english_project_data_input_dir, target_chapter):
    shops_tsv_path = os.path.join(english_project_data_input_dir, 'shops.tsv')
    if not os.path.exists(shops_tsv_path):
        # print(f"Warning: shops.tsv not found at {shops_tsv_path}")
        return ""
    try:
        with open(shops_tsv_path, 'r', encoding='utf-8') as f:
            tsv_reader = csv.reader(f, delimiter='\t')
            header = next(tsv_reader)
            
            embed_url_col_index = -1
            try:
                embed_url_col_index = header.index('Embed URL') # 'Embed URL' 列のインデックスを取得
            except ValueError:
                # print(f"Warning: 'Embed URL' column not found in {shops_tsv_path}.")
                return "" # 列が見つからなければ空

            for i, row in enumerate(tsv_reader, start=1):
                if i == target_chapter:
                    if embed_url_col_index != -1 and len(row) > embed_url_col_index:
                        embed_url = row[embed_url_col_index]
                        # 正規表現で place_id=... を抽出
                        match = re.search(r"place_id:([^&]+)", embed_url)
                        if match:
                            return match.group(1)
                        else:
                            # print(f"Warning: Could not extract Place ID from Embed URL: {embed_url}")
                            return ""
                    else:
                        # print(f"Warning: Row {target_chapter} in {shops_tsv_path} is empty or too short for Embed URL.")
                        return ""
    except Exception as e:
        # print(f"Error reading shops.tsv or extracting Place ID: {e}")
        pass
    return ""

def generate_summary_html(project_name, base_temp_path_project, section_num, summary_txt_path, output_path):
    summary_content = read_file(summary_txt_path)
    if not summary_content:
        print(f"  Warning: {summary_txt_path} is empty or not found.")
        # ショップ名だけでも表示試行するため、ここではreturnしないことを検討したが、
        # summary.txtがない場合は基本情報が欠落するので空HTMLが良いだろう。
        # ただし、英語ショップ名ベースで進めるなら、summary.txtがなくてもショップ名H2は出せる。
        # ここでは、summary.txt がないと主要な日本語情報がないので空を返す方針は維持。
        # return "" 
    lines = [l.strip() for l in summary_content.splitlines()] if summary_content else []

    # summary.txt の内容を調整して読み込む
    # デフォルト値を設定しつつ、実際のテキストがあればそれを採用
    rating_text = lines[0] if len(lines) > 0 else "評価情報なし"
    price_text = lines[1] if len(lines) > 1 else "価格情報なし"
    recommended_text = lines[2] if len(lines) > 2 else "おすすめ情報なし" # summary.txtの3行目は「おすすめ」で始まる想定
    summary_body_text = lines[3] if len(lines) > 3 else "概要なし" # summary.txtの4行目は「まとめ」で始まる想定

    # 正規表現で行頭の「キーワード[スペース]*[:：][スペース]*」を除去
    # これにより、summary.txt側の接頭辞を削除する
    rating_ja = re.sub(r"^\s*評価\s*[:：]\s*", "", rating_text).strip()
    rating_ja = re.sub(r"(\S+)/(\S+)", r"\1 / \2", rating_ja) # スラッシュの前後にスペースを挿入
    price_ja = re.sub(r"^\s*価格\s*[:：]\s*", "", price_text).strip()
    recommended_ja = re.sub(r"^\s*おすすめ\s*[:：]\s*", "", recommended_text).strip()
    summary_body_ja = re.sub(r"^\s*まとめ\s*[:：]\s*", "", summary_body_text).strip()

    # --- 英語のショップ名を取得する処理 ---
    shop_name_en = "ショップ名不明" # デフォルト
    # 3_generate_html.py の実行場所からの相対パスで英語版プロジェクトのパスを構築
    # このスクリプトは translation/3_generate_html.py なので、親ディレクトリがワークスペースルート
    script_dir = os.path.dirname(os.path.abspath(__file__)) # translation
    workspace_root = os.path.dirname(script_dir) # blog_articles_generator
    
    # project_name は 1_best_foot_massage_in_sukhumvit_2025 のような形式
    english_project_base_dir = os.path.join(workspace_root, project_name)
    english_shops_tsv_path = os.path.join(english_project_base_dir, "data_input", "shops.tsv")

    if os.path.exists(english_shops_tsv_path):
        try:
            with open(english_shops_tsv_path, 'r', encoding='utf-8') as f_tsv:
                tsv_reader = csv.reader(f_tsv, delimiter='	')
                header = next(tsv_reader) # ヘッダー行をスキップ
                shop_name_col_index = 0 # 通常、ショップ名は最初の列にあると仮定
                # ヘッダーに 'Name' があればそのインデックスを使う (より堅牢)
                if 'Name' in header:
                    shop_name_col_index = header.index('Name')
                
                for i, row in enumerate(tsv_reader, start=1):
                    if i == section_num:
                        if len(row) > shop_name_col_index:
                            shop_name_en = row[shop_name_col_index].strip()
                        else:
                            print(f"  [Warning] Row for section {section_num} in {english_shops_tsv_path} is shorter than expected shop name column.")
                        break
                if shop_name_en == "ショップ名不明" and section_num <= i: # ループは回ったが該当セクションが見つからない(iは最終行番号)
                     print(f"  [Warning] Section {section_num} not found in {english_shops_tsv_path} (max {i} sections). Using default shop name.")
        except Exception as e:
            print(f"  [Warning] Could not read shop name from {english_shops_tsv_path} for section {section_num}: {e}")
    else:
        print(f"  [Warning] English shops.tsv not found at {english_shops_tsv_path}. Using default shop name.")
    # --- 英語のショップ名取得処理ここまで ---

    # 対応する英語版プロジェクトのパスを決定 (画像・地図用 - これは元々のロジックを少し調整)
    # generate_summary_html は project_name を引数に取るので、それをそのまま使う
    # english_project_name = project_name # これは上で定義済み
    # english_project_base_dir は上で定義済み
    english_project_data_input_dir = os.path.join(english_project_base_dir, "data_input")
    english_project_images_dir = os.path.join(english_project_base_dir, "data_output", "images")

    english_prefix = get_english_keywords_prefix(english_project_data_input_dir) # これは画像URLのプレフィックス用
    wp_image_filename = get_wordpress_image_filename(english_project_images_dir, english_prefix, section_num)
    
    image_url = ""
    if wp_image_filename:
        image_url = f"{WORDPRESS_BASE_URL}{UPLOAD_DATE_PATH}/{wp_image_filename}"
    else:
        print(f"  Warning: Image filename not found for {project_name} section {section_num}. Image will be missing.")

    # altテキストはH2に合わせて英語のショップ名を使用
    alt_text = shop_name_en

    place_id = get_place_id_from_shops_tsv(english_project_data_input_dir, section_num)
    map_iframe = ""
    if place_id:
        map_iframe = f"<iframe src='https://www.google.com/maps/embed/v1/place?q=place_id:{place_id}&zoom=17&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8' width='600' height='450' style='border:0' allowfullscreen='' loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe>"
    else:
        print(f"  Warning: Place ID not found for {project_name} section {section_num}. Map will be missing.")

    html = f'''<h2 style="margin-bottom: 20px; margin-top: 50px;"><strong>{shop_name_en}</strong></h2>
<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full" style="margin-bottom: 20px;">
    <img src="{image_url}" alt="{alt_text}" class="wp-image-21" />
</figure>
<!-- /wp:image -->
<!-- wp:list -->
<ul class='wp-block-list' style="padding-left: 15px; margin-left: 0;">
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;"><strong>総合評価:</strong> {rating_ja}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;"><strong>価格:</strong> {price_ja}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;"><strong>こんな人へ:</strong> {recommended_ja}</li>
   <!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
<!-- wp:paragraph -->
<p style="margin-top: 20px; margin-bottom: 20px; line-height: 1.6;">{summary_body_ja}</p>
<!-- /wp:paragraph -->
<p>{map_iframe}</p>'''
    write_file(output_path, html)
    return html

def generate_reviews_html(reviews_txt_path, output_path):
    reviews_content = read_file(reviews_txt_path)
    if not reviews_content:
        # print(f"  Warning: {reviews_txt_path} is empty or not found.")
        return ""
    reviews = [l.strip() for l in reviews_content.splitlines() if l.strip()]
    if len(reviews) != 10:
        # print(f"  Warning: {reviews_txt_path} does not contain exactly 10 reviews (found {len(reviews)}). Skipping reviews section.")
        return "" # レビュー数が10でない場合は空のHTMLを返す
    order = [0, 1, 2, 8, 3, 4, 9, 5, 6, 7]
    html = '<!-- wp:heading {"level":4} -->\n'
    html += '<h3 class="wp-block-heading"><strong>レビュー</strong></h3>\n' # 日本語に変更
    html += '<!-- /wp:heading -->\n\n'
    html += '<!-- wp:list -->\n'
    html += '<ul class="wp-block-list" style="padding-left: 15px; margin-left: 0;">\n'
    for idx in order:
        if idx < len(reviews):
            html += '   <!-- wp:list-item -->\n'
            html += f'   <li style="margin-bottom: 10px; margin-left: 0;">{reviews[idx]}</li>\n'
            html += '   <!-- /wp:list-item -->\n'
    html += '</ul>\n'
    html += '<!-- /wp:list -->'
    write_file(output_path, html)
    return html

def generate_conclusion_with_h2(conclusion_path, output_path):
    content = read_file(conclusion_path)
    if not content:
        # print(f"  Warning: {conclusion_path} is empty or not found.")
        return ""
    h2_tag = '<h2 style="margin-bottom: 20px; margin-top: 50px;"><strong>まとめ</strong></h2>' # 日本語に変更
    new_content = h2_tag + '\n' + content
    write_file(output_path, new_content)
    return new_content

# --- メイン処理 ---
def main():
    temp_root_translation = os.path.join("translation", "temp")
    project_dirs_translation = [d for d in os.listdir(temp_root_translation) if os.path.isdir(os.path.join(temp_root_translation, d)) and re.match(r"\d+_best_foot_massage_(in|near)_.*_2025", d)]
    
    if not project_dirs_translation:
        print("No project directories found in translation/temp.")
        return

    for project_name_translation in sorted(project_dirs_translation, key=lambda x: int(x.split('_')[0])):
        try:
            print(f"\n=== Processing Japanese project: {project_name_translation} ===")
            base_temp_path_project_translation = os.path.join(temp_root_translation, project_name_translation)
            output_dir_project_translation = os.path.join("translation", "output", project_name_translation)
            output_file_project_translation = os.path.join(output_dir_project_translation, "ja.html")
            os.makedirs(output_dir_project_translation, exist_ok=True)

            html_parts = []

            # intro
            intro_path_translation = os.path.join(base_temp_path_project_translation, "sections", "intro", "intro.html") # "sections" を追加
            intro_content = read_file(intro_path_translation)
            if intro_content: 
                html_parts.append(intro_content)
            else:
                print(f"  Warning: intro.html not found or empty for {project_name_translation}")

            # sections
            sections_dir_translation = os.path.join(base_temp_path_project_translation, "sections")
            section_numbers = get_section_numbers(sections_dir_translation)
            if not section_numbers:
                print(f"  Warning: No sections found for {project_name_translation}")

            for sec_num in section_numbers:
                sec_dir_translation = os.path.join(sections_dir_translation, str(sec_num), "ja") # 日本語版のセクションパス
                summary_txt_translation = os.path.join(sec_dir_translation, "summary.txt")
                reviews_txt_translation = os.path.join(sec_dir_translation, "reviews.txt")
                
                # 中間HTMLファイルの出力先も日本語プロジェクト内にする
                summary_html_output_path = os.path.join(sec_dir_translation, "summary_generated.html") 
                reviews_html_output_path = os.path.join(sec_dir_translation, "reviews_generated.html")

                if os.path.exists(summary_txt_translation):
                    summary_html_content = generate_summary_html(project_name_translation, base_temp_path_project_translation, sec_num, summary_txt_translation, summary_html_output_path)
                    if summary_html_content: html_parts.append(summary_html_content)
                else:
                    print(f"  Warning: summary.txt not found for section {sec_num} in {project_name_translation}")
                
                if os.path.exists(reviews_txt_translation):
                    reviews_html_content = generate_reviews_html(reviews_txt_translation, reviews_html_output_path)
                    if reviews_html_content: html_parts.append(reviews_html_content)
                else:
                    print(f"  Warning: reviews.txt not found for section {sec_num} in {project_name_translation}")

            # conclusion
            conclusion_dir_translation = os.path.join(base_temp_path_project_translation, "sections", "conclusion") # "sections" を追加
            conclusion_html_translation = os.path.join(conclusion_dir_translation, "conclusion.html")
            conclusion_with_h2_output_path = os.path.join(conclusion_dir_translation, "conclusion_with_h2_generated.html")
            
            if os.path.exists(conclusion_html_translation):
                conclusion_html_content = generate_conclusion_with_h2(conclusion_html_translation, conclusion_with_h2_output_path)
                if conclusion_html_content: html_parts.append(conclusion_html_content)
            else:
                print(f"  Warning: conclusion.html not found for {project_name_translation}")

            # 結合して出力
            final_html = '\n\n'.join(filter(None, html_parts)) # Noneや空文字列を除外して結合
            if final_html.strip(): # 空でなければ書き出す
                write_file(output_file_project_translation, final_html)
                print(f"  → Generated: {output_file_project_translation}")
            else:
                print(f"  Warning: No content to write for {project_name_translation}. Output file not created.")

        except Exception as e:
            print(f"  [ERROR] Processing {project_name_translation}: {e}")
            import traceback
            traceback.print_exc() # 詳細なエラー情報を表示

if __name__ == "__main__":
    main()

# テンプレートディレクトリのパスを修正
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'prompt_templates')
