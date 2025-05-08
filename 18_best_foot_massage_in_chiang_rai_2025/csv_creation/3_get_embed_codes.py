import csv
import re
from urllib.parse import urlparse, parse_qs
import time
import os

def extract_place_id(google_maps_link):
    """Extract place_id from Google Maps link."""
    # Parse the URL and get the query parameters
    parsed_url = urlparse(google_maps_link)
    query_params = parse_qs(parsed_url.query)
    
    # Extract place_id from the query parameters
    if 'place_id' in query_params.get('q', [''])[0]:
        # Extract place_id from the q parameter
        place_id = query_params.get('q', [''])[0].split(':')[1]
        return place_id
    return None

def create_embed_url(place_id):
    """Create an embed URL for the given place ID."""
    # Using place mode which is specifically for showing single locations
    return f"https://www.google.com/maps/embed/v1/place?q=place_id:{place_id}&zoom=17&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8"

def create_embed_code(embed_url, width=600, height=450):
    """Create the full iframe HTML code."""
    return f"<iframe src='{embed_url}' width='{width}' height='{height}' style='border:0' allowfullscreen='' loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe>"

def process_csv():
    input_file = "csv_creation/massage_ratings_in_one_area_replaced.csv"
    output_file = "csv_creation/massage_ratings_with_embeds.csv"
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames) + ['Embed URL', 'Embed Code']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for row in reader:
            # Extract place_id from the Google Maps link
            place_id = extract_place_id(row['Google Maps Link'])
            if place_id:
                # Create embed URL and code
                embed_url = create_embed_url(place_id)
                embed_code = create_embed_code(embed_url)
                
                # Add new fields to the row
                row['Embed URL'] = embed_url
                row['Embed Code'] = embed_code
            
            writer.writerow(row)

if __name__ == "__main__":
    process_csv()
    print("Processing complete! Check csv_creation/massage_ratings_with_embeds.csv for results.") 