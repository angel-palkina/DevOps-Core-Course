"""
DevOps Info Service - Flask Application
Main application module providing system and service information.
"""

import os
import socket
import platform
import logging
import json
from datetime import datetime, timezone
from flask import Flask, jsonify, request

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from threading import Lock

# ========== JSON Formatter ==========
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add HTTP context if available
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'client_ip'):
            log_data['client_ip'] = record.client_ip
        if hasattr(record, 'host'):
            log_data['host'] = record.host
        if hasattr(record, 'port'):
            log_data['port'] = record.port
        if hasattr(record, 'debug'):
            log_data['debug'] = record.debug
            
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

# ========== Logging Setup ==========
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Disable werkzeug logger to avoid duplicate logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# ========== Flask App Initialization ==========
app = Flask(__name__)

# ========== Configuration ==========
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# ========== Visits Persistence ==========
VISITS_FILE = os.getenv("VISITS_FILE", "/data/visits")
VISITS_DIR = os.path.dirname(VISITS_FILE)
VISITS_LOCK = Lock()

def ensure_visits_file():
    """Ensure visits directory and file exist."""
    if VISITS_DIR:
        os.makedirs(VISITS_DIR, exist_ok=True)
    if not os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, "w", encoding="utf-8") as f:
            f.write("0")

def read_visits():
    """Read visits count from file, fallback to 0."""
    ensure_visits_file()
    try:
        with open(VISITS_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            return int(raw) if raw else 0
    except Exception:
        logger.exception("Failed to read visits file, fallback to 0")
        return 0

def write_visits(value: int):
    """Atomically write visits count to file."""
    ensure_visits_file()
    tmp_file = f"{VISITS_FILE}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(str(value))
    os.replace(tmp_file, VISITS_FILE)

def increment_visits():
    """Thread-safe increment of visits counter."""
    with VISITS_LOCK:
        current = read_visits()
        new_value = current + 1
        write_visits(new_value)
        return new_value

# ========== Application Start Time ==========
START_TIME = datetime.now(timezone.utc)

# Initialize visits file on startup
ensure_visits_file()

# ========== Prometheus Metrics ==========
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed"
)

# App-specific metrics
ENDPOINT_CALLS = Counter(
    "devops_info_endpoint_calls_total",
    "DevOps info service endpoint calls",
    ["endpoint"]
)

SYSTEM_INFO_DURATION_SECONDS = Histogram(
    "devops_info_system_collection_seconds",
    "Time spent collecting system info"
)

# ========== Request/Response Logging Middleware ==========
@app.before_request
def log_request_info():
    """Log incoming HTTP request."""
    request._start_time = time.perf_counter()
    HTTP_REQUESTS_IN_PROGRESS.inc()
    KNOWN_ENDPOINTS = {"/", "/health", "/metrics", "/visits"}
    raw_endpoint = request.path
    endpoint = raw_endpoint if raw_endpoint in KNOWN_ENDPOINTS else "__unknown__"

    ENDPOINT_CALLS.labels(endpoint=endpoint).inc()
    logger.info(
        "Incoming request",
        extra={
            'method': request.method,
            'path': endpoint,
            'client_ip': request.remote_addr
        }
    )

@app.after_request
def log_response_info(response):
    """Log HTTP response."""
    try:
        duration = time.perf_counter() - getattr(request, "_start_time", time.perf_counter())
    except Exception:
        duration = 0.0

    KNOWN_ENDPOINTS = {"/", "/health", "/metrics", "/visits"}

    raw_endpoint = request.path
    endpoint = raw_endpoint if raw_endpoint in KNOWN_ENDPOINTS else "__unknown__"
    method = request.method
    status_code = str(response.status_code)

    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(duration)
    HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    HTTP_REQUESTS_IN_PROGRESS.dec()
    logger.info(
        "Request completed",
        extra={
            'method': request.method,
            'path': endpoint,
            'status': response.status_code,
            'client_ip': request.remote_addr
        }
    )
    return response


# ========== Helper Functions ==========
def get_system_info():
    """Collect system information."""
    with SYSTEM_INFO_DURATION_SECONDS.time():
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
        'seconds': int(delta.total_seconds()),
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
        'version': '2.1.0',
        'description': 'DevOps course info service with JSON logging and persistent visits counter',
        'framework': 'Flask'
    }


def get_endpoints_list():
    """List available endpoints."""
    return [
        {'path': '/', 'method': 'GET', 'description': 'Service information and increment visits counter'},
        {'path': '/health', 'method': 'GET', 'description': 'Health check'},
        {'path': '/metrics', 'method': 'GET', 'description': 'Prometheus metrics'},
        {'path': '/visits', 'method': 'GET', 'description': 'Current visits counter'}
    ]


# ========== Main Endpoint ==========
@app.route('/')
def index():
    """Main endpoint - returns comprehensive service and system information."""
    visits = increment_visits()
    logger.info(
        "Index endpoint accessed",
        extra={
            'method': request.method,
            'path': request.path,
            'client_ip': request.remote_addr
        }
    )
    response_data = {
        'service': get_service_info(),
        'system': get_system_info(),
        'runtime': get_runtime_info(),
        'request': get_request_info(),
        'visits': visits,
        'endpoints': get_endpoints_list()
    }
    return jsonify(response_data)


# ========== Visits Endpoint ==========
@app.route('/visits')
def visits():
    """Return current visits count without incrementing."""
    count = read_visits()
    return jsonify({
        'visits': count,
        'file': VISITS_FILE
    })

# ========== Health Check Endpoint ==========
@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    logger.info(
        "Health check accessed",
        extra={
            'method': request.method,
            'path': request.path,
            'client_ip': request.remote_addr
        }
    )
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime_seconds': get_uptime()['seconds']
    })

# ========== Metrics Endpoint ==========
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# ========== Error Handlers ==========
@app.errorhandler(404)
def not_found(error):
    logger.warning(
        "404 Not Found",
        extra={
            'method': request.method,
            'path': request.path,
            'client_ip': request.remote_addr,
            'status': 404
        }
    )
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(
        "Internal Server Error",
        extra={
            'method': request.method,
            'path': request.path,
            'client_ip': request.remote_addr,
            'status': 500
        },
        exc_info=True
    )
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ========== Application Entry Point ==========
if __name__ == '__main__':
    logger.info(
        "Starting DevOps Info Service",
        extra={
            'host': HOST,
            'port': PORT,
            'debug': DEBUG
        }
    )
    app.run(host=HOST, port=PORT, debug=DEBUG)