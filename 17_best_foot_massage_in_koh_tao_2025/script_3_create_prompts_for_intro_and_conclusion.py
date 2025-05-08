import os
import json
import shutil
import csv
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

# Read settings
def read_settings(file_path):
    settings = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    settings[key.strip()] = value.strip()
        
        # Read min number of reviews
        try:
            with open('csv_creation/min_num_of_reviews.txt', 'r', encoding='utf-8') as f:
                settings['MIN_NUM_OF_REVIEWS'] = f.read().strip()
        except FileNotFoundError:
            errors_and_warnings.append("Warning: csv_creation/min_num_of_reviews.txt not found")
            settings['MIN_NUM_OF_REVIEWS'] = "0"  # Default value
        except Exception as e:
            errors_and_warnings.append(f"Error reading min_num_of_reviews.txt: {e}")
            settings['MIN_NUM_OF_REVIEWS'] = "0"  # Default value
        
        return settings
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: Settings file {file_path} not found")
        return {}
    except Exception as e:
        errors_and_warnings.append(f"Error reading settings file: {e}")
        return {}

# Read focus keywords from CSV
def read_focus_keywords(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if row['language'] == 'en':  # Get English keywords
                    return row['Primary Focus Keyword'].strip(), row[' Secondary Focus Keyword'].strip()
        errors_and_warnings.append("Warning: No English focus keywords found in CSV file")
        return None, None
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: Focus keywords file {file_path} not found")
        return None, None
    except Exception as e:
        errors_and_warnings.append(f"Error reading focus keywords file: {e}")
        return None, None

# Read summary of features and highlights
def read_summary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: Summary file {file_path} not found")
        return ""
    except Exception as e:
        errors_and_warnings.append(f"Error reading summary file: {e}")
        return ""

# Create directories if they don't exist
def ensure_directories(base_path):
    try:
        os.makedirs(os.path.join(base_path, 'contents', 'intro'), exist_ok=True)
        os.makedirs(os.path.join(base_path, 'contents', 'conclusion'), exist_ok=True)
    except Exception as e:
        errors_and_warnings.append(f"Error creating directories: {e}")

# Read template file
def read_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: Template file {file_path} not found")
        return ""
    except Exception as e:
        errors_and_warnings.append(f"Error reading template file: {e}")
        return ""

# Replace placeholders in template
def replace_placeholders(template, settings, primary_keyword, secondary_keyword, summary):
    try:
        replacements = {
            '[TEMPLATE_TITLE_BLOG_EN]': settings.get('TEMPLATE_TITLE_BLOG_EN', ''),
            '[TEMPLATE_INTERNAL_LINK_IN_INTRO_TITLE]': settings.get('TEMPLATE_INTERNAL_LINK_IN_INTRO_TITLE', ''),
            '[TEMPLATE_INTERNAL_LINK_IN_INTRO_URL]': settings.get('TEMPLATE_INTERNAL_LINK_IN_INTRO_URL', ''),
            '[TEMPLATE_INTERNAL_LINK_IN_CONCLUSION_URL]': settings.get('TEMPLATE_INTERNAL_LINK_IN_CONCLUSION_URL', ''),
            '[TEMPLATE_NUMBER_OF_MIN_REVIEWS]': settings.get('MIN_NUM_OF_REVIEWS', '0'),
            '[TEMPLATE_PRIMARY_FOCUS_KEYWORD]': primary_keyword if primary_keyword else '',
            '[TEMPLATE_SECONDARY_FOCUS_KEYWORD]': secondary_keyword if secondary_keyword else '',
            '[TEMPLATE_SUMMARY_OF_FEATURES_AND_HIGHLIGHTS_OF_ALL_SHOPS]': summary
        }
        
        result = template
        for key, value in replacements.items():
            if value is not None:  # Only replace if value exists
                result = result.replace(key, value)
        return result
    except Exception as e:
        errors_and_warnings.append(f"Error replacing placeholders: {e}")
        return template

def copy_h2_script(base_path):
    try:
        source = os.path.join(base_path, 'prompt_script_template', 'add_h2_in_conclusion.py')
        destination = os.path.join(base_path, 'contents', 'conclusion', 'add_h2.py')
        
        if not os.path.exists(source):
            errors_and_warnings.append(f"Warning: Source script {source} not found")
            return
            
        shutil.copy2(source, destination)
    except Exception as e:
        errors_and_warnings.append(f"Error copying H2 script: {e}")

def main():
    try:
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
        try:
            with open(os.path.join(base_path, 'contents', 'intro', 'prompt_to_generate_html.txt'), 'w', encoding='utf-8') as f:
                f.write(intro_content)
            
            with open(os.path.join(base_path, 'contents', 'conclusion', 'prompt_to_generate_html.txt'), 'w', encoding='utf-8') as f:
                f.write(conclusion_content)
                
            print("Successfully created prompt files for intro and conclusion")
        except Exception as e:
            errors_and_warnings.append(f"Error writing output files: {e}")
        
        # Copy the add_h2_in_conclusion.py script
        copy_h2_script(base_path)
    
    except Exception as e:
        errors_and_warnings.append(f"Unexpected error: {str(e)}")
        errors_and_warnings.append(traceback.format_exc())

if __name__ == '__main__':
    main()
    
    # Print any errors or warnings in red at the end
    if errors_and_warnings:
        print(f"\n{Colors.RED}Errors and warnings during execution:{Colors.RESET}")
        for item in errors_and_warnings:
            print(f"{Colors.RED}{item}{Colors.RESET}")
