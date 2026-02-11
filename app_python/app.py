"""
DevOps Info Service - Flask Application
Main application module providing system and service information.
"""

import os
import socket
import platform
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request

# ========== Flask App Initialization ==========
app = Flask(__name__)

# ========== Configuration ==========
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ========== Logging Setup ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== Application Start Time ==========
START_TIME = datetime.now(timezone.utc)


# ========== Helper Functions ==========
def get_system_info():
    """Collect system information."""
    return {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_version': platform.platform(),
        'architecture': platform.machine(),
        'cpu_count': os.cpu_count(),
        'python_version': platform.python_version()
    }


def get_uptime():
    """Calculate application uptime."""
    delta = datetime.now(timezone.utc) - START_TIME
    seconds = int(delta.total_seconds())
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        'seconds': seconds,
        'human': f"{hours} hours, {minutes} minutes"
    }


def get_runtime_info():
    """Collect runtime information."""
    uptime = get_uptime()
    now = datetime.now(timezone.utc)
    return {
        'uptime_seconds': uptime['seconds'],
        'uptime_human': uptime['human'],
        'current_time': now.isoformat(),
        'timezone': str(now.tzinfo)
    }


def get_request_info():
    """Collect request information."""
    return {
        'client_ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'unknown'),
        'method': request.method,
        'path': request.path
    }


def get_service_info():
    """Service metadata."""
    return {
        'name': 'devops-info-service',
        'version': '1.0.0',
        'description': 'DevOps course info service',
        'framework': 'Flask'
    }


def get_endpoints_list():
    """List available endpoints."""
    return [
        {'path': '/', 'method': 'GET', 'description': 'Service information'},
        {'path': '/health', 'method': 'GET', 'description': 'Health check'}
    ]


# ========== Main Endpoint ==========
@app.route('/')
def index():
    """Main endpoint - returns comprehensive service and system information."""
    logger.info(f"Request to / from {request.remote_addr}")
    response_data = {
        'service': get_service_info(),
        'system': get_system_info(),
        'runtime': get_runtime_info(),
        'request': get_request_info(),
        'endpoints': get_endpoints_list()
    }
    return jsonify(response_data)


# ========== Health Check Endpoint ==========
@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    logger.info(f"Health check from {request.remote_addr}")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': get_uptime()['seconds']
    })


# ========== Error Handlers ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal Server Error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ========== Application Entry Point ==========
if __name__ == '__main__':
    logger.info(
        f"Starting DevOps Info Service on {HOST}:{PORT} (DEBUG={DEBUG})")
    app.run(host=HOST, port=PORT, debug=DEBUG)
