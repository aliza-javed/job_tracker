"""
app.py
------
Flask application with all routes.
ALL BUGS FIXED - Complete working version.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import logging
from datetime import datetime

# Our modules
from analyzer import ResumeAnalyzer
from llm_client import GeminiLLMClient

# Initialize Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
analyzer = ResumeAnalyzer()
llm_client = None

# Try to initialize LLM (Gemini)
try:
    llm_client = GeminiLLMClient()
    logger.info("LLM client initialized successfully")
except Exception as e:
    logger.warning(f"LLM client not available: {e}")


# ============================================================
# ROUTES - Pages
# ============================================================

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/resume')
def resume_page():
    """Resume analyzer page."""
    return render_template('resume.html')

@app.route('/job-rag')
def job_rag_page():
    """Job RAG query page."""
    return render_template('job_rag.html')


@app.route('/resume-builder')
def resume_builder():
    """Resume template page."""
    return render_template('resume_template.html')

# ============================================================
# ROUTES - API
# ============================================================

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    """
    Analyze resume endpoint.
    Accepts: multipart/form-data with 'file' field
    Returns: JSON with analysis results
    """
    logger.info("Resume analysis request received")
    
    # FIX 1: Check content type
    if not request.content_type or 'multipart/form-data' not in request.content_type:
        logger.error(f"Invalid content type: {request.content_type}")
        return jsonify({
            "success": False,
            "error": "Content-Type must be multipart/form-data"
        }), 400
    
    # FIX 2: Check if file exists in request
    if 'file' not in request.files:
        logger.error("No file in request")
        logger.info(f"Request files: {request.files}")
        logger.info(f"Request form: {request.form}")
        return jsonify({
            "success": False,
            "error": "No file provided. Please upload a file."
        }), 400
    
    file = request.files['file']
    
    # FIX 3: Check if file has a filename
    if file.filename == '' or file.filename is None:
        logger.error("Empty filename")
        return jsonify({
            "success": False,
            "error": "No file selected. Please choose a file."
        }), 400
    
    # FIX 4: Validate file extension
    allowed_extensions = {'.txt', '.md', '.docx', '.pdf'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        logger.error(f"Invalid file extension: {file_ext}")
        return jsonify({
            "success": False,
            "error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        }), 400
    
    try:
        # FIX 5: Read file content based on type
        logger.info(f"Reading file: {file.filename} (type: {file_ext})")
        
        if file_ext in ['.txt', '.md']:
            content = file.read().decode('utf-8')
        
        elif file_ext == '.docx':
            try:
                from docx import Document
                doc = Document(file)
                content = '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return jsonify({
                    "success": False,
                    "error": "python-docx not installed. Run: pip install python-docx"
                }), 500
        
        elif file_ext == '.pdf':
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(file)
                content = '\n'.join([page.extract_text() for page in reader.pages])
            except ImportError:
                return jsonify({
                    "success": False,
                    "error": "PyPDF2 not installed. Run: pip install PyPDF2"
                }), 500
        
        # FIX 6: Validate content is not empty
        if not content or not content.strip():
            return jsonify({
                "success": False,
                "error": "File appears to be empty"
            }), 400
        
        logger.info(f"File content length: {len(content)} characters")
        
        # Analyze the resume
        result = analyzer.analyze(content)
        
        # FIX 7: Build proper JSON response
        response_data = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
            "overall_score": result.overall_score,
            "ranking": result.ranking,
            "sections": {},
            "suggestions": result.suggestions
        }
        
        # Add section data
        for section_name, section in result.sections.items():
            response_data["sections"][section_name] = {
                "score": section.score,
                "feedback": section.feedback,
                "content": section.content[:500] if section.content else ""  # Limit content
            }
        
        logger.info(f"Analysis complete. Score: {result.overall_score}")
        return jsonify(response_data), 200
    
    except UnicodeDecodeError:
        logger.error("Unicode decode error")
        return jsonify({
            "success": False,
            "error": "File encoding error. Please upload a UTF-8 encoded text file."
        }), 400
    
    except Exception as e:
        logger.exception(f"Error analyzing resume: {e}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/rag-query', methods=['POST'])
def rag_query():
    """
    Job RAG query endpoint.
    Accepts JSON: {"query": "your question"}
    Returns JSON: {"answer": "..."}
    """
    logger.info("RAG query received")
    
    # FIX: Validate content type
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Content-Type must be application/json"
        }), 400
    
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'query' field"
        }), 400
    
    query = data['query'].strip()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Query cannot be empty"
        }), 400
    
    try:
        if llm_client is None:
            return jsonify({
                "success": False,
                "error": "LLM client not available"
            }), 503
        
        answer = llm_client.query(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "answer": answer
        }), 200
    
    except Exception as e:
        logger.exception(f"RAG error: {e}")
        return jsonify({
            "success": False,
            "error": f"Query failed: {str(e)}"
        }), 500


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 - return JSON for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 - return JSON for API routes."""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('500.html'), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Resume Analyzer + Job RAG System")
    print("=" * 60)
    print(f"Resume Analyzer: http://localhost:5000/resume")
    print(f"Job RAG Query:   http://localhost:5000/job-rag")
    print("=" * 60)
    
    app.run(debug=True, port=5000)