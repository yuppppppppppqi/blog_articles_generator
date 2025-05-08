def read_reviews(filename):
    with open(filename, 'r') as file:
        reviews = file.read().splitlines()
    
    if len(reviews) != 10:
        raise ValueError(f"Expected 10 reviews, but found {len(reviews)} reviews")
    
    return reviews

def generate_html(reviews):
    # Specified order: 1,2,3,9,4,5,10,6,7,8
    # Note: Converting to 0-based indexing
    order = [0, 1, 2, 8, 3, 4, 9, 5, 6, 7]
    
    html = '<!-- wp:heading {"level":4} -->\n'
    html += '<h3 class="wp-block-heading"><strong>Reviews</strong></h3>\n'
    html += '<!-- /wp:heading -->\n\n'
    
    html += '<!-- wp:list -->\n'
    html += '<ul class="wp-block-list" style="padding-left: 15px; margin-left: 0;">\n'
    
    for index in order:
        html += '   <!-- wp:list-item -->\n'
        html += f'   <li style="margin-bottom: 10px; margin-left: 0;">{reviews[index]}</li>\n'
        html += '   <!-- /wp:list-item -->\n'
    
    html += '</ul>\n'
    html += '<!-- /wp:list -->'
    return html

def main():
    try:
        reviews = read_reviews('reviews.txt')
        html_content = generate_html(reviews)
        
        with open('reviews.html', 'w') as file:
            file.write(html_content)
        
        print("Successfully generated reviews.html")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
