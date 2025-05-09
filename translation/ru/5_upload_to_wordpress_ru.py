import os
import requests
import json
import re
import csv
import mimetypes
from dotenv import load_dotenv
from translation.common.utils import load_template, ensure_dir

# --- Constants for project number filtering ---
MIN_PROJECT_NUMBER = 4
MAX_PROJECT_NUMBER = 18
# --- End of constants ---

# --- グローバル設定読み込み ---
def load_app_settings():
    """設定ファイルからグローバル設定を読み込む"""
    _settings = {
        "WP_BASE_URL": os.getenv("WP_BASE_URL"),
        "WP_USERNAME": os.getenv("WP_USERNAME"),
        "WP_APP_PASSWORD": os.getenv("WP_APP_PASSWORD"),
        "TARGET_CATEGORY_ID": 30,  # デフォルト値
        "POLYLANG_LANG_TERM_IDS": {}, # 追加: 言語コードとタームIDのマッピング
    }

    # settings.txt から TARGET_CATEGORY_ID を読み込む
    settings_txt_path = os.path.join("translation", "settings", "settings.txt")
    try:
        with open(settings_txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith("TARGET_CATEGORY_ID="):
                    _settings["TARGET_CATEGORY_ID"] = int(line.strip().split("=")[1])
                    break
    except FileNotFoundError:
        print(f"  [Warning] {settings_txt_path} not found. Using default TARGET_CATEGORY_ID: {_settings['TARGET_CATEGORY_ID']}")
    except Exception as e:
        print(f"  [Error] Reading {settings_txt_path}: {e}. Using default TARGET_CATEGORY_ID: {_settings['TARGET_CATEGORY_ID']}")

    # polylang_language_ids.txt から各言語の Polylang タームIDを読み込む
    polylang_ids_path = os.path.join("translation", "settings", "polylang_language_ids.txt")
    try:
        with open(polylang_ids_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): # 空行やコメント行はスキップ
                    continue
                parts = line.split(':')
                if len(parts) == 2:
                    lang_code = parts[0].strip()
                    term_id_str = parts[1].strip()
                    if lang_code and term_id_str.isdigit():
                        _settings["POLYLANG_LANG_TERM_IDS"][lang_code] = int(term_id_str)
                    else:
                        print(f"  [Warning] Invalid format in {polylang_ids_path}: '{line}'. Skipping.")
                else:
                    print(f"  [Warning] Invalid format in {polylang_ids_path}: '{line}'. Skipping.")
        if not _settings["POLYLANG_LANG_TERM_IDS"]:
            print(f"  [Warning] No language term IDs loaded from {polylang_ids_path}. Language setting for posts will be skipped.")
    except FileNotFoundError:
        print(f"  [Warning] {polylang_ids_path} not found. Language setting for posts will be skipped.")
    except Exception as e:
        print(f"  [Error] Reading {polylang_ids_path}: {e}. Language setting for posts will be skipped.")
        
    return _settings

# .envファイルから環境変数を読み込む (存在すれば)
load_dotenv()
APP_SETTINGS = load_app_settings()
print(f"Loaded Polylang Term IDs: {APP_SETTINGS.get('POLYLANG_LANG_TERM_IDS')}") # DEBUG PRINT

WP_BASE_URL = APP_SETTINGS["WP_BASE_URL"]
WP_USERNAME = APP_SETTINGS["WP_USERNAME"]
WP_APP_PASSWORD = APP_SETTINGS["WP_APP_PASSWORD"]
TARGET_CATEGORY_ID = APP_SETTINGS["TARGET_CATEGORY_ID"]
POLYLANG_LANG_TERM_IDS = APP_SETTINGS.get("POLYLANG_LANG_TERM_IDS", {}) # 追加

# WordPress APIエンドポイント
API_POSTS_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/posts" if WP_BASE_URL else None
API_MEDIA_ENDPOINT = f"{WP_BASE_URL}/wp-json/wp/v2/media" if WP_BASE_URL else None

# テンプレートディレクトリのパスを修正
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'prompt_templates')

# タイトルテンプレートのパス
TITLE_TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "post_title_template_ja.txt")

# アイキャッチ画像のファイル名サフィックス (プロジェクトによる違いがあれば調整)
# FEATURED_IMAGE_FILENAME_SUFFIX = "-special-header.webp" # 使われなくなるためコメントアウト

# --- ヘルパー関数 ---

def read_file_content(filepath):
    """ファイルの内容を読み込む"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"  [Warning] File not found: {filepath}")
        return None
    except Exception as e:
        print(f"  [Error] Could not read file {filepath}: {e}")
        return None

def get_keywords_for_title(english_project_data_input_dir, lang_to_get):
    """focus_keywords.csvから指定言語のキーワードを取得してタイトル生成用データを返す"""
    keywords = {"primary": "", "secondary": ""}
    focus_keywords_path = os.path.join(english_project_data_input_dir, 'focus_keywords.csv')
    if not os.path.exists(focus_keywords_path):
        print(f"  [Warning] focus_keywords.csv not found at {focus_keywords_path}")
        return keywords
    try:
        with open(focus_keywords_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # CSVのヘッダー名に合わせてキーを調整
                cleaned_row_keys = {k.strip().lower() if k else None: v.strip() for k, v in row.items()}
                lang_in_row = cleaned_row_keys.get("language", "").lower() # キーを小文字で取得

                if lang_in_row == lang_to_get.lower():
                    keywords["primary"] = cleaned_row_keys.get('primary focus keyword', '').strip() # キーを小文字で取得
                    keywords["secondary"] = cleaned_row_keys.get('secondary focus keyword', '').strip() # キーを小文字で取得
                    break
        if not keywords["primary"] and not keywords["secondary"]:
            print(f"  [Warning] Keywords for '{lang_to_get}' not found in {focus_keywords_path}. Title might be generic.")
        return keywords
    except Exception as e:
        print(f"  [Error] Reading focus_keywords.csv for '{lang_to_get}' keywords: {e}")
        return keywords

def get_english_keywords_prefix(english_project_data_input_dir):
    """focus_keywords.csvから英語のキーワードを取得してファイル名プレフィックスを生成"""
    keywords = {"primary_en": "", "secondary_en": ""}
    focus_keywords_path = os.path.join(english_project_data_input_dir, 'focus_keywords.csv')
    if not os.path.exists(focus_keywords_path):
        print(f"  [Warning] get_english_keywords_prefix: focus_keywords.csv not found at {focus_keywords_path}")
        return None
    try:
        with open(focus_keywords_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            found_en_keywords = False
            for row in reader:
                cleaned_row = {k.strip().lower(): v.strip() for k, v in row.items()}
                if cleaned_row.get('language', '').lower() == 'en':
                    keywords["primary_en"] = cleaned_row.get('primary focus keyword', '').strip()
                    keywords["secondary_en"] = cleaned_row.get('secondary focus keyword', '').strip()
                    found_en_keywords = True
                    break  # Stop after finding the 'en' row
        
        if not found_en_keywords:
            print(f"  [Warning] get_english_keywords_prefix: English keywords (lang=en) not found in {focus_keywords_path}.")
            return None

        primary_slug = keywords["primary_en"].replace(' ', '-').lower() if keywords["primary_en"] else ""
        secondary_slug = keywords["secondary_en"].replace(' ', '-').lower() if keywords["secondary_en"] else ""

        if primary_slug and secondary_slug:
            prefix = f"{primary_slug}-{secondary_slug}"
            # 3_generate_html.py の挙動に合わせ、一般的な "best-" プレフィックスがあれば除去する処理を追加
            # 例: "best-foot-massage-sukhumvit" -> "foot-massage-sukhumvit"
            # ただし、この処理は 3_generate_html.py で具体的にどうやっているか確認が必要。
            # ここでは、もし "best-" で始まっていたら除去する、という単純なルールを仮定する。
            # 一般的なキーワードの場合 "best" が意図的な場合もあるので、この処理は慎重に検討が必要。
            # 今回は、ユーザーの「各プロジェクトを見てきて、自分で考えて」という指示から、
            # 英語版キーワードから直接生成する形を優先し、"best-" 除去は一旦行わない。
            # もし必要であれば、3_generate_html.py のプレフィックス生成ロジックを正確に移植する。
            return prefix
        elif primary_slug:
            return primary_slug
        elif secondary_slug:
            return secondary_slug
        else:
            print(f"  [Warning] get_english_keywords_prefix: Both primary and secondary English keywords are empty in {focus_keywords_path}.")
            return None
            
    except Exception as e:
        print(f"  [Error] get_english_keywords_prefix: Reading focus_keywords.csv for English prefix: {e}")
        return None

def count_sections_in_html(html_content):
    """HTMLコンテンツ内の店舗紹介セクションのh2タグの数を数える"""
    if not html_content:
        return 0
    h2_tags = re.findall(r"<h2[^>]*>(.*?)</h2>", html_content, re.IGNORECASE | re.DOTALL)
    if not h2_tags:
        return 0
    section_count = 0
    for h2_content_full in h2_tags:
        h2_content = h2_content_full.strip()
        if "まとめ" not in h2_content:
            section_count += 1
    return section_count

def generate_post_title(primary_keyword_ja, secondary_keyword_ja, num_sections, lang_code):
    template_content = read_file_content(TITLE_TEMPLATE_PATH)
    if not template_content:
        print("  [Error] Title template not found or empty. Using default title.")
        return f"{secondary_keyword_ja}の{primary_keyword_ja}おすすめ記事"
    title = template_content.strip()
    title = title.replace("[primary keyword]", primary_keyword_ja if primary_keyword_ja else "フットマッサージ")
    title = title.replace("[secondary keyword]", secondary_keyword_ja if secondary_keyword_ja else "エリア")
    title = title.replace("[N]", str(num_sections) if num_sections > 0 else "人気")
    return title

def generate_post_slug(english_project_data_input_dir):
    project_name_for_fallback = os.path.basename(os.path.dirname(english_project_data_input_dir))
    # Generate a simple, clean base slug from the project name for fallbacks
    base_fallback_slug = re.sub(r'[^a-z0-9]+', '-', project_name_for_fallback.lower()).strip('-')
    if not base_fallback_slug: # Should not happen if project_name_for_fallback is valid
        base_fallback_slug = f"project-{abs(hash(project_name_for_fallback)) % 10000}" # Robust unique ID

    keywords_csv_path = os.path.join(english_project_data_input_dir, "focus_keywords.csv")
    keywords = {}
    try:
        with open(keywords_csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # Robust handling of None for keys and values in the CSV row
                cleaned_row_keys = {
                    (k.strip().lower() if k is not None else None): (v.strip() if v is not None else "")
                    for k, v in row.items()
                }
                # Remove any keys that ended up as None (e.g., from malformed CSV headers)
                cleaned_row_keys = {k: v for k, v in cleaned_row_keys.items() if k is not None}

                lang = cleaned_row_keys.get("language", "").strip().lower()
                if lang:
                    # Ensure default to empty string if keys are missing, then strip
                    primary_kw = cleaned_row_keys.get("primary focus keyword", "")
                    secondary_kw = cleaned_row_keys.get("secondary focus keyword", "")
                    keywords[lang] = {
                        "Primary Focus Keyword": primary_kw.strip(),
                        "Secondary Focus Keyword": secondary_kw.strip()
                    }
    except FileNotFoundError:
        print(f"    [Warning] Keywords file not found: {keywords_csv_path}. Using fallback slug: {base_fallback_slug}-no-csv")
        return f"{base_fallback_slug}-no-csv"
    except Exception as e:
        print(f"    [Error] Reading keywords file {keywords_csv_path} for slug generation: {e}. Using fallback slug: {base_fallback_slug}-csv-error")
        return f"{base_fallback_slug}-csv-error"

    primary_keyword_en = keywords.get('en', {}).get('Primary Focus Keyword', '').strip()
    secondary_keyword_en_full = keywords.get('en', {}).get('Secondary Focus Keyword', '').strip()
    
    print(f"    DEBUG SLUG: Loaded EN Primary Keyword: '{primary_keyword_en}'")
    print(f"    DEBUG SLUG: Loaded EN Secondary Keyword (full): '{secondary_keyword_en_full}'")

    secondary_keyword_en = secondary_keyword_en_full.split(',')[0].strip() if secondary_keyword_en_full else ""
    print(f"    DEBUG SLUG: Using EN Secondary Keyword (first part): '{secondary_keyword_en}'")

    slug_parts = []
    if primary_keyword_en:
        pk_lower = primary_keyword_en.lower()
        if "best" not in pk_lower.split(" "): # Note: split() without args handles multiple spaces better
            slug_parts.append("best")
            print(f"    DEBUG SLUG: Added 'best' to slug_parts: {slug_parts}")
        
        slug_parts.extend([part.lower() for part in pk_lower.replace("-", " ").split() if part]) # Use split() for robustness
        print(f"    DEBUG SLUG: slug_parts after primary keyword: {slug_parts}")

    if secondary_keyword_en:
        sk_lower = secondary_keyword_en.lower()
        slug_parts.extend([part.lower() for part in sk_lower.replace("-", " ").split() if part]) # Use split()
        print(f"    DEBUG SLUG: slug_parts after secondary keyword: {slug_parts}")
    
    if not slug_parts:
        print(f"    [Warning] Could not generate slug from English keywords in {keywords_csv_path} (primary='{primary_keyword_en}', secondary='{secondary_keyword_en}'). Using fallback slug: {base_fallback_slug}-no-en-keywords")
        return f"{base_fallback_slug}-no-en-keywords"

    processed_slug_parts = []
    for part in slug_parts:
        sub_parts = re.split(r'[-\s]+', part)
        processed_slug_parts.extend([p for p in sub_parts if p])

    slug = "-".join(processed_slug_parts)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip('-')

    if not slug:
        print(f"    [Warning] Slug from keywords became empty after cleaning for {english_project_data_input_dir}. Using fallback slug: {base_fallback_slug}-empty-cleaned-slug")
        return f"{base_fallback_slug}-empty-cleaned-slug"

    return slug

def get_potential_featured_image_filenames(generated_english_slug):
    # english_project_data_input_dir は使わなくなったので、代わりに生成済みスラッグを利用
    # slug = generate_post_slug(english_project_data_input_dir) # この呼び出しは不要になる
    # if not slug or "fallback" in slug or "empty" in slug: # スラッグ生成失敗時はデフォルトのファイル名候補
    #     return ["header.webp", "profile.webp"]
    
    # スラッグが正常に生成されたと仮定
    base_filename = generated_english_slug # 引数で受け取ったスラッグを使用

    potential_filenames = []
    if base_filename:
        potential_filenames.append(f"{base_filename}-header.webp")
        potential_filenames.append(f"{base_filename}-profile.webp")

        # 特定のプレフィックス (例: sukhumvit) の場合に例外的なファイル名を追加
        # ここでは prefix に "sukhumvit" が含まれるかで簡易的に判定
        if "sukhumvit" in base_filename.lower():
            potential_filenames.append("skhumvit-1536x864.webp")
            print(f"    - Added exceptional filename: skhumvit-1536x864.webp (for Sukhumvit projects)")

        print(f"  Potential featured image filenames (using English keywords prefix: '{base_filename}'):")
        for fname in potential_filenames:
            print(f"    - {fname}")
    else:
        print(f"  [Warning] Could not determine featured image filename prefix from English keywords for project associated with {generated_english_slug}. Cannot generate featured image names.")
    return potential_filenames

def get_media_id_by_filename(filename_to_search):
    """WordPressのメディアライブラリをファイル名で検索し、メディアIDを取得"""
    if not filename_to_search:
        return None
    print(f"  Searching for media with filename like: {filename_to_search}")
    try:
        # searchパラメータはファイル名の一部で検索できる（完全一致ではない）
        # WordPressのバージョンや設定によってはslugでの検索が有効な場合もある
        params = {'search': os.path.splitext(filename_to_search)[0]} # 拡張子なしで検索
        response = requests.get(API_MEDIA_ENDPOINT, params=params, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
        response.raise_for_status() # エラーがあれば例外発生
        media_items = response.json()

        if media_items:
            for item in media_items:
                # filenameは通常 basename(source_url) に近いが、完全一致を期待するのは難しい
                # title.rendered や slug での比較も考慮
                if filename_to_search.lower() in item.get('source_url', '').lower():
                    print(f"    Found media: ID={item['id']}, Title='{item['title']['rendered']}', URL={item['source_url']}")
                    return item['id']
            print(f"    Media items found with search term, but no exact filename match in source_url for '{filename_to_search}'.")
            # 最初に見つかったものを返すというのも一つの手だが、誤マッチの可能性もある
            # first_match_id = media_items[0]['id']
            # print(f"    Returning first found media ID as a fallback: {first_match_id}")
            # return first_match_id
        else:
            print(f"    No media found with search term: {os.path.splitext(filename_to_search)[0]}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [Error] API request to search media failed: {e}")
        return None
    except Exception as e:
        print(f"  [Error] Failed to get media ID for '{filename_to_search}': {e}")
        return None

def get_post_id_by_slug(slug, lang_code):
    """指定されたスラッグと言語コードでWordPressの投稿を検索し、存在すれば投稿IDを返す"""
    print(f"  Searching for existing post with slug: {slug} and language: {lang_code}")

    params = {
        'slug': slug,
        'status': 'any', # publish, future, draft, pending, private, trash
        '_fields': 'id' # 必要なのはIDだけなのでレスポンスを軽量化
    }

    # 言語コードに対応する Polylang タームIDを取得 (グローバル変数 POLYLANG_LANG_TERM_IDS を参照)
    term_id = POLYLANG_LANG_TERM_IDS.get(lang_code)

    if term_id:
        # Polylang REST API (無料版でも動作する可能性あり) の languages パラメータを使用
        # 注意: パラメータ名が 'language' (単数形) の可能性もあるため、動作しない場合は要確認
        params['languages'] = term_id 
        print(f"    Filtering by language term ID: {term_id}")
    else:
        # タームIDが見つからない場合 (英語などのデフォルト言語や設定漏れ)
        # デフォルト言語(en) の場合は、言語パラメータなしで検索するのが一般的
        # Polylangの設定によっては 'en' にもタームIDが割り当てられている場合もある
        if lang_code != 'en': # 仮に英語をデフォルトとし、それ以外の言語でIDが見つからない場合のみ警告
             print(f"    [Warning] Polylang term ID not found for language '{lang_code}'. Searching by slug only (might cause issues if slug is not unique across languages).")
        else:
             print(f"    Searching for default language ('{lang_code}') post by slug only.")


    try:
        response = requests.get(API_POSTS_ENDPOINT, params=params, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=10)
        response.raise_for_status()
        posts = response.json()
        if posts and isinstance(posts, list) and len(posts) > 0:
            # スラッグと言語で絞り込んでいるため、通常は1件のはず
            if len(posts) > 1:
                 print(f"    [Warning] Found multiple posts ({len(posts)}) with slug '{slug}' and language '{lang_code}' (term_id: {term_id}). Using the first one.")
            post_id = posts[0]['id']
            print(f"    Found existing post with ID: {post_id} for slug: {slug} and language: {lang_code}")
            return post_id
        else:
            print(f"    No existing post found with slug: {slug} and language: {lang_code}")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"  [Warning] HTTP error while searching for post by slug '{slug}' and lang '{lang_code}': {e.response.status_code} {e.response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  [Error] API request to search post by slug '{slug}' and lang '{lang_code}' failed: {e}")
        return None
    except Exception as e:
        print(f"  [Error] Failed to get post ID by slug '{slug}' and lang '{lang_code}': {e}")
        return None

def update_wordpress_post(post_id, post_data):
    """WordPressの既存の投稿を更新"""
    headers = {'Content-Type': 'application/json'}
    update_url = f"{API_POSTS_ENDPOINT}/{post_id}"
    try:
        print(f"  Attempting to update post ID: {post_id} with title: '{post_data.get('title')}'")
        print(f"    DEBUG: Update data being sent: {json.dumps(post_data, indent=2, ensure_ascii=False)}") # DEBUG PRINT
        # 更新時にはスラッグを送信データに含めない方が安全な場合がある（変更不可の場合や重複エラー回避）
        # ただし、今回はpost_dataにslugが含まれている前提でそのまま送る
        response = requests.post(update_url, headers=headers, json=post_data, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
        response.raise_for_status()
        updated_post = response.json()
        print(f"  Successfully updated post:")
        print(f"    ID: {updated_post['id']}")
        print(f"    Title: {updated_post['title']['rendered']}")
        print(f"    Status: {updated_post['status']}")
        print(f"    Link: {updated_post['link']}")
        print(f"    Edit Link: {WP_BASE_URL}/wp-admin/post.php?post={updated_post['id']}&action=edit")
        return updated_post['id']
    except requests.exceptions.HTTPError as e:
        print(f"  [Error] HTTP error updating post ID {post_id}: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            try:
                error_details = e.response.json()
                print(f"    Error details: {error_details}")
            except json.JSONDecodeError:
                print(f"    Error content (not JSON): {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"  [Error] API request to update post ID {post_id} failed: {e}")
    except Exception as e:
        print(f"  [Error] Failed to update WordPress post ID {post_id}: {e}")
    return None

def create_wordpress_post(post_data):
    """WordPressに新しい投稿を作成（下書きとして）"""
    headers = {'Content-Type': 'application/json'}
    try:
        print(f"  Attempting to create post: '{post_data['title']}'")
        print(f"    DEBUG: Create data being sent: {json.dumps(post_data, indent=2, ensure_ascii=False)}") # DEBUG PRINT
        response = requests.post(API_POSTS_ENDPOINT, headers=headers, json=post_data, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=30)
        response.raise_for_status()
        new_post = response.json()
        print(f"  Successfully created post (draft):")
        print(f"    ID: {new_post['id']}")
        print(f"    Title: {new_post['title']['rendered']}")
        print(f"    Status: {new_post['status']}")
        print(f"    Link: {new_post['link']}")
        print(f"    Edit Link: {WP_BASE_URL}/wp-admin/post.php?post={new_post['id']}&action=edit")
        return new_post['id']
    except requests.exceptions.HTTPError as e:
        print(f"  [Error] HTTP error creating post: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            try:
                error_details = e.response.json()
                print(f"    Error details: {error_details}")
            except json.JSONDecodeError:
                print(f"    Error content (not JSON): {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"  [Error] API request to create post failed: {e}")
    except Exception as e:
        print(f"  [Error] Failed to create WordPress post: {e}")
    return None

# --- Function to upload media to WordPress ---
def upload_media_to_wordpress(local_image_path, desired_filename):
    if not os.path.exists(local_image_path):
        print(f"    [Info] Local image not found at: {local_image_path}")
        return None

    print(f"  Attempting to upload local image: {local_image_path} as {desired_filename}")
    try:
        with open(local_image_path, 'rb') as img_file:
            mime_type, _ = mimetypes.guess_type(local_image_path)
            if not mime_type:
                mime_type = 'application/octet-stream' # Fallback
                print(f"    [Warning] Could not determine MIME type for {local_image_path}. Using {mime_type}.")

            files = {'file': (desired_filename, img_file, mime_type)}
            payload = {
                'title': os.path.splitext(desired_filename)[0],
                'alt_text': os.path.splitext(desired_filename)[0],
                'status': 'inherit'
            }

            if not API_MEDIA_ENDPOINT:
                print("    [Error] API_MEDIA_ENDPOINT is not configured. Cannot upload media.")
                return None

            response = requests.post(API_MEDIA_ENDPOINT, files=files, data=payload, auth=(WP_USERNAME, WP_APP_PASSWORD), timeout=60) # Increased timeout for upload
            response.raise_for_status()
            new_media_item = response.json()
            print(f"    Successfully uploaded media: ID={new_media_item['id']}, Title='{new_media_item['title']['rendered']}', URL={new_media_item['source_url']}")
            return new_media_item['id']
    except requests.exceptions.HTTPError as e:
        print(f"    [Error] HTTP error uploading media {desired_filename}: {e.response.status_code} {e.response.reason}")
        if e.response.content:
            try:
                error_details = e.response.json()
                print(f"        Error details: {error_details}")
            except json.JSONDecodeError:
                print(f"        Error content (not JSON): {e.response.text}")
        return None
    except FileNotFoundError:
        print(f"    [Error] Local image file not found during upload attempt: {local_image_path}")
        return None
    except Exception as e:
        print(f"    [Error] Failed to upload media {desired_filename}: {e}")
        return None

# --- メイン処理 ---
def main():
    print("Starting WordPress Uploader Script...")
    if not all([WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD]):
        print("[Error] Missing WordPress credentials or base URL. Set WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD.")
        return
    print(f"Target WordPress Site: {WP_BASE_URL}")
    print(f"Username: {WP_USERNAME}")



    output_translation_dir = os.path.join("translation", "output")
    if not os.path.isdir(output_translation_dir):
        print(f"[Error] Directory not found: {output_translation_dir}")
        return

    processed_projects_count = 0
    for project_name in sorted(os.listdir(output_translation_dir)):
        project_output_path = os.path.join(output_translation_dir, project_name)
        if not os.path.isdir(project_output_path):
            continue

        # --- Filtering logic for project_name ---
        match = re.match(r"^(\d+)_.*", project_name)
        if not match:
            print(f"  [Info] Skipping project with non-numeric prefix: {project_name}")
            continue

        try:
            project_number = int(match.group(1))
            if not (MIN_PROJECT_NUMBER <= project_number <= MAX_PROJECT_NUMBER):
                print(f"  [Info] Skipping project outside of range {MIN_PROJECT_NUMBER}-{MAX_PROJECT_NUMBER}: {project_name} (Number: {project_number})")
                continue
        except ValueError:
            print(f"  [Info] Skipping project with non-integer prefix: {project_name}")
            continue
        # --- End of filtering logic ---

        # プロジェクト内の全ての .html ファイルを処理対象とする
        for html_filename in sorted(os.listdir(project_output_path)):
            if not html_filename.endswith(".html"):
                continue

            lang_code_match = re.match(r"([a-z]{2}(?:-[a-z]{2})?)\.html", html_filename, re.IGNORECASE)
            if not lang_code_match:
                print(f"  [Info] Skipping file with non-standard lang code format: {html_filename} in {project_name}")
                continue
            
            current_lang_code = lang_code_match.group(1).lower()
            html_file_path = os.path.join(project_output_path, html_filename)

            print(f"\n--- Processing project: {project_name}, Language: {current_lang_code} ({html_filename}) ---")
            
            script_dir_for_path = os.path.dirname(os.path.abspath(__file__))
            workspace_root = os.path.dirname(script_dir_for_path)
            english_project_base_dir = os.path.join(workspace_root, project_name)
            english_project_data_input_dir = os.path.join(english_project_base_dir, "data_input")

            english_post_id = None
            if current_lang_code != "en":
                print(f"  Attempting to find the original English post for linking...")
                english_slug = generate_post_slug(english_project_data_input_dir)
                if english_slug:
                    print(f"    Generated English slug for original post: {english_slug}")
                    english_post_id = get_post_id_by_slug(english_slug, "en")
                    if english_post_id:
                        print(f"    Found English original post ID: {english_post_id}")
                    else:
                        print(f"    [Warning] English original post with slug '{english_slug}' not found. Cannot link translation for {project_name} ({current_lang_code}). The post will be created/updated without translation linkage.")
                else:
                    print(f"    [Warning] Could not generate English slug for original post for {project_name}. Cannot link translation.")
            elif current_lang_code == "en":
                 print(f"  Processing an English post. No translation linking needed for itself.")

            html_content = read_file_content(html_file_path)
            if not html_content:
                print(f"  [Error] Could not read or empty content: {html_file_path}")
                continue

            keywords_for_title_lang = current_lang_code
            keywords_data = get_keywords_for_title(english_project_data_input_dir, lang_to_get=current_lang_code)
            primary_keyword_for_title = keywords_data["primary"]
            secondary_keyword_for_title = keywords_data["secondary"]
            print(f"  Keywords for Title ({keywords_for_title_lang}): Primary='{primary_keyword_for_title}', Secondary='{secondary_keyword_for_title}'")

            num_sections = count_sections_in_html(html_content)
            print(f"  Number of sections (N for title): {num_sections}")
            if num_sections == 0:
                 print(f"  [Warning] No h2 tags for sections. Title might be generic for N.")

            post_title = generate_post_title(primary_keyword_for_title, secondary_keyword_for_title, num_sections, lang_code=current_lang_code)
            print(f"  Generated Post Title: {post_title}")
            
            post_slug = generate_post_slug(english_project_data_input_dir)
            print(f"  Generated Post Slug: {post_slug}")

            featured_media_id = None
            local_images_project_path = os.path.join(english_project_base_dir, "images") 
            local_images_data_input_path = os.path.join(english_project_data_input_dir) # For images directly in data_input

            potential_filenames = get_potential_featured_image_filenames(post_slug)
            
            if potential_filenames:
                for filename in potential_filenames:
                    media_id_found = get_media_id_by_filename(filename)
                    if media_id_found:
                        print(f"    Found Featured Media ID in WordPress: {media_id_found} for {filename}")
                        featured_media_id = media_id_found
                        break 
                    else:
                        print(f"    Media '{filename}' not found in WordPress. Checking locally...")
                        
                        # Define potential local paths
                        potential_local_paths = [
                            os.path.join(local_images_project_path, filename),       # project_name/images/filename
                            os.path.join(local_images_data_input_path, filename), # project_name/data_input/filename
                            os.path.join(english_project_base_dir, filename)    # project_name/filename
                        ]
                        
                        actual_local_path_found = None
                        for p_path in potential_local_paths:
                            if os.path.exists(p_path):
                                actual_local_path_found = p_path
                                break
                        
                        if actual_local_path_found:
                            print(f"      Found local image at: {actual_local_path_found}")
                            uploaded_media_id = upload_media_to_wordpress(actual_local_path_found, filename)
                            if uploaded_media_id:
                                print(f"      Successfully uploaded '{filename}' with new Media ID: {uploaded_media_id}")
                                featured_media_id = uploaded_media_id
                                break # Found and uploaded, so stop
                            else:
                                print(f"      Failed to upload local image '{filename}' from {actual_local_path_found}.")
                        else:
                            # Only print this if it's the last filename and still no image found/uploaded
                            if filename == potential_filenames[-1] and not featured_media_id:
                                print(f"      Local image for '{filename}' (and others) not found in expected locations for project {project_name}.")
                                print(f"        Checked paths based on: {local_images_project_path}, {local_images_data_input_path}, {english_project_base_dir}")
                
                if not featured_media_id:
                    print(f"  [Warning] Featured Media ID not found (and could not be uploaded) for any potential filenames: {potential_filenames} for project {project_name}")
            else:
                print(f"  [Warning] Could not determine any potential featured image filenames for project {project_name}.")

            post_data = {
                'title': post_title,
                'content': html_content,
                'status': 'publish',
                'slug': post_slug,
                'categories': [TARGET_CATEGORY_ID] if TARGET_CATEGORY_ID else [],
                'featured_media': featured_media_id if featured_media_id else 0,
                'meta': {
                    'rank_math_focus_keyword': primary_keyword_for_title if primary_keyword_for_title else ""
                }
            }
            
            if current_lang_code:
                post_data['polylang_lang_code'] = current_lang_code
            else:
                print(f"  [Warning] Language code could not be determined for {html_filename}. Language will not be set for this post.")
            
            if current_lang_code != "en" and english_post_id:
                post_data['polylang_translations'] = { "en": english_post_id }
                print(f"  Prepared to link this post as a translation of English post ID {english_post_id}")
            elif current_lang_code != "en" and not english_post_id:
                print(f"  [Info] Not linking translation as English original post ID was not found for {project_name}.")
            
            existing_post_id = get_post_id_by_slug(post_slug, current_lang_code)
            
            final_post_id = None
            if existing_post_id:
                print(f"  Post with slug '{post_slug}' already exists (ID: {existing_post_id}). Attempting to update.")
                update_data = post_data.copy()
                update_data['status'] = 'publish'
                final_post_id = update_wordpress_post(existing_post_id, update_data)
                if final_post_id:
                    print(f"  Post ID {existing_post_id} was successfully updated.")
                else:
                    print(f"  [Failed] Could not update post ID {existing_post_id} for {project_name} ({current_lang_code}).")
            else:
                print(f"  Post with slug '{post_slug}' does not exist. Attempting to create new post.")
                create_data = post_data.copy()
                create_data['status'] = 'publish'
                final_post_id = create_wordpress_post(create_data)
                if final_post_id:
                    print(f"  New post was successfully created with ID {final_post_id}.")
                else:
                    print(f"  [Failed] Could not create new post for {project_name} ({current_lang_code}).")

            if final_post_id:
                processed_projects_count += 1

    if processed_projects_count > 0:
        print(f"\nSuccessfully processed and attempted to upload {processed_projects_count} post(s).")
    elif not any(
        any(f.endswith(".html") for f in os.listdir(os.path.join(output_translation_dir, p)))
        for p in os.listdir(output_translation_dir)
        if os.path.isdir(os.path.join(output_translation_dir, p))
    ):
        print(f"\nNo projects with .html files found to process in {output_translation_dir}")
    else:
        print("\nNo posts were successfully processed or uploaded (HTML files might exist but processing failed).")
    
    print("\nWordPress Uploader Script Finished.")

if __name__ == "__main__":
    if not all([os.getenv("WP_BASE_URL"), os.getenv("WP_USERNAME"), os.getenv("WP_APP_PASSWORD")]) :
        print("----------------------------------------------------------------------")
        print("IMPORTANT: WordPress API credentials are not set as environment variables.")
        print("Please set: WP_BASE_URL, WP_USERNAME, WP_APP_PASSWORD")
        print("----------------------------------------------------------------------")
    main()

LANG_CODE = os.path.basename(os.path.dirname(__file__))
