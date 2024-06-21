def index():
    with open('resources/index.html', 'r') as file:
        html_content = file.read()
    return html_content, 200