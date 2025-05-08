import os
import re
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

def read_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        errors_and_warnings.append(f"Warning: File not found: {file_path}")
        return ""
    except Exception as e:
        errors_and_warnings.append(f"Error reading file {file_path}: {e}")
        return ""

def get_sorted_content_dirs(contents_dir):
    try:
        # Get all directories in contents
        all_dirs = [d for d in os.listdir(contents_dir) 
                    if os.path.isdir(os.path.join(contents_dir, d))]
        
        # Filter and sort content directories
        content_dirs = []
        for d in all_dirs:
            # Match pattern XX_1_intro or XX_2_reviews where XX is any number
            if re.match(r'\d+_[12]_(?:intro|reviews)', d):
                content_dirs.append(d)
        
        # Sort directories numerically
        content_dirs.sort(key=lambda x: (int(x.split('_')[0]), int(x.split('_')[1])))
        return content_dirs
    except FileNotFoundError:
        errors_and_warnings.append(f"Error: Contents directory not found: {contents_dir}")
        return []
    except Exception as e:
        errors_and_warnings.append(f"Error getting content directories: {e}")
        return []

def combine_html_files():
    try:
        # Define the base directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        contents_dir = os.path.join(base_dir, 'contents')
        
        # Check if contents directory exists
        if not os.path.exists(contents_dir):
            errors_and_warnings.append(f"Error: Contents directory not found: {contents_dir}")
            return
        
        # Start with intro
        file_order = ['intro/intro.html']
        
        # Add sorted content directories
        content_dirs = get_sorted_content_dirs(contents_dir)
        if not content_dirs:
            errors_and_warnings.append("Warning: No content directories found to combine")
            
        for dir_name in content_dirs:
            if '_1_intro' in dir_name:
                file_order.append(f'{dir_name}/summary.html')
            elif '_2_reviews' in dir_name:
                file_order.append(f'{dir_name}/reviews.html')
        
        # End with conclusion
        file_order.append('conclusion/conclusion_with_h2.html')
        
        # Combine the HTML content
        combined_html = []
        missing_files = []
        
        for file_path in file_order:
            full_path = os.path.join(contents_dir, file_path)
            content = read_html_file(full_path)
            if not content:
                missing_files.append(file_path)
            combined_html.append(content)
        
        # Check if we found any content
        if not any(combined_html):
            errors_and_warnings.append("Error: No HTML content found to combine")
            return
            
        if missing_files:
            errors_and_warnings.append(f"Warning: {len(missing_files)} files were missing or empty")
        
        # Write the combined content to a file in the contents directory
        output_path = os.path.join(contents_dir, 'combined_post.html')
        try:
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write('\n'.join(combined_html))
            
            print(f"Combined HTML has been written to: {output_path}")
            print("Files combined in this order:")
            for file in file_order:
                print(f"- {file}")
        except Exception as e:
            errors_and_warnings.append(f"Error writing combined HTML file: {e}")
            
    except Exception as e:
        errors_and_warnings.append(f"Unexpected error: {str(e)}")
        errors_and_warnings.append(traceback.format_exc())

if __name__ == "__main__":
    combine_html_files()
    
    # Print any errors or warnings in red at the end
    if errors_and_warnings:
        print(f"\n{Colors.RED}Errors and warnings during execution:{Colors.RESET}")
        for item in errors_and_warnings:
            print(f"{Colors.RED}{item}{Colors.RESET}")
