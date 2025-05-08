import os
import csv
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'prompt_script_template', 'prompt_to_generate_metadata.txt')
INTRO_PATH = os.path.join(os.path.dirname(__file__), 'contents', 'intro', 'intro.html')
KEYWORDS_PATH = os.path.join(os.path.dirname(__file__), 'data_input', 'focus_keywords.csv')
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'data_input', 'settings.txt')
# Output to the root directory
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data_output/prompt_to_generate_metadata.txt')

def main():
    try:
        # Check if paths exist
        if not os.path.exists(TEMPLATE_PATH):
            errors_and_warnings.append(f"Error: Template file not found at {TEMPLATE_PATH}")
            return
        if not os.path.exists(INTRO_PATH):
            errors_and_warnings.append(f"Error: Intro file not found at {INTRO_PATH}")
            return
        if not os.path.exists(KEYWORDS_PATH):
            errors_and_warnings.append(f"Error: Keywords file not found at {KEYWORDS_PATH}")
            return
        if not os.path.exists(SETTINGS_PATH):
            errors_and_warnings.append(f"Error: Settings file not found at {SETTINGS_PATH}")
            return
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(OUTPUT_PATH)
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                errors_and_warnings.append(f"Error creating output directory: {e}")
                return
        
        # Read the template
        try:
            with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            errors_and_warnings.append(f"Error reading template file: {e}")
            return
            
        # Read the intro
        try:
            with open(INTRO_PATH, 'r', encoding='utf-8') as f:
                intro = f.read().strip()
        except Exception as e:
            errors_and_warnings.append(f"Error reading intro file: {e}")
            intro = ""  # Set default empty value
        
        # Read primary focus keyword for English from CSV
        primary_keyword = ""
        try:
            with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Skip header
                for row in csv_reader:
                    if row[0].strip() == 'en':
                        primary_keyword = row[1].strip()
                        break
                if not primary_keyword:
                    errors_and_warnings.append("Warning: No English primary keyword found in CSV")
        except Exception as e:
            errors_and_warnings.append(f"Error reading keywords file: {e}")
        
        # Read blog title from settings.txt
        blog_title = ""
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('TEMPLATE_TITLE_BLOG_EN'):
                        blog_title = line.split('=')[1].strip()
                        break
                if not blog_title:
                    errors_and_warnings.append("Warning: Blog title not found in settings.txt")
        except Exception as e:
            errors_and_warnings.append(f"Error reading settings file: {e}")
        
        # Replace the template placeholders with actual values
        template = template.replace('[TEMPLATE_PRIMARY_KEYWORD]', primary_keyword)
        template = template.replace('[TEMPLATE_TITLE_BLOG_EN]', blog_title)
        
        # Combine template and intro
        new_prompt = template.strip() + '\n' + intro
        
        # Write the new prompt
        try:
            with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
                f.write(new_prompt)
            print(f"Metadata prompt successfully created at: {OUTPUT_PATH}")
        except Exception as e:
            errors_and_warnings.append(f"Error writing output file: {e}")
            
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
