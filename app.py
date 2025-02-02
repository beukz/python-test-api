# app.py
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from waitress import serve
import sys

# Configure application
app = Flask(__name__)

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for health checks"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/test', methods=['GET'])
@limiter.limit("5 per minute")
def test_get():
    """Simple GET endpoint"""
    app.logger.info('GET request received')
    return jsonify({
        "message": "GET request successful",
        "data": {"sample_key": "sample_value"}
    }), 200

@app.route('/api/test', methods=['POST'])
def test_post():
    """Simple POST endpoint"""
    try:
        data = request.get_json()
        app.logger.info(f'POST request received with data: {data}')
        
        if not data or 'name' not in data:
            return jsonify({"error": "Missing required parameter 'name'"}), 400
            
        return jsonify({
            "message": "POST request successful",
            "received_data": data,
            "processed": f"Hello, {data['name']}!"
        }), 200
        
    except Exception as e:
        app.logger.error(f'Error processing POST request: {str(e)}')
        return jsonify({"error": "Internal server error"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # For production, use a WSGI server like Waitress or Gunicorn
    serve(app, host='0.0.0.0', port=5000)