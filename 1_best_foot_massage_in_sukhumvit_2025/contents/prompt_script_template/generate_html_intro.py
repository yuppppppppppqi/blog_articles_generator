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

        # Extract the required information
        shop_name = lines[0].strip()
        rating = remove_redundant_words(remove_duplication(remove_leading_dot(lines[1].strip())))
        price = remove_redundant_words(remove_duplication(remove_leading_dot(lines[2].strip())))
        recommended = remove_redundant_words(remove_duplication(remove_leading_dot(lines[3].strip())))
        summary = wrap_with_wp_paragraph(lines[4].strip())

        # Create the HTML content using WordPress-like tags with improved formatting
        html_content = f"""<h2 style="margin-bottom: 20px; margin-top: 50px;"><strong>{shop_name}</strong></h2>
<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full" style="margin-bottom: 20px;">
    <img 
        src="[TEMPLATE_IMAGE_URL]"
        alt="[TEMPLATE_IMAGE_ALT]"
        class="wp-image-21"
    />
</figure>
<!-- /wp:image -->
<!-- wp:list -->
<ul class='wp-block-list'>
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px;"><strong>Rating:</strong> {rating}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px;"><strong>Price:</strong> {price}</li>
   <!-- /wp:list-item -->
   <!-- wp:list-item -->
   <li style="margin-bottom: 10px;"><strong>Recommended:</strong> {recommended}</li>
   <!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
<!-- wp:paragraph -->
<p style="margin-top: 20px; margin-bottom: 20px; line-height: 1.6;">{summary}</p>
<!-- /wp:paragraph -->
<p>[TEMPLATE_IFRAME_CODE]</p>"""

        # Write the HTML content to the output file
        with open(output_file, 'w') as file:
            file.write(html_content)

        print(f"HTML file '{output_file}' generated successfully.")

    except Exception as e:
        print(f"Error: {e}")

# Run the function
generate_html_from_summary() 