from flask import Flask, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def root():
    # Serve the HTML file
    return app.send_static_file('image_selection_ui.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Serve other static files (images, JS, etc.)
    return send_from_directory('.', path)

@app.route('/save_json', methods=['POST'])
def save_json():
    data = request.get_json()
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'selected_images.json'), 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'status': 'success'})

@app.route('/list_shops', methods=['GET'])
def list_shops():
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    shops = []
    if not os.path.exists(output_dir):
        return jsonify(shops)
    for shop_name in sorted(os.listdir(output_dir)):
        shop_path = os.path.join(output_dir, shop_name)
        if not os.path.isdir(shop_path):
            continue
        # Prefer 'modified' subdir if it exists and has images
        modified_path = os.path.join(shop_path, 'modified')
        images = []
        if os.path.isdir(modified_path):
            images = [f for f in sorted(os.listdir(modified_path)) if f.lower().endswith('.png')]
        if not images:
            images = [f for f in sorted(os.listdir(shop_path)) if f.lower().endswith('.png')]
        if not images:
            continue  # Skip shops with no images
        shops.append({
            'name': shop_name,
            'images': images
        })
    return jsonify(shops)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 