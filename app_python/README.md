# DevOps Info Service

## Overview
A web application that provides detailed information about itself and its runtime environment. This service will evolve throughout the DevOps course into a comprehensive monitoring tool.

## Project Structure
```text
app_python/
├── app.py                    # Main application
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore
├── README.md                # This file
├── tests/                   # Unit tests (Lab 3)
│   └── __init__.py
└── docs/                    # Documentation
    ├── LAB01.md
    └── screenshots/
```

## Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd app_python
    ```


2. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

3. Activate the virtual environment:
- Linux/Mac:

    ```bash
    source venv/bin/activate
    ```
- Windows:

    ```bash
    venv\Scripts\activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

```bash
python app.py #Default Configuration The service will start at: http://0.0.0.0:5000

# Custom Configuration on Linux/Mac:
PORT=8080 python app.py # Change port
HOST=127.0.0.1 PORT=3000 python app.py # Change host and port
DEBUG=true python app.py # Enable debug mode

# Custom Configuration on  Windows PowerShell:
$env:HOST="127.0.0.1"; $env:PORT=8080; python app.py
```

## API Endpoints

### GET /

- Returns comprehensive service and system information (endpoints, request, runtime, system info, service info).

    **Request:**

    ```bash
    curl http://localhost:5000/
    ```

    **Status Codes:**

    - 200 OK: Service is healthy
    - 4xx: Service is unhealthy (implemented in future labs)
    - 5xx: Service is unhealthy (implemented in future labs)

    **Response Example:**
    ![alt text](docs/screenshots/01-main-endpoint.png)

### GET /health

- Health check endpoint for monitoring systems and Kubernetes probes.

    **Request:**

    ```bash
    curl http://localhost:5000/health
    ```

    **Status Codes:**

    - 200 OK: Service is healthy
    - 4xx: Service is unhealthy (implemented in future labs)
    - 5xx: Service is unhealthy (implemented in future labs)

    **Response Example:**
    ![alt text](docs/screenshots/02-health-check.png)

##  Configuration

The application is configured through environment variables:

|Variable | Default | Description |
|----------|-------|---------|
|HOST | 0.0.0.0 | Host interface to bind the server|
|PORT | 5000 | Port number to listen on|
|DEBUG | false | Debug mode (true/false)|


## Future Development

This service will evolve throughout the course:

- Lab 2: Containerization with Docker

- Lab 3: Unit tests and CI/CD

- Lab 8: Metrics endpoint for Prometheus

- Lab 9: Kubernetes deployment

- Lab 12: Persistence with file storage

- Lab 13: Multi-environment deployment


