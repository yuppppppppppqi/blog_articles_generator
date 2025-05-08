import os
import csv

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'prompt_script_template', 'prompt_to_generate_metadata.txt')
INTRO_PATH = os.path.join(os.path.dirname(__file__), 'contents', 'intro', 'intro.html')
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), 'data_input', 'focus_keywords.csv')
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'data_input', 'settings.txt')
# Output to the root directory
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'prompt_to_generate_metadata.txt')

def main():
    # Read the template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    # Read the intro
    with open(INTRO_PATH, 'r', encoding='utf-8') as f:
        intro = f.read().strip()
    
    # Read primary focus keyword for English from CSV
    primary_keyword = ""
    with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip header
        for row in csv_reader:
            if row[0].strip() == 'en':
                primary_keyword = row[1].strip()
                break
    
    # Read blog title from settings.txt
    blog_title = ""
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('TEMPLATE_TITLE_BLOG_EN'):
                blog_title = line.split('=')[1].strip()
                break
    
    # Replace the template placeholders with actual values
    template = template.replace('[TEMPLATE_PRIMARY_KEYWORD]', primary_keyword)
    template = template.replace('[TEMPLATE_TITLE_BLOG_EN]', blog_title)
    
    # Combine template and intro
    new_prompt = template.strip() + '\n' + intro
    
    # Write the new prompt
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(new_prompt)

if __name__ == '__main__':
    main()
