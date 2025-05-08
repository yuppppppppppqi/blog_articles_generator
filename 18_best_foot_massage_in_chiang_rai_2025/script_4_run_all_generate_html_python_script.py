import os
import subprocess
import re
import sys
import traceback

# ANSI color codes
class Colors:
    RED = '\033[91m'
    RESET = '\033[0m'

# Store errors and warnings
errors_and_warnings = []

def run_generate_html_files():
    try:
        # Get the base directory
        base_dir = os.path.join(os.path.dirname(__file__), 'contents')
        
        # Pattern to match XX_1_intro and XX_2_reviews directories
        pattern = re.compile(r'\d+_[12]_(intro|reviews)$')
        
        # Store directories to process
        target_dirs = []
        
        # Find all matching directories
        try:
            for item in os.listdir(base_dir):
                full_path = os.path.join(base_dir, item)
                if os.path.isdir(full_path) and pattern.match(item):
                    target_dirs.append(full_path)
        except FileNotFoundError:
            errors_and_warnings.append(f"Error: Base directory {base_dir} not found")
            return
        except Exception as e:
            errors_and_warnings.append(f"Error reading directory {base_dir}: {e}")
            return
        
        # Sort directories to process them in order
        target_dirs.sort()
        
        if not target_dirs:
            errors_and_warnings.append(f"Warning: No matching directories found in {base_dir}")
        
        # Store current working directory
        original_dir = os.getcwd()
        
        # Process each directory
        for directory in target_dirs:
            print(f"Processing {directory}...")
            try:
                # Change to the target directory
                os.chdir(directory)
                
                # Check if the generate_html.py script exists
                if not os.path.exists('generate_html.py'):
                    errors_and_warnings.append(f"Error: generate_html.py not found in {directory}")
                    continue
                
                # Run the generate_html.py script
                subprocess.run(['python', 'generate_html.py'], check=True)
                print(f"Successfully processed {directory}")
                
            except subprocess.CalledProcessError as e:
                errors_and_warnings.append(f"Error processing {directory}: {e}")
            except Exception as e:
                errors_and_warnings.append(f"Error: {e}")
            finally:
                # Always return to original directory
                os.chdir(original_dir)

        # After all generate_html.py scripts are done, run add_h2.py in the conclusion directory
        conclusion_dir = os.path.join(base_dir, 'conclusion')
        if os.path.exists(conclusion_dir):
            try:
                print("Running add_h2.py in conclusion directory...")
                os.chdir(conclusion_dir)
                
                # Check if the add_h2.py script exists
                if not os.path.exists('add_h2.py'):
                    errors_and_warnings.append(f"Error: add_h2.py not found in {conclusion_dir}")
                else:
                    subprocess.run(['python', 'add_h2.py'], check=True)
                    print("Successfully added H2 to conclusion")
            except subprocess.CalledProcessError as e:
                errors_and_warnings.append(f"Error adding H2 to conclusion: {e}")
            except Exception as e:
                errors_and_warnings.append(f"Error: {e}")
            finally:
                os.chdir(original_dir)
        else:
            errors_and_warnings.append(f"Warning: Conclusion directory {conclusion_dir} not found")
    
    except Exception as e:
        errors_and_warnings.append(f"Unexpected error: {str(e)}")
        errors_and_warnings.append(traceback.format_exc())

if __name__ == '__main__':
    run_generate_html_files()
    
    # Print any errors or warnings in red at the end
    if errors_and_warnings:
        print(f"\n{Colors.RED}Errors and warnings during execution:{Colors.RESET}")
        for item in errors_and_warnings:
            print(f"{Colors.RED}{item}{Colors.RESET}") 