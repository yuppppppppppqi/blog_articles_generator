import os

prompt_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "temp",
    "1_best_foot_massage_in_sukhumvit_2025",
    "sections",
    "intro",
    "prompt_to_generate_intro_html_ru.txt"
)

with open(prompt_path, "r", encoding="utf-8") as f:
    print(f.read()) 