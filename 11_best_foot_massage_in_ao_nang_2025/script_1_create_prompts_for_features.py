import os
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

def read_template(template_path):
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        errors_and_warnings.append(f"Error reading template file: {str(e)}")
        return ""

def read_tsv(tsv_path):
    try:
        with open(tsv_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        errors_and_warnings.append(f"Error reading TSV file: {str(e)}")
        return ""

def create_prompt(template, tsv_content):
    if not template:
        errors_and_warnings.append("Warning: Template is empty")
    if not tsv_content:
        errors_and_warnings.append("Warning: TSV content is empty")
    return template.replace('[TARGET_SHOP_TSV_ROW]', tsv_content)

def ensure_output_dir(output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except Exception as e:
        errors_and_warnings.append(f"Error creating output directory: {str(e)}")

def main():
    try:
        # Define paths using absolute paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = script_dir
        template_path = os.path.join(base_dir, 'prompt_script_template', 'prompt_for_features_highlights_of_shops.txt')
        tsv_path = os.path.join(base_dir, 'data_input', 'shops.tsv')
        output_dir = os.path.join(base_dir, 'data_output')
        output_path = os.path.join(output_dir, 'prompt_for_features_highlights_of_shops.txt')

        # Check if paths exist
        if not os.path.exists(template_path):
            errors_and_warnings.append(f"Error: Template file not found at {template_path}")
        if not os.path.exists(tsv_path):
            errors_and_warnings.append(f"Error: TSV file not found at {tsv_path}")

        # Read template and TSV content
        template = read_template(template_path)
        tsv_content = read_tsv(tsv_path)

        # Create prompt by replacing placeholder
        prompt = create_prompt(template, tsv_content)

        # Ensure output directory exists
        ensure_output_dir(output_dir)

        # Write output
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"Prompt successfully created at: {output_path}")
        except Exception as e:
            errors_and_warnings.append(f"Error writing output file: {str(e)}")
    
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
