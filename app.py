from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import base64
from dotenv import load_dotenv
from pdf_processor import extract_text_from_pdf
from content_generator import generate_content

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the PDF
            text = extract_text_from_pdf(file_path)
            
            # Generate content
            content = generate_content(text)
            
            return jsonify({
                'message': 'File uploaded and content generated successfully',
                'content': content
            }), 200
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_new_content():
    try:
        file_content = request.json.get('file_content')
        if not file_content:
            return jsonify({'error': 'No file content provided'}), 400
        
        # Decode the base64 content
        pdf_content = base64.b64decode(file_content)
        
        # Save to a temporary file
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.pdf')
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(pdf_content)
        
        # Process the PDF
        text = extract_text_from_pdf(temp_file_path)
        
        # Generate content
        content = generate_content(text)
        
        # Clean up the temporary file
        os.remove(temp_file_path)
        
        return jsonify({
            'message': 'New content generated successfully',
            'content': content
        }), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)