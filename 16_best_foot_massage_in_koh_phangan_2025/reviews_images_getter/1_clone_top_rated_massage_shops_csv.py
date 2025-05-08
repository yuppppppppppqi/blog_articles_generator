import shutil
import os

# Define source and destination paths
src = os.path.join(os.path.dirname(__file__), '../csv_creation/top_rated_massage_shops.csv')
dst = os.path.join(os.path.dirname(__file__), 'input/top_rated_massage_shops.csv')

# Ensure the destination directory exists
os.makedirs(os.path.dirname(dst), exist_ok=True)

# Copy the file
shutil.copy2(src, dst)
print(f"Cloned CSV from {src} to {dst}")
