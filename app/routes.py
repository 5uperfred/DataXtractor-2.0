from flask import Blueprint, request, jsonify
import os
import tempfile
from .extraction import PDFExtractor
from config import settings

api_routes = Blueprint('api', __name__)

def save_upload(file, suffix):
    temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    file.save(temp.name)
    return temp.name

@api_routes.route("/extract/standard", methods=['POST'])
def extract_standard():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    temp_path = save_upload(file, '.pdf')
    try:
        text = PDFExtractor.extract_text_standard(temp_path)
        return jsonify({"filename": file.filename, "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

@api_routes.route("/extract/ocr", methods=['POST'])
def extract_ocr():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    temp_path = save_upload(file, '.pdf')
    try:
        # Default to English, but allow param override
        lang = request.form.get('language', 'eng')
        text = PDFExtractor.extract_text_ocr(temp_path, language=lang)
        return jsonify({"filename": file.filename, "text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

@api_routes.route("/extract/columns", methods=['POST'])
def extract_columns():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    temp_path = save_upload(file, '.pdf')
    try:
        col1, col2 = PDFExtractor.extract_columns(temp_path)
        return jsonify({
            "filename": file.filename, 
            "column_1": col1, 
            "column_2": col2
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

@api_routes.route("/extract/xls", methods=['POST'])
def extract_excel():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    
    # Accept both .xls and .xlsx
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        return jsonify({"error": "Invalid file type. Must be Excel."}), 400

    temp_path = save_upload(file, '.xlsx')
    try:
        data = PDFExtractor.extract_excel(temp_path)
        return jsonify({"filename": file.filename, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)
