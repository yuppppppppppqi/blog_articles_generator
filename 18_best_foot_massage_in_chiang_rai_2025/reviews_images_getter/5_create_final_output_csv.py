import pandas as pd
import json
import re

# File paths
csv_path = 'reviews_images_getter/input/top_rated_massage_shops.csv'
reviews_json_path = 'reviews_images_getter/output/all_reviews.json'
selected_images_path = 'reviews_images_getter/output/selected_images.json'
output_csv_path = 'reviews_images_getter/final_output/shops.tsv'

# 1. Read input files
# Read CSV
df = pd.read_csv(csv_path)

# Replace newlines in all string columns
df = df.applymap(lambda x: x.replace('\n', ' ').replace('\r', ' ') if isinstance(x, str) else x)

# Read all_reviews.json
with open(reviews_json_path, 'r') as f:
    all_reviews = json.load(f)

# Read selected_images.json
with open(selected_images_path, 'r') as f:
    selected_images = json.load(f)

# 2. Extract Place ID from Google Maps Link
# Example link: https://www.google.com/maps/place/?q=place_id:ChIJN1t_tDeuEmsRUsoyG83frY4
# Extract the part after 'place_id:'
def extract_place_id(link):
    match = re.search(r'place_id:([\w-]+)', str(link))
    return match.group(1) if match else None

df['place_id'] = df['Google Maps Link'].apply(extract_place_id)

# 3. Attach reviews from all_reviews.json
# Instead of 'all_reviews', fill review_01, review_02, ...
review_cols = [f'review_{i:02d}' for i in range(1, 21)]

def clean_text(text):
    return str(text).replace('\n', ' ').replace('\r', ' ').replace(',', ' ')

def get_review_list(place_id):
    entry = all_reviews.get(place_id, {})
    reviews = entry.get('reviews', [])
    return [clean_text(r['text']) for r in reviews][:20] if reviews else []

for idx, row in df.iterrows():
    place_id = row['place_id']
    reviews = get_review_list(place_id)
    for i, col in enumerate(review_cols):
        df.at[idx, col] = reviews[i] if i < len(reviews) else ''

# 4. Reorder rows based on selected_images.json
# selected_images is a list of dicts: {"shop": "shop07", ...}
# We assume shopXX means the original index (1-based)
# We'll create a mapping from shopXX to DataFrame index
shop_to_index = {}
for idx, row in df.iterrows():
    shop_num = idx + 1  # 1-based
    shop_to_index[f'shop{shop_num:02d}'] = idx

# Build new order
new_order = []
for entry in selected_images[:10]:
    shop = entry['shop']
    idx = shop_to_index.get(shop)
    if idx is not None:
        new_order.append(idx)

# Reorder DataFrame
reordered_df = df.loc[new_order].reset_index(drop=True)

# Ensure output has the same columns and order as the input CSV
reordered_df = reordered_df[df.columns]

# 5. Write the output TSV
reordered_df.to_csv(output_csv_path, index=False, sep='\t')

print(f"Final output written to {output_csv_path}")

# Remove the old all_reviews column if it exists
if 'all_reviews' in df.columns:
    df = df.drop(columns=['all_reviews'])
