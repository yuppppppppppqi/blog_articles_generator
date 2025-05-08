import os
import subprocess
import re

def run_generate_html_files():
    # Get the base directory
    base_dir = os.path.join(os.path.dirname(__file__), 'contents')
    
    # Pattern to match XX_1_intro and XX_2_reviews directories
    pattern = re.compile(r'\d+_[12]_(intro|reviews)$')
    
    # Store directories to process
    target_dirs = []
    
    # Find all matching directories
    for item in os.listdir(base_dir):
        full_path = os.path.join(base_dir, item)
        if os.path.isdir(full_path) and pattern.match(item):
            target_dirs.append(full_path)
    
    # Sort directories to process them in order
    target_dirs.sort()
    
    # Store current working directory
    original_dir = os.getcwd()
    
    # Process each directory
    for directory in target_dirs:
        print(f"Processing {directory}...")
        try:
            # Change to the target directory
            os.chdir(directory)
            
            # Run the generate_html.py script
            subprocess.run(['python', 'generate_html.py'], check=True)
            print(f"Successfully processed {directory}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {directory}: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Always return to original directory
            os.chdir(original_dir)

if __name__ == '__main__':
    run_generate_html_files() 