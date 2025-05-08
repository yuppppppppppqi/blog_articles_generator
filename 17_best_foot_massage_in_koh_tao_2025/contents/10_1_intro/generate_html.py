import os

# Define the input and output file paths
input_file = 'summary.txt'
output_file = 'summary.html'

# Function to read the summary.txt and generate summary.html

def generate_html_from_summary():
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # Check if the file has exactly 5 lines
        if len(lines) != 5:
            raise ValueError("The summary.txt file does not have exactly 5 lines.")

        # Function to wrap every 2-3 sentences with WordPress paragraph tags
        def wrap_with_wp_paragraph(text):
            sentences = text.split('. ')
            formatted_text = ''
            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                # Add period only if the sentence doesn't end with a period
                if not sentence.endswith('.'):
                    formatted_text += sentence + '. '
                else:
                    formatted_text += sentence + ' '
                if (i + 1) % 2 == 0:
                    formatted_text = f'<!-- wp:paragraph --><p>{formatted_text.strip()}</p><!-- /wp:paragraph -->\n'
            return formatted_text.strip()

        # Function to remove leading '・' from text
        def remove_leading_dot(text):
            return text.lstrip('・').strip()

        # Function to remove duplications like 'Rating: Rating: 5'
        def remove_duplication(text):
            parts = text.split(': ')
            if len(parts) > 1 and parts[0] in parts[1]:
                return parts[1]
            return text

        # Function to remove redundant words from the text
        def remove_redundant_words(text):
            redundant_words = ['Rating', 'Price', 'Recommended']
            for word in redundant_words:
                if text.startswith(word + ': '):
                    return text[len(word) + 2:]
            return text

        # Function to clean summary text
        def clean_summary_text(text):
            # Remove leading bullet point and "Summary:" if present
            text = text.lstrip('・').strip()
            if text.startswith('Summary:'):
                text = text[8:].strip()
            return text

        # Function to add proper spacing around forward slash
        def format_slash_spacing(text):
            # Replace slash without spaces with spaced version
            parts = text.split('/')
            if len(parts) > 1:
                return ' / '.join(part.strip() for part in parts)
            return text

        # Extract the required information
        shop_name = lines[0].strip()
        rating = format_slash_spacing(remove_redundant_words(remove_duplication(remove_leading_dot(lines[1].strip()))))
        price = remove_redundant_words(remove_duplication(remove_leading_dot(lines[2].strip())))
        recommended = remove_redundant_words(remove_duplication(remove_leading_dot(lines[3].strip())))
        summary = wrap_with_wp_paragraph(clean_summary_text(lines[4].strip()))

        # Create the HTML content using WordPress-like tags with improved formatting
        html_content = f"""<h2 style="margin-bottom: 20px; margin-top: 50px;"><strong>{shop_name}</strong></h2>
<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full" style="margin-bottom: 20px;">
    <img 
        src="https://my-bangkok-life.com/wp-content/uploads/2025/05/foot-koh-tao-10-seashell-restaurant.webp"
        alt="foot koh tao 10 seashell restaurant"
        class="wp-image-21"
    />
</figure>
<!-- /wp:image -->
<!-- wp:list -->
<ul class='wp-block-list' style="padding-left: 15px; margin-left: 0;">
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;"><strong>Rating:</strong> {rating}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;;"><strong>Price:</strong> {price}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px; margin-left: 0;"><strong>Recommended:</strong> {recommended}</li>
   <!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
<!-- wp:paragraph -->
<p style="margin-top: 20px; margin-bottom: 20px; line-height: 1.6;">{summary}</p>
<!-- /wp:paragraph -->
<p><iframe src='https://www.google.com/maps/embed/v1/place?q=place_id:ChIJjwocw-6hVTAR2kI9uZReyUQ&zoom=17&key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8' width='600' height='450' style='border:0' allowfullscreen='' loading='lazy' referrerpolicy='no-referrer-when-downgrade'></iframe></p>"""

        # Write the HTML content to the output file
        with open(output_file, 'w') as file:
            file.write(html_content)

        print(f"HTML file '{output_file}' generated successfully.")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
generate_html_from_summary() 