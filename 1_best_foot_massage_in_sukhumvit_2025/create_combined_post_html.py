import os
import re

def read_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}")
        return ""

def get_sorted_content_dirs(contents_dir):
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

def combine_html_files():
    # Define the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    contents_dir = os.path.join(base_dir, 'contents')
    
    # Start with intro
    file_order = ['intro/intro.html']
    
    # Add sorted content directories
    content_dirs = get_sorted_content_dirs(contents_dir)
    for dir_name in content_dirs:
        if '_1_intro' in dir_name:
            file_order.append(f'{dir_name}/summary.html')
        elif '_2_reviews' in dir_name:
            file_order.append(f'{dir_name}/reviews.html')
    
    # End with conclusion
    file_order.append('conclusion/conclusion_with_h2.html')
    
    # Combine the HTML content
    combined_html = []
    for file_path in file_order:
        full_path = os.path.join(contents_dir, file_path)
        content = read_html_file(full_path)
        combined_html.append(content)
    
    # Write the combined content to a file in the contents directory
    output_path = os.path.join(contents_dir, 'combined_post.html')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write('\n'.join(combined_html))
    
    print(f"Combined HTML has been written to: {output_path}")
    print("Files combined in this order:")
    for file in file_order:
        print(f"- {file}")

if __name__ == "__main__":
    combine_html_files()
