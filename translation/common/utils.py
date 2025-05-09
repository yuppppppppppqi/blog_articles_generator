import os


def load_template(template_dir, filename):
    """指定ディレクトリからテンプレートファイルを読み込む"""
    path = os.path.join(template_dir, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def ensure_dir(path):
    """ディレクトリがなければ作成する"""
    os.makedirs(path, exist_ok=True)


def load_languages_from_polylang_ids(path):
    """polylang_language_ids.txt から言語コードリストを取得"""
    langs = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    code = line.split(':')[0].strip()
                    if code:
                        langs.append(code)
    except Exception as e:
        print(f"Warning: Could not read languages from {path}: {e}")
    return langs or ["ja"] 