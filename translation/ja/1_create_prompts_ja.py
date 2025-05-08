import os
import shutil
import glob
import csv # For reading focus_keywords.csv

# Configuration
# shops_file_path will be dynamic
# output_base_dir will be dynamic
# project_name will be dynamic

# 修正: テンプレートディレクトリのパスを移動後の構成に合わせる
template_dir = os.path.join(os.path.dirname(__file__), 'prompt_templates')
reviews_template_filename = "prompt_to_translate_reviews.txt"
summary_template_filename = "prompt_to_translate_summary.txt"
intro_html_template_filename = "prompt_to_generate_intro_html.txt" # New template
conclusion_html_template_filename = "prompt_to_generate_conclusion_html.txt" # New template
temp_base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp") # translation/temp

def process_project(project_name):
    print(f"\n--- Processing project: {project_name} ---")
    shops_file_path = os.path.join(project_name, "data_input", "shops.tsv")
    # Output base for prompts related to this project
    project_temp_dir = os.path.join(temp_base_dir, project_name)
    output_sections_base_dir = os.path.join(project_temp_dir, "sections") 
    all_shops_summary_file_path = os.path.join(project_name, "data_output", "summary_of_features_and_highlights_of_all_shops.txt")
    focus_keywords_file_path = os.path.join(project_name, "data_input", "focus_keywords.csv") # New path

    # Paths for new templates
    reviews_template_path = os.path.join(template_dir, reviews_template_filename)
    summary_template_path = os.path.join(template_dir, summary_template_filename)
    intro_html_template_path = os.path.join(template_dir, intro_html_template_filename)
    conclusion_html_template_path = os.path.join(template_dir, conclusion_html_template_filename)

    # --- File Existence Checks ---
    required_files = {
        "Shops TSV": shops_file_path,
        "All Shops Summary": all_shops_summary_file_path,
        "Focus Keywords CSV": focus_keywords_file_path,
        "Reviews Template": reviews_template_path, # Though checked in main, good to have here if process_project is called independently
        "Summary Template": summary_template_path,
        "Intro HTML Template": intro_html_template_path,
        "Conclusion HTML Template": conclusion_html_template_path
    }
    for file_desc, file_path in required_files.items():
        if not os.path.exists(file_path):
            print(f"ERROR: {file_desc} file not found for project {project_name} at {file_path}. Skipping project.")
            return 0

    # --- Read Content --- 
    with open(reviews_template_path, 'r', encoding='utf-8') as f: reviews_template_content_base = f.read()
    with open(summary_template_path, 'r', encoding='utf-8') as f: summary_template_content_base = f.read()
    with open(intro_html_template_path, 'r', encoding='utf-8') as f: intro_html_template_content_base = f.read()
    with open(conclusion_html_template_path, 'r', encoding='utf-8') as f: conclusion_html_template_content_base = f.read()
    with open(all_shops_summary_file_path, 'r', encoding='utf-8') as f: all_shops_summary_block_content = f.read()
    with open(shops_file_path, 'r', encoding='utf-8') as f: shops_lines = f.readlines()
    
    # --- Process focus_keywords.csv ---    
    primary_topic_keyword = "" # e.g., フットマッサージ, ヘッドスパ
    secondary_location_keyword = "" # e.g., サイアム, スクンビット
    seo_keywords_list_for_constraint = []
    try:
        with open(focus_keywords_file_path, 'r', encoding='utf-8-sig') as csvfile: # Use utf-8-sig for BOM handling
            reader = csv.DictReader(csvfile)
            # Sanitize fieldnames to remove leading/trailing whitespace
            if reader.fieldnames:
                reader.fieldnames = [fieldname.strip() for fieldname in reader.fieldnames]
            
            found_ja = False
            for row in reader:
                if row.get('language','').strip().lower() == 'ja':
                    found_ja = True
                    primary_topic_keyword = row.get('Primary Focus Keyword', '').strip()
                    secondary_location_keyword = row.get('Secondary Focus Keyword', '').strip()
                    
                    if primary_topic_keyword:
                        seo_keywords_list_for_constraint.append(primary_topic_keyword)
                    if secondary_location_keyword:
                        seo_keywords_list_for_constraint.append(secondary_location_keyword) # Add location to SEO list too
                    break # Found Japanese row, no need to continue
            if not found_ja:
                print(f"Warning: No 'ja' language row found in {focus_keywords_file_path} for {project_name}.")
    except FileNotFoundError:
        print(f"ERROR: Focus keywords file not found at {focus_keywords_file_path}. Skipping project {project_name}.")
        return 0
    except Exception as e:
        print(f"ERROR: Could not read/process {focus_keywords_file_path}: {e}")
        return 0

    if not primary_topic_keyword:
        print(f"Warning: Primary Focus Keyword (topic) for 'ja' is empty/missing in {focus_keywords_file_path} for {project_name}. Title/SEO affected.")
        primary_topic_keyword = "[トピック]" # Placeholder if empty
    if not secondary_location_keyword:
        print(f"Warning: Secondary Focus Keyword (location) for 'ja' is empty/missing in {focus_keywords_file_path} for {project_name}. Title affected.")
        secondary_location_keyword = "[場所]" # Placeholder if empty

    if not seo_keywords_list_for_constraint:
        seo_keywords_constraint_text = "SEOキーワードを意識して作成してください。" 
    else:
        seo_keywords_constraint_text = "SEOのキーワードは、" + "と".join([f'"{kw}"' for kw in seo_keywords_list_for_constraint]) + "を必ず含めてください。"

    # --- Process shops.tsv (for count and iteration) ---
    if not shops_lines:
        print(f"ERROR: Shops file is empty: {shops_file_path}. Skipping project.")
        return 0
    shops_tsv_header = shops_lines[0].strip()
    shop_data_lines = [line for line in shops_lines[1:] if line.strip()] # Filter out empty lines
    num_shops = len(shop_data_lines)

    # --- Construct Article Title (REVISED LOGIC) --- 
    article_title = f'”【在住者が選ぶ】{secondary_location_keyword}の{primary_topic_keyword}おすすめ{num_shops}選【2025年版】”'

    # --- Generate Intro Prompt --- 
    output_intro_dir = os.path.join(output_sections_base_dir, "intro")
    os.makedirs(output_intro_dir, exist_ok=True)
    intro_prompt_path = os.path.join(output_intro_dir, "prompt_to_generate_intro_html.txt")
    intro_prompt_content = intro_html_template_content_base.replace("{ARTICLE_TITLE}", article_title)
    intro_prompt_content = intro_prompt_content.replace("{PROJECT_NAME}", project_name)
    intro_prompt_content = intro_prompt_content.replace("{SEO_KEYWORDS_CONSTRAINT}", seo_keywords_constraint_text)
    intro_prompt_content = intro_prompt_content.replace("{ALL_SHOPS_FEATURES_AND_HIGHLIGHTS}", all_shops_summary_block_content)
    with open(intro_prompt_path, 'w', encoding='utf-8') as f: f.write(intro_prompt_content)
    print(f"Generated: {intro_prompt_path}")

    # --- Generate Conclusion Prompt --- 
    output_conclusion_dir = os.path.join(output_sections_base_dir, "conclusion") 
    os.makedirs(output_conclusion_dir, exist_ok=True)
    conclusion_prompt_path = os.path.join(output_conclusion_dir, "prompt_to_generate_conclusion_html.txt")
    conclusion_prompt_content = conclusion_html_template_content_base.replace("{ARTICLE_TITLE}", article_title)
    conclusion_prompt_content = conclusion_prompt_content.replace("{PROJECT_NAME}", project_name)
    conclusion_prompt_content = conclusion_prompt_content.replace("{SEO_KEYWORDS_CONSTRAINT}", seo_keywords_constraint_text)
    conclusion_prompt_content = conclusion_prompt_content.replace("{ALL_SHOPS_FEATURES_AND_HIGHLIGHTS}", all_shops_summary_block_content)
    with open(conclusion_prompt_path, 'w', encoding='utf-8') as f: f.write(conclusion_prompt_content)
    print(f"Generated: {conclusion_prompt_path}")

    # --- Generate Shop-Specific Prompts & Collect Paths --- 
    summary_prompt_paths = []
    reviews_prompt_paths = []
    for i, shop_tsv_data_line in enumerate(shop_data_lines):
        section_num = i + 1
        shop_tsv_data_line = shop_tsv_data_line.strip()

        try:
            shop_name = shop_tsv_data_line.split('\t')[0]
        except IndexError:
            shop_name = f"Shop_{section_num}"
            print(f"Warning: Could not parse shop name for section {section_num} in {project_name} from line: {shop_tsv_data_line}")

        output_section_dir = os.path.join(output_sections_base_dir, str(section_num), "ja")
        os.makedirs(output_section_dir, exist_ok=True)
        
        # Reviews Prompt
        reviews_prompt_path = os.path.join(output_section_dir, "prompt_to_translate_reviews.txt")
        reviews_prompt_content = reviews_template_content_base.replace("{PROJECT_NAME}", project_name)
        reviews_prompt_content = reviews_prompt_content.replace("{SECTION_NUM}", str(section_num))
        reviews_prompt_content = reviews_prompt_content.replace("{SHOP_TSV_DATA}", f"{shops_tsv_header}\n{shop_tsv_data_line}")
        with open(reviews_prompt_path, 'w', encoding='utf-8') as f: f.write(reviews_prompt_content)
        print(f"Generated: {reviews_prompt_path}")
        reviews_prompt_paths.append(reviews_prompt_path)

        # Summary Prompt
        summary_prompt_path = os.path.join(output_section_dir, "prompt_to_translate_summary.txt")
        summary_prompt_content = summary_template_content_base.replace("{PROJECT_NAME}", project_name)
        summary_prompt_content = summary_prompt_content.replace("{SHOP_NAME}", shop_name)
        summary_prompt_content = summary_prompt_content.replace("{SECTION_NUM}", str(section_num))
        summary_prompt_content = summary_prompt_content.replace("{ALL_SHOPS_FEATURES_AND_HIGHLIGHTS}", all_shops_summary_block_content)
        summary_prompt_content = summary_prompt_content.replace("{SHOPS_TSV_HEADER}", shops_tsv_header)
        summary_prompt_content = summary_prompt_content.replace("{SHOP_TSV_DATA}", shop_tsv_data_line)
        with open(summary_prompt_path, 'w', encoding='utf-8') as f: f.write(summary_prompt_content)
        print(f"Generated: {summary_prompt_path}")
        summary_prompt_paths.append(summary_prompt_path)

    # --- Generate Execution Instruction Files --- 
    instruction_header = "Read the following prompt files and run them one by one:\n\n"
    instruction_footer = "\n\nEach file contains a specific generation task. Follow the instructions inside each prompt exactly as written."

    # 1_prompt_to_generate_intro_conclusion.txt
    instruction_file_1_path = os.path.join(project_temp_dir, "1_prompt_to_generate_intro_conclusion.txt")
    with open(instruction_file_1_path, 'w', encoding='utf-8') as f:
        f.write(instruction_header)
        f.write(f"1. {intro_prompt_path}\n")
        f.write(f"2. {conclusion_prompt_path}\n")
        f.write(instruction_footer)
    print(f"Generated: {instruction_file_1_path}")
    
    # 2_prompt_to_generate_shop_summaries.txt
    instruction_file_2_path = os.path.join(project_temp_dir, "2_prompt_to_generate_shop_summaries.txt")
    with open(instruction_file_2_path, 'w', encoding='utf-8') as f:
        f.write(instruction_header)
        for idx, path in enumerate(summary_prompt_paths):
            f.write(f"{idx + 1}. {path}\n")
        f.write(instruction_footer)
    print(f"Generated: {instruction_file_2_path}")

    # 3_prompt_to_generate_reviews.txt
    instruction_file_3_path = os.path.join(project_temp_dir, "3_prompt_to_generate_reviews.txt")
    with open(instruction_file_3_path, 'w', encoding='utf-8') as f:
        f.write(instruction_header)
        for idx, path in enumerate(reviews_prompt_paths):
            f.write(f"{idx + 1}. {path}\n")
        f.write(instruction_footer)
    print(f"Generated: {instruction_file_3_path}")

    # --- Verification Step ---
    print(f"\n--- Verifying generated files for project: {project_name} ---")
    files_to_verify = []
    files_to_verify.extend([intro_prompt_path, conclusion_prompt_path])
    files_to_verify.extend(summary_prompt_paths)
    files_to_verify.extend(reviews_prompt_paths)
    files_to_verify.append(instruction_file_1_path)
    files_to_verify.append(instruction_file_2_path)
    files_to_verify.append(instruction_file_3_path)

    missing_files_count = 0
    # Remove duplicates (e.g. if intro/conclusion were somehow added twice) and sort for consistent checking
    unique_files_to_verify = sorted(list(set(files_to_verify)))

    for f_path in unique_files_to_verify:
        if not os.path.exists(f_path):
            print(f"VERIFICATION ERROR: File not found: {f_path}")
            missing_files_count += 1
    
    if missing_files_count == 0:
        print("Verification successful: All expected files are present.")
    else:
        print(f"VERIFICATION FAILED: {missing_files_count} file(s) missing for project {project_name}.")
    
    return missing_files_count

def main():
    # Clean and recreate the base temp directory
    if os.path.exists(temp_base_dir):
        print(f"ERROR: Directory {temp_base_dir} already exists. Please remove it manually before running the script.")
        return # Exit if directory exists
    os.makedirs(temp_base_dir)
    print(f"Created empty directory: {temp_base_dir}")

    # Check for base template files once before starting
    base_template_files = [
        os.path.join(template_dir, reviews_template_filename),
        os.path.join(template_dir, summary_template_filename),
        os.path.join(template_dir, intro_html_template_filename),
        os.path.join(template_dir, conclusion_html_template_filename)
    ]
    for tpl_path in base_template_files:
        if not os.path.exists(tpl_path):
            print(f"ERROR: Base template file not found: {tpl_path}. Aborting.")
            return

    project_pattern = "*_best_*_*_2025"
    project_directories = sorted([d for d in glob.glob(project_pattern) if os.path.isdir(d)]) # Sort for consistent order

    if not project_directories:
        print(f"No project directories found matching pattern '{project_pattern}' in the current directory.")
        original_project_name = "1_best_foot_massage_in_sukhumvit_2025"
        if os.path.isdir(original_project_name):
            print(f"Attempting to process the default project: {original_project_name}")
            process_project(original_project_name)
        else:
            print(f"Default project {original_project_name} also not found.")
        return

    total_missing_files_overall = 0
    projects_processed_count = 0
    projects_with_missing_files_count = 0

    for project_name in project_directories:
        missing_count_for_project = process_project(project_name)
        if missing_count_for_project > 0:
            total_missing_files_overall += missing_count_for_project
            projects_with_missing_files_count += 1
        projects_processed_count += 1
        
    print("\n--- Overall Script Summary ---")
    if projects_processed_count == 0:
        print("No projects were processed.")
    else:
        print(f"Processed {projects_processed_count} project(s).")
        if total_missing_files_overall == 0:
            print("All expected files generated and verified successfully for all processed projects.")
        else:
            print(f"WARNING: A total of {total_missing_files_overall} expected file(s) were NOT found "
                  f"across {projects_with_missing_files_count} project(s).")
            print("Please review the 'VERIFICATION ERROR' messages above for details on missing files.")

    print("Done generating prompts for all projects.")

if __name__ == "__main__":
    main()
