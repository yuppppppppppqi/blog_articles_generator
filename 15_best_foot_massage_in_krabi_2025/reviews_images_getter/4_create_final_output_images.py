import os
import json
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FINAL_OUTPUT_DIR = os.path.join(BASE_DIR, 'final_output')
SELECTED_IMAGES_JSON = os.path.join(OUTPUT_DIR, 'selected_images.json')

# Ensure final_output directory exists
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)

# Read selected_images.json
with open(SELECTED_IMAGES_JSON, 'r') as f:
    selected_images = json.load(f)

for idx, entry in enumerate(selected_images):
    if idx >= 10:
        break
    shop = entry['shop']
    image = entry['image']
    src_path = os.path.join(OUTPUT_DIR, shop, 'modified', image)
    dst_filename = f"{idx + 1}.png"
    dst_path = os.path.join(FINAL_OUTPUT_DIR, dst_filename)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied {src_path} to {dst_path}")
    else:
        print(f"Warning: {src_path} does not exist!")
