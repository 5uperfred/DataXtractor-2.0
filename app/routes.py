import os
import tempfile
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from .extraction import PDFExtractor
import config

bp = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@bp.route('/extract', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
        
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file format. Only PDF files are allowed.'
        }), 400

    temp_path = None
    try:
        # Save uploaded file to temporary location
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)  # Close file descriptor immediately
        file.save(temp_path)
        
        # Extract text
        result = PDFExtractor.extract_text_standard(temp_path)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

@bp.route('/extract/ocr', methods=['POST'])
def extract_text_ocr():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
        
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file format. Only PDF files are allowed.'
        }), 400

    language = request.form.get('language', 'eng')
    if language not in config.SUPPORTED_LANGUAGES:
        return jsonify({
            'success': False,
            'error': f'Language {language} not supported'
        }), 400
    
    temp_path = None
    try:
        # Save uploaded file to temporary location
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)  # Close file descriptor immediately
        file.save(temp_path)
        
        # Extract text using OCR
        result = PDFExtractor.extract_text_ocr(temp_path, language)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

@bp.route('/extract/columns', methods=['POST'])
def extract_columns():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
        
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file format. Only PDF files are allowed.'
        }), 400

    # Get parameters from form data
    left_partition = float(request.form.get('left_partition', 0.4))
    right_partition = float(request.form.get('right_partition', 0.6))
    lang_first = request.form.get('lang_first', 'eng')
    lang_second = request.form.get('lang_second', 'eng')
    
    if lang_first not in config.SUPPORTED_LANGUAGES or \
       lang_second not in config.SUPPORTED_LANGUAGES:
        return jsonify({
            'success': False,
            'error': 'One or more languages not supported'
        }), 400
    
    temp_path = None
    try:
        # Save uploaded file to temporary location
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)  # Close file descriptor immediately
        file.save(temp_path)
        
        # Extract text from columns
        result = PDFExtractor.extract_columns(
            temp_path,
            left_partition,
            right_partition,
            lang_first,
            lang_second
        )
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
