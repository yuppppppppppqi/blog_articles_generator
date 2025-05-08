def add_h2_to_conclusion():
    # Read the original conclusion.html
    with open('conclusion.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Add the H2 heading at the beginning
    h2_tag = '<h2 style="margin-bottom: 20px; margin-top: 50px;"><strong>Conclusion</strong></h2>'
    new_content = h2_tag + '\n' + content
    
    # Write to the new file
    with open('conclusion_with_h2.html', 'w', encoding='utf-8') as file:
        file.write(new_content)

if __name__ == '__main__':
    add_h2_to_conclusion()
