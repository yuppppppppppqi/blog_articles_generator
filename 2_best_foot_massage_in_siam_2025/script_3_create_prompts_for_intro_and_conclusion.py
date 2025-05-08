import os
import json
import shutil
import csv

# Read settings
def read_settings(file_path):
    settings = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                settings[key.strip()] = value.strip()
    
    # Read min number of reviews
    with open('csv_creation/min_num_of_reviews.txt', 'r', encoding='utf-8') as f:
        settings['MIN_NUM_OF_REVIEWS'] = f.read().strip()
    
    return settings

# Read focus keywords from CSV
def read_focus_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            if row['language'] == 'en':  # Get English keywords
                return row['Primary Focus Keyword'].strip(), row[' Secondary Focus Keyword'].strip()
    return None, None

# Read summary of features and highlights
def read_summary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

# Create directories if they don't exist
def ensure_directories(base_path):
    os.makedirs(os.path.join(base_path, 'contents', 'intro'), exist_ok=True)
    os.makedirs(os.path.join(base_path, 'contents', 'conclusion'), exist_ok=True)

# Read template file
def read_template(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Replace placeholders in template
def replace_placeholders(template, settings, primary_keyword, secondary_keyword, summary):
    replacements = {
        '[TEMPLATE_TITLE_BLOG_EN]': settings['TEMPLATE_TITLE_BLOG_EN'],
        '[TEMPLATE_INTERNAL_LINK_IN_INTRO_TITLE]': settings['TEMPLATE_INTERNAL_LINK_IN_INTRO_TITLE'],
        '[TEMPLATE_INTERNAL_LINK_IN_INTRO_URL]': settings['TEMPLATE_INTERNAL_LINK_IN_INTRO_URL'],
        '[TEMPLATE_INTERNAL_LINK_IN_CONCLUSION_URL]': settings['TEMPLATE_INTERNAL_LINK_IN_CONCLUSION_URL'],
        '[TEMPLATE_NUMBER_OF_MIN_REVIEWS]': settings['MIN_NUM_OF_REVIEWS'],
        '[TEMPLATE_PRIMARY_FOCUS_KEYWORD]': primary_keyword,
        '[TEMPLATE_SECONDARY_FOCUS_KEYWORD]': secondary_keyword,
        '[TEMPLATE_SUMMARY_OF_FEATURES_AND_HIGHLIGHTS_OF_ALL_SHOPS]': summary
    }
    
    result = template
    for key, value in replacements.items():
        if value is not None:  # Only replace if value exists
            result = result.replace(key, value)
    return result

def copy_h2_script(base_path):
    source = os.path.join(base_path, 'prompt_script_template', 'add_h2_in_conclusion.py')
    destination = os.path.join(base_path, 'contents', 'conclusion', 'add_h2.py')
    shutil.copy2(source, destination)

def main():
    base_path = '.'  # Current directory
    
    # Read settings
    settings = read_settings(os.path.join(base_path, 'data_input', 'settings.txt'))
    
    # Read focus keywords
    primary_keyword, secondary_keyword = read_focus_keywords(os.path.join(base_path, 'data_input', 'focus_keywords.csv'))
    
    # Read summary
    summary = read_summary(os.path.join(base_path, 'data_output', 'summary_of_features_and_highlights_of_all_shops.txt'))
    
    # Ensure directories exist
    ensure_directories(base_path)
    
    # Process intro template
    intro_template = read_template(os.path.join(base_path, 'prompt_script_template', 'prompt_to_generate_html_intro_of_all.txt'))
    intro_content = replace_placeholders(intro_template, settings, primary_keyword, secondary_keyword, summary)
    
    # Process conclusion template
    conclusion_template = read_template(os.path.join(base_path, 'prompt_script_template', 'prompt_to_generate_html_conclusion.txt'))
    conclusion_content = replace_placeholders(conclusion_template, settings, primary_keyword, secondary_keyword, summary)
    
    # Write the generated files
    with open(os.path.join(base_path, 'contents', 'intro', 'prompt_to_generate_html.txt'), 'w', encoding='utf-8') as f:
        f.write(intro_content)
    
    with open(os.path.join(base_path, 'contents', 'conclusion', 'prompt_to_generate_html.txt'), 'w', encoding='utf-8') as f:
        f.write(conclusion_content)
    
    # Copy the add_h2_in_conclusion.py script
    copy_h2_script(base_path)

if __name__ == '__main__':
    main()
