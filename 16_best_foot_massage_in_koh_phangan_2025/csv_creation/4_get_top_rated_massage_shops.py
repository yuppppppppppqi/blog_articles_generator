import pandas as pd
import os

# Constants for shop number thresholds
MIN_NUMBER_OF_SHOPS = 12
MAX_NUMBER_OF_SHOPS = 25

def filter_and_sort_shops(input_file, output_file, min_reviews=200):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Convert Total Reviews to numeric
    df['Total Reviews'] = pd.to_numeric(df['Total Reviews'])
    
    # Filter shops with minimum number of reviews
    df_filtered = df[df['Total Reviews'] >= min_reviews]
    
    # Check if we have between MIN_NUMBER_OF_SHOPS-MAX_NUMBER_OF_SHOPS shops
    shop_count = len(df_filtered)
    
    # Adjust min_reviews if needed to get between MIN_NUMBER_OF_SHOPS-MAX_NUMBER_OF_SHOPS shops
    while shop_count < MIN_NUMBER_OF_SHOPS and min_reviews > 50:
        min_reviews -= 50
        df_filtered = df[df['Total Reviews'] >= min_reviews]
        shop_count = len(df_filtered)
    
    while shop_count > MAX_NUMBER_OF_SHOPS and min_reviews < 1000:
        min_reviews += 50
        df_filtered = df[df['Total Reviews'] >= min_reviews]
        shop_count = len(df_filtered)
    
    # Sort by Rating in descending order
    final_result = df_filtered.sort_values('Rating', ascending=False)
    
    print(f"Found {len(final_result)} shops with {min_reviews}+ reviews")
    
    # Add 20 empty review columns
    for i in range(1, 21):
        column_name = f'review_{str(i).zfill(2)}'
        final_result[column_name] = ''
    
    # Save minimum number of reviews to a text file
    reviews_file = 'csv_creation/min_num_of_reviews.txt'
    with open(reviews_file, 'w') as f:
        f.write(f"{min_reviews}+")
    
    # Save to new CSV file
    final_result.to_csv(output_file, index=False)

if __name__ == "__main__":
    input_file = "csv_creation/massage_ratings_with_embeds.csv"
    output_file = "csv_creation/top_rated_massage_shops.csv"
    filter_and_sort_shops(input_file, output_file)
