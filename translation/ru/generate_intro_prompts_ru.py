import os
import csv
import unidecode
import re

TITLE_DIR = os.path.join(os.path.dirname(__file__), "title_results")
INTRO_PROMPT_DIR = os.path.join(os.path.dirname(__file__), "intro_prompts")
os.makedirs(INTRO_PROMPT_DIR, exist_ok=True)

AREA_TO_DIR = {
    'Sukkhumvit': '1_best_foot_massage_in_sukhumvit_2025',
    'Siam': '2_best_foot_massage_in_siam_2025',
    'Thong_Lor': '3_best_foot_massage_in_thonglor_2025',
    'Vat_Pkho': '4_best_foot_massage_near_wat_pho_2025',
    'Aeroport_Suvarnabkhumi': '5_best_foot_massage_near_suvarnabhumi_airport_2025',
    'Aeroport_Don_Muang': '6_best_foot_massage_near_don_mueang_airport_2025',
    'Sentral_Vorld': '7_best_foot_massage_near_central_world_2025',
    'Prompong': '8_best_foot_massage_near_phrom_phong_2025',
    'Asok': '9_best_foot_massage_in_asoke_2025',
    'Ko_Samui': '10_best_foot_massage_in_ko_samui_2025',
    'Ao_Nang': '11_best_foot_massage_in_ao_nang_2025',
    'Chiangmai': '12_best_foot_massage_in_chiang_mai_2025',
    'Pattaiia': '13_best_foot_massage_in_pattaya_2025',
    'Pkhuket': '14_best_foot_massage_in_phuket_2025',
    'Krabi': '15_best_foot_massage_in_krabi_2025',
    'Ko_Pkhangan': '16_best_foot_massage_in_koh_phangan_2025',
    'Ko_Tao': '17_best_foot_massage_in_koh_tao_2025',
    'Chiangrai': '18_best_foot_massage_in_chiang_rai_2025',
}

INTRO_TEMPLATE = '''必ずロシア語で出力してください。日本語で出力しないでください。

{ARTICLE_TITLE}というタイトルに相応しい魅力的なイントロダクション（導入文）を書いてください。

制約:
    • 自然なロシア語で、個人ブログのような、実際にタイに住んでいる人の目線で書いてください。
    • 出力は自然で会話調、感情がこもった、本物の人間が書いたような文章にしてください。
    • イントロの次に記載する[マッサージ店の特徴まとめ]の内容を、参考にしてください。
    • カジュアルなトーンで、親しみやすい雰囲気で書いて。ただし、馴れ馴れし過ぎないようにしてください。
    • ブログのターゲットは、この2パターン
        1. タイへの旅行客
        2. タイに既に在住している人
      これらの人の興味を引くような内容にしてください。
    • このブログの執筆者は、タイに3年住んでいて、この個人的な経験を活かすようにしてください。
    • {SEO_KEYWORDS_CONSTRAINT}
    • このブログの目的は、informational（情報提供）です。セールスやPRではありません。
    • 300から400字になるようにしてください。
    • 印象、感情、感想、体験などには、<strong><u></u></strong>と言うタグをつけて、読者にわかりやすくしてください。ただし、4-6回程度の頻度にして、文章として自然になるようにしてください。出だしの1文目には、必ず入れるようにしてください。
    • 前後に余計な情報を加えないでください。ブログのイントロ部分だけを出力してください。
    • 読みやすいように、2, 3文に一回は改行を入れてください。
    • パラグラフは、このフォーマットにしてください： <!-- wp:paragraph --><p>（ここに文章が入る）</p><!-- /wp:paragraph -->
    • "【在住者が選ぶ】バンコクのおすすめフットマッサージ10選【2025年】"と言うタイトルの、同じブログの別記事のリンクを挿入してください。これ以外のリンクは挿入しないでください。

リンク挿入について:
    下記のようなスタイルで、自然にリンクを挿入してください：
    <p>[ここに、短く、興味を引くような文章を書いてください。<a href="https://my-bangkok-life.com/ja/%e3%83%90%e3%83%b3%e3%82%b3%e3%82%af%e3%81%ae%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e3%83%95%e3%83%83%e3%83%88%e3%83%9e%e3%83%83%e3%82%b5%e3%83%bc%e3%82%b810%e9%81%b8/">[ここにアンカーテキストを入れてください。]</a>]</p>
    次の行に、下記のようなワードプレスのembed blockを書いてください。:

    <!-- wp:paragraph -->
        <p>
        <!-- wp:embed {"url":"https://my-bangkok-life.com/ja/%e3%83%90%e3%83%b3%e3%82%b3%e3%82%af%e3%81%ae%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e3%83%95%e3%83%83%e3%83%88%e3%83%9e%e3%83%83%e3%82%b5%e3%83%bc%e3%82%b810%e9%81%b8/","type":"wp-embed","providerNameSlug":"my-bangkok-life"} -->
            <figure class="wp-block-embed is-type-wp-embed is-provider-my-bangkok-life wp-block-embed-my-bangkok-life">
                <div class="wp-block-embed__wrapper">
                    https://my-bangkok-life.com/ja/%e3%83%90%e3%83%b3%e3%82%b3%e3%82%af%e3%81%ae%e3%81%8a%e3%81%99%e3%81%99%e3%82%81%e3%83%95%e3%83%83%e3%83%88%e3%83%9e%e3%83%83%e3%82%b5%e3%83%bc%e3%82%b810%e9%81%b8/
                </div>
            </figure>
        <!-- /wp:embed -->
        </p>
    <!-- /wp:paragraph -->

出力は、ここに保存してください:
translation/ru/temp/{PROJECT_NAME}/sections/intro/intro.html

[マッサージ店の特徴まとめ]
{ALL_SHOPS_FEATURES_AND_HIGHLIGHTS}
'''

def normalize_str(s):
    s = unidecode.unidecode(s).lower()
    s = re.sub(r'(.)\\1+', r'\\1', s)  # 連続文字を1つに
    return s

def get_all_shops_features_and_highlights(project_area):
    import glob
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
    area_norm = normalize_str(project_area)
    # 明示的なマッピングがあればそれを使う
    dir_name = AREA_TO_DIR.get(project_area, None)
    if dir_name and os.path.exists(os.path.join(base_dir, dir_name)):
        project_dir = os.path.join(base_dir, dir_name)
    else:
        def extract_romaji_part(dirname):
            parts = re.split(r'_|-|\\s', dirname)
            for p in parts[::-1]:
                p_norm = normalize_str(p)
                if area_norm in p_norm or p_norm in area_norm:
                    return True
            return False
        candidates = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and extract_romaji_part(d)]
        if not candidates:
            return "(特徴まとめデータなし)"
        project_dir = os.path.join(base_dir, candidates[0])
    summary_path = os.path.join(project_dir, "data_output", "summary_of_features_and_highlights_of_all_shops.txt")
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as f:
            return f.read().strip()
    csv_paths = [
        os.path.join(project_dir, "csv_creation", "top_rated_massage_shops.csv"),
        os.path.join(project_dir, "reviews_images_getter", "input", "top_rated_massage_shops.csv"),
        os.path.join(project_dir, "data_input", "shops.tsv"),
    ]
    shops_path = None
    for p in csv_paths:
        if os.path.exists(p):
            shops_path = p
            break
    if not shops_path:
        return "(特徴まとめデータなし)"
    features = []
    with open(shops_path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=',' if shops_path.endswith('.csv') else '\\t')
        for row in reader:
            name = row.get("Name", "")
            rating = row.get("Rating", "")
            reviews = row.get("Total Reviews", "")
            review1 = row.get("review_01", "")
            review2 = row.get("review_02", "")
            review3 = row.get("review_03", "")
            review_part = ""
            if review1:
                review_part += f"\n  - {review1}"
            if review2:
                review_part += f"\n  - {review2}"
            if review3:
                review_part += f"\n  - {review3}"
            features.append(f"・{name}（評価: {rating}, レビュー数: {reviews}）{review_part}")
    return "\n".join(features)

for fname in os.listdir(TITLE_DIR):
    if fname.startswith("title_ru_") and fname.endswith(".txt"):
        area = fname[len("title_ru_"):-len(".txt")]
        with open(os.path.join(TITLE_DIR, fname), encoding="utf-8") as f:
            title = f.read().strip()
        all_shops_features = get_all_shops_features_and_highlights(area)
        dir_name = AREA_TO_DIR.get(area, None)
        prompt = INTRO_TEMPLATE.replace("{ARTICLE_TITLE}", title).replace("{SEO_KEYWORDS_CONSTRAINT}", "").replace("{ALL_SHOPS_FEATURES_AND_HIGHLIGHTS}", all_shops_features)
        if dir_name:
            prompt = prompt.replace("{PROJECT_NAME}", dir_name)
        out_path = os.path.join(INTRO_PROMPT_DIR, f"body_intro_prompt_ru_{area}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(prompt)
        print(f"{out_path} にロシア語イントロ生成用プロンプトを出力しました。") 