import os
import shutil
import csv
import re
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

# Define target chapters
TARGET = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Define path constants
UPLOAD_DATE_PATH = "2025/05"

# Get project name and directory
PROJECT_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PROJECT_DIR, "data_output/images")
DATA_INPUT_DIR = os.path.join(PROJECT_DIR, "data_input")

def get_english_keywords():
    """Read English focus keywords from CSV file"""
    try:
        focus_keywords_path = os.path.join(DATA_INPUT_DIR, 'focus_keywords.csv')
        with open(focus_keywords_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Create a dictionary with stripped keys for case-insensitive access
            for row in reader:
                cleaned_row = {k.strip(): v for k, v in row.items()}
                if cleaned_row.get('language') == 'en':
                    primary = cleaned_row.get('Primary Focus Keyword', '').strip()
                    secondary = cleaned_row.get('Secondary Focus Keyword', '').strip()
                    # Convert to lowercase and replace spaces with hyphens
                    prefix = f"{primary}-{secondary}".lower().replace(' ', '-')
                    return prefix
    except Exception as e:
        errors_and_warnings.append(f"Error reading focus_keywords.csv: {e}")
        return "foot-massage-siam"  # fallback prefix

def get_image_mapping():
    """Create mappings of chapter numbers to image filenames and alt texts."""
    image_files = {}
    image_alts = {}
    
    # Get the prefix from focus keywords
    prefix = get_english_keywords()
    
    # Ensure the images directory exists
    if not os.path.exists(IMAGES_DIR):
        errors_and_warnings.append(f"Warning: Images directory {IMAGES_DIR} not found")
        return image_files, image_alts
    
    try:
        # List all webp files in the images directory
        for filename in os.listdir(IMAGES_DIR):
            if filename.endswith('.webp'):
                # Extract chapter number using regex with dynamic prefix
                match = re.search(fr'{prefix}-(\d+)-', filename)
                if match:
                    chapter_num = int(match.group(1))
                    image_files[chapter_num] = filename
                    # Convert filename to alt text by removing extension and replacing hyphens with spaces
                    alt_text = filename[:-4].replace('-', ' ')
                    image_alts[chapter_num] = alt_text
    except Exception as e:
        errors_and_warnings.append(f"Error reading images directory: {e}")
    
    return image_files, image_alts

# Get image mappings
IMAGE_FILENAMES, IMAGE_ALTS = get_image_mapping()

# Define template directory
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'prompt_script_template')
BASE_DIR = os.path.join(PROJECT_DIR, 'contents')

# Define base replacements
REPLACEMENTS = {}

def get_image_filename(target_chapter):
    """Generate the image filename based on target chapter."""
    try:
        # Get all webp files from the images directory
        image_files = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.webp')]
        
        # Find the file that matches the pattern XXX-{chapter}-YYY.webp
        for filename in image_files:
            # Extract chapter number from filename using regex
            match = re.search(r'-(\d+)-', filename)
            if match and int(match.group(1)) == target_chapter:
                return filename
        
        return ""  # Return empty string if no matching file found
    except Exception as e:
        errors_and_warnings.append(f"Error getting image filename for chapter {target_chapter}: {e}")
        return ""

def get_image_alt(target_chapter):
    """Generate the image alt text based on target chapter."""
    try:
        filename = get_image_filename(target_chapter)
        if filename:
            # Remove .webp extension and replace hyphens with spaces
            return filename[:-5].replace('-', ' ')
        return ""
    except Exception as e:
        errors_and_warnings.append(f"Error getting image alt text for chapter {target_chapter}: {e}")
        return ""

def read_summary_content():
    """Read the content of summary file."""
    try:
        summary_path = os.path.join(PROJECT_DIR, 'data_output/summary_of_features_and_highlights_of_all_shops.txt')
        with open(summary_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: {summary_path} not found")
        return ""
    except Exception as e:
        errors_and_warnings.append(f"Error reading summary file: {e}")
        return ""

def read_tsv_row(target_chapter):
    """Read the specific row from shops.tsv based on target chapter."""
    try:
        shops_tsv_path = os.path.join(DATA_INPUT_DIR, 'shops.tsv')
        with open(shops_tsv_path, 'r', encoding='utf-8') as f:
            tsv_reader = csv.reader(f, delimiter='\t')
            # Skip header row
            header = next(tsv_reader)
            # Get row based on target chapter (row index = target chapter + 1)
            for i, row in enumerate(tsv_reader, start=1):
                if i == target_chapter:
                    if row:  # Check if row is not empty
                        return {
                            'full_row': '\t'.join(row),
                            'shop_name': row[0] if len(row) > 0 else "",
                            'iframe_code': row[8] if len(row) > 8 else ""  # Changed from index 5 to 8 for Embed Code column
                        }
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: {shops_tsv_path} not found")
    except Exception as e:
        errors_and_warnings.append(f"Error reading TSV file: {e}")
    return {'full_row': "", 'shop_name': "", 'iframe_code': ""}

def perform_replacements(content, target_chapter):
    """Replace template placeholders with actual values."""
    try:
        # Create a copy of base replacements
        current_replacements = REPLACEMENTS.copy()
        
        # Add dynamic output file name
        current_replacements['[TEMPLATE_OUTPUT_FILE_NAME]'] = f'{PROJECT_NAME}/contents/{target_chapter:02d}_1_intro/summary.txt'
        
        # Get TSV data
        tsv_data = read_tsv_row(target_chapter)
        
        # Add shop name from TSV
        current_replacements['[TEMPLATE_SHOP_NAME]'] = tsv_data['shop_name']
        
        # Add dynamic image URL and alt text
        image_filename = get_image_filename(target_chapter)
        if image_filename:  # Only set the URL if we have a valid image filename
            current_replacements['[TEMPLATE_IMAGE_URL]'] = f'https://my-bangkok-life.com/wp-content/uploads/{UPLOAD_DATE_PATH}/{image_filename}'
        else:
            errors_and_warnings.append(f"Warning: No image filename found for chapter {target_chapter}")
            current_replacements['[TEMPLATE_IMAGE_URL]'] = ""  # Set empty string if no image found
        current_replacements['[TEMPLATE_IMAGE_ALT]'] = get_image_alt(target_chapter)
        
        # Add iframe code from TSV
        current_replacements['[TEMPLATE_IFRAME_CODE]'] = tsv_data['iframe_code']
        
        # Apply standard replacements
        for placeholder, value in current_replacements.items():
            content = content.replace(placeholder, value)
        
        # Replace summary content
        summary_content = read_summary_content()
        content = content.replace('[TEMPLATE_SUMMARY_OF_FEATURES_AND_HIGHLIGHTS_OF_ALL_SHOPS]', summary_content)
        
        # Replace TSV row content
        content = content.replace('[TARGET_SHOP_TSV_ROW]', tsv_data['full_row'])
        
        return content
    except Exception as e:
        errors_and_warnings.append(f"Error performing replacements for chapter {target_chapter}: {e}")
        return content

def create_directory_structure():
    try:
        # Create directories and files for each target chapter
        for chapter in TARGET:
            sections = [
                (f"{chapter:02d}_1_intro", "intro"),
                (f"{chapter:02d}_2_reviews", "reviews")
            ]
            
            for section_dir, section_type in sections:
                try:
                    # Create directory
                    full_dir_path = os.path.join(BASE_DIR, section_dir)
                    os.makedirs(full_dir_path, exist_ok=True)
                    print(f"Created directory: {full_dir_path}")
                    
                    # Select the appropriate template files based on section type
                    if section_type == "intro":
                        template_files = ['generate_html_intro.py', 'prompt_to_generate_txt_intro.txt']
                    else:  # reviews
                        template_files = ['generate_html_reviews.py', 'prompt_to_generate_txt_reviews.txt']
                    
                    # Copy and modify template files to each section
                    for template_file in template_files:
                        source_path = os.path.join(TEMPLATE_DIR, template_file)
                        # Remove type suffix from filenames
                        if template_file.endswith('.py'):
                            dest_filename = 'generate_html.py'
                        elif template_file.endswith('_intro.txt'):
                            dest_filename = 'prompt_to_generate_txt.txt'
                        else:
                            dest_filename = template_file
                        dest_path = os.path.join(full_dir_path, dest_filename)
                        
                        if os.path.exists(source_path):
                            # Read template content
                            try:
                                with open(source_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # Perform replacements
                                modified_content = perform_replacements(content, chapter)
                                
                                # Write modified content
                                with open(dest_path, 'w', encoding='utf-8') as f:
                                    f.write(modified_content)
                                print(f"Created and modified file: {dest_path}")
                            except Exception as e:
                                errors_and_warnings.append(f"Error processing template file {source_path}: {e}")
                        else:
                            errors_and_warnings.append(f"Warning: Template file {source_path} not found")
                except Exception as e:
                    errors_and_warnings.append(f"Error processing section {section_dir}: {e}")
    except Exception as e:
        errors_and_warnings.append(f"Error creating directory structure: {str(e)}")
        errors_and_warnings.append(traceback.format_exc())

if __name__ == "__main__":
    try:
        # Make sure directories exist
        os.makedirs(BASE_DIR, exist_ok=True)
        print(f"Script is running from: {PROJECT_DIR}")
        print(f"Data input directory: {DATA_INPUT_DIR}")
        print(f"Images directory: {IMAGES_DIR}")
        create_directory_structure()
        print("Script execution completed")
    except Exception as e:
        errors_and_warnings.append(f"Unexpected error: {str(e)}")
        errors_and_warnings.append(traceback.format_exc())
    
    # Print any errors or warnings in red at the end
    if errors_and_warnings:
        print(f"\n{Colors.RED}Errors and warnings during execution:{Colors.RESET}")
        for item in errors_and_warnings:
            print(f"{Colors.RED}{item}{Colors.RESET}")
