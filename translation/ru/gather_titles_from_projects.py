import os
import shutil

# translation/ru/ 配下に保存先ディレクトリ
RU_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "title_results")
os.makedirs(RU_RESULTS_DIR, exist_ok=True)
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")

# プロジェクトディレクトリを列挙
project_dirs = [d for d in os.listdir(PROJECT_ROOT) if d.endswith("_2025") and os.path.isdir(os.path.join(PROJECT_ROOT, d))]

for project in sorted(project_dirs):
    # エリア名をディレクトリ名から推測（例: 1_best_foot_massage_in_sukhumvit_2025 → sukhumvit）
    area = project.split("_in_")[-1].replace("_2025", "").replace("_near_", "_")
    # 入力ファイル
    src = os.path.join(PROJECT_ROOT, project, "data_output", "title_prompts", "title_ru.txt")
    # 出力ファイル
    dst = os.path.join(RU_RESULTS_DIR, f"title_ru_{area}.txt")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"{src} → {dst} コピー完了")
    else:
        print(f"[SKIP] {src} が見つかりません") 