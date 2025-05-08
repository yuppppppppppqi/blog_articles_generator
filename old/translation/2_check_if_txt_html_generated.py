import os

BASE_DIR = "translation/temp"
EXCLUDE_PROJECTS = [
    "1_best_foot_massage_in_sukhumvit_2025",
    "2_best_foot_massage_in_siam_2025",
    "3_best_foot_massage_in_thonglor_2025",
]

REQUIRED_HTML_FILES = [
    "sections/intro/intro.html",
    "sections/conclusion/conclusion.html",
]

SECTION_SUBDIR_RANGE = range(1, 11) # 1 to 10

def check_project(project_name):
    project_path = os.path.join(BASE_DIR, project_name)
    results = {"project_name": project_name, "missing_files": [], "present_files": []}
    all_ok = True

    # 2. Check required HTML files
    for html_file_rel_path in REQUIRED_HTML_FILES:
        file_path = os.path.join(project_path, html_file_rel_path)
        if os.path.exists(file_path):
            results["present_files"].append(html_file_rel_path)
        else:
            results["missing_files"].append(html_file_rel_path)
            all_ok = False

    # 3. Check section files (summary.txt and reviews.txt for x=1 to 10)
    for i in SECTION_SUBDIR_RANGE:
        section_dir_path = os.path.join(project_path, "sections", str(i))
        if not os.path.isdir(section_dir_path):
            missing_path = os.path.join("sections", str(i))
            results["missing_files"].append(f"Directory: {missing_path}")
            all_ok = False
            # If section 'x' directory itself is missing, its contents are also missing
            results["missing_files"].append(os.path.join(missing_path, "ja", "summary.txt"))
            results["missing_files"].append(os.path.join(missing_path, "ja", "reviews.txt"))
            continue # No need to check for files if directory is missing

        summary_file_rel_path = os.path.join("sections", str(i), "ja", "summary.txt")
        summary_file_path = os.path.join(project_path, summary_file_rel_path)
        if os.path.exists(summary_file_path):
            results["present_files"].append(summary_file_rel_path)
        else:
            results["missing_files"].append(summary_file_rel_path)
            all_ok = False

        reviews_file_rel_path = os.path.join("sections", str(i), "ja", "reviews.txt")
        reviews_file_path = os.path.join(project_path, reviews_file_rel_path)
        if os.path.exists(reviews_file_path):
            results["present_files"].append(reviews_file_rel_path)
        else:
            results["missing_files"].append(reviews_file_rel_path)
            all_ok = False
            
    results["all_ok"] = all_ok
    return results

def main():
    if not os.path.isdir(BASE_DIR):
        print(f"Error: Base directory '{BASE_DIR}' not found.")
        return

    project_names = [
        d for d in os.listdir(BASE_DIR)
        if os.path.isdir(os.path.join(BASE_DIR, d)) and d not in EXCLUDE_PROJECTS
    ]

    if not project_names:
        print(f"No projects found in '{BASE_DIR}' (excluding {EXCLUDE_PROJECTS}).")
        return

    print(f"Checking {len(project_names)} projects...\\n")

    all_projects_summary = []

    for project_name in sorted(project_names):
        print(f"--- Checking Project: {project_name} ---")
        result = check_project(project_name)
        all_projects_summary.append(result)
        
        if result["all_ok"]:
            print("Status: OK - All required files are present.")
        else:
            print("Status: NG - Some files are missing.")
            if result["missing_files"]:
                print("  Missing files/directories:")
                for mf in sorted(list(set(result["missing_files"]))): # Use set to avoid duplicates if section dir and its files are missing
                    print(f"    - {mf}")
        # Optional: print present files if needed for debugging
        # if result["present_files"]:
        #     print("  Present files:")
        #     for pf in sorted(result["present_files"]):
        #         print(f"    - {pf}")
        print("\\n")

    print("--- Summary ---")
    fully_ok_projects = [p["project_name"] for p in all_projects_summary if p["all_ok"]]
    not_ok_projects_count = len(project_names) - len(fully_ok_projects)

    if fully_ok_projects:
        print(f"Projects with all files present ({len(fully_ok_projects)}):")
        for p_name in sorted(fully_ok_projects):
            print(f"  - {p_name}")
    else:
        print("No projects have all required files present.")

    if not_ok_projects_count > 0:
        print(f"\\nProjects with missing files ({not_ok_projects_count}).")
    
    print(f"\\nTotal projects checked: {len(project_names)}")


if __name__ == "__main__":
    main()
