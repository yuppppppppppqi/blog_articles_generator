import os
import re
import shutil
import csv
from PIL import Image
import glob
import pillow_avif  # AVIF support auto-registration

# Directory configurations using relative paths
INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_input", "images")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_output", "images")
SHOPS_TSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_input", "shops.tsv")
SETTINGS_TXT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_input", "settings.txt")

def get_image_name_prefix():
    """Read IMAGE_NAME_PREFIX from settings.txt file"""
    try:
        with open(SETTINGS_TXT, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('IMAGE_NAME_PREFIX'):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading settings.txt: {e}")
        return "image"

def read_shop_names():
    """Read shop names from the TSV file"""
    shop_names = []
    try:
        with open(SHOPS_TSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                shop_names.append(row['Name'])
        return shop_names
    except Exception as e:
        print(f"Error reading shops.tsv: {e}")
        return []

def clean_filename(name, index, prefix):
    # First remove any characters that are not alphanumeric or spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    
    # Add a prefix and format the filename
    cleaned = f"{prefix}-{index + 1}-{cleaned}"
    
    # Replace spaces with hyphens
    cleaned = cleaned.replace(" ", "-")
    
    # Ensure the filename is lowercase for consistency
    cleaned = cleaned.lower()
    
    # Replace multiple consecutive hyphens with a single hyphen
    cleaned = re.sub(r'-+', '-', cleaned)
    
    return cleaned

def convert_to_webp(input_path, output_path):
    """Convert image to WebP format"""
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Convert RGBA or LA mode to RGB
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode == 'P':
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(output_path, 'webp', quality=80)
        print(f"Conversion successful: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
    except Exception as e:
        print(f"Conversion error {os.path.basename(input_path)}: {str(e)}")

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def process_images():
    print(f"Output directory: {OUTPUT_DIR}")
    # Create output directory if it doesn't exist
    ensure_directory_exists(OUTPUT_DIR)

    # Delete all files in the output directory before saving new files
    for filename in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    
    # Get prefix from IMAGE_NAME_PREFIX in settings.txt
    prefix = get_image_name_prefix()
    
    # Get list of all image files in input directory
    input_files = []
    for ext in ['*.png', '*.PNG', '*.jpg', '*.jpeg', '*.avif', '*.gif', '*.bmp']:
        input_files.extend(glob.glob(os.path.join(INPUT_DIR, ext)))
    input_files.sort()
    
    if not input_files:
        print("No image files found in input directory")
        return
    
    print(f"Found {len(input_files)} image files to process...")
    
    # Read shop names from TSV file for named files
    massage_shops = read_shop_names()
    
    # Process all image files
    for i, source_path in enumerate(input_files):
        original_filename = os.path.basename(source_path)
        print(f"\nProcessing file {i + 1}: {original_filename}")
        
        # Check if the filename matches the pattern of numbered files (e.g., "1.png", "2.avif")
        number_match = re.match(r'^(\d+)\.(png|avif)$', original_filename)
        if number_match:
            # Get the actual number from filename
            file_number = int(number_match.group(1)) - 1  # Convert to 0-based index
            # If we have a corresponding shop name, use it for the filename
            if file_number < len(massage_shops):
                new_base_name = clean_filename(massage_shops[file_number], file_number, prefix)
            else:
                # For additional numbered files without shop names
                new_base_name = f"{prefix}-{file_number + 1}"
        else:
            # For files that don't match the numbered pattern, keep original name with prefix
            base_name = os.path.splitext(original_filename)[0]
            new_base_name = f"{prefix}-{base_name}"
        
        # Final WebP path
        final_path = os.path.join(OUTPUT_DIR, new_base_name + '.webp')
        
        try:
            # Convert directly to WebP
            convert_to_webp(source_path, final_path)
        except Exception as e:
            print(f"Error processing file: {e}")

if __name__ == "__main__":
    process_images()
    print("All processing completed.") 