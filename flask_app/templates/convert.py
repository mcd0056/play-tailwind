import re

def update_paths(html_file_path):
    # Define the mapping of old paths to new paths
    path_mappings = {
        'href="assets/css/': 'href="static/css/',
        'src="assets/js/': 'src="static/js/',
        'src="assets/images/': 'src="static/images/',
        'assets/images/favicon.png': 'static/images/favicon.png',
        'assets/images/logo/logo.svg': 'static/images/logo/logo.svg'
    }

    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace old paths with new paths
    for old_path, new_path in path_mappings.items():
        content = re.sub(old_path, new_path, content)

    # Write the updated content back to the file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print("Paths updated in the HTML file.")

# Replace with the path to your HTML file
html_file_path = 'flask_app\\templates\\signin.html'
update_paths(html_file_path)
