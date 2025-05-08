import os

def read_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_tsv(tsv_path):
    with open(tsv_path, 'r', encoding='utf-8') as f:
        return f.read()

def create_prompt(template, tsv_content):
    return template.replace('[TARGET_SHOP_TSV_ROW]', tsv_content)

def ensure_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def main():
    # Define paths using absolute paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = script_dir
    template_path = os.path.join(base_dir, 'prompt_script_template', 'prompt_for_features_highlights_of_shops.txt')
    tsv_path = os.path.join(base_dir, 'data_input', 'shops.tsv')
    output_dir = os.path.join(base_dir, 'data_output')
    output_path = os.path.join(output_dir, 'prompt_for_features_highlights_of_shops.txt')

    # Read template and TSV content
    template = read_template(template_path)
    tsv_content = read_tsv(tsv_path)

    # Create prompt by replacing placeholder
    prompt = create_prompt(template, tsv_content)

    # Ensure output directory exists
    ensure_output_dir(output_dir)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

if __name__ == '__main__':
    main()
