# Lab 1 — DevOps Info Service: Implementation Report

## Framework Selection

I selected **Flask** as the web framework for this project, because Flask provides the optimal balance of simplicity, flexibility, and learning opportunity.  Flask's minimal approach allows us to focus on DevOps practices while still creating a production-ready service.


| Framework | Pros | Cons | Decision Reason |
|-----------|------|------|----------------|
| **Flask** | - Lightweight and minimal<br>- Perfect for microservices<br>- Excellent for educational purposes | - Less built-in features compared to Django<br>- Manual setup for async operations | Ideal for simple API services, easier for beginners learning DevOps concepts, sufficient for our monitoring service needs |
| FastAPI | - Native async support<br>- Auto-generated OpenAPI documentation<br>- High performance<br>- Type hints integration | - Steeper learning curve for Python beginners<br>- More overhead for a simple application | Considered for modern features but Flask's simplicity better fits educational goals |
| Django | - Comprehensive security features<br>- Excellent for full-stack applications | - Heavyweight <br>- Overkill for a simple API service<br>- Longer setup time | Too complex for this microservice; would add unnecessary complexity |

## Best Practices Applied

### 1. Clean Code Organization
- **Modular Structure:** Separated concerns into distinct functions (`get_system_info`, `get_runtime_info`, etc.) for better understanding
- **Descriptive Naming:** Functions clearly indicate their purpose
- **Import Grouping:** Organized imports in logical groups (standard library, third-party)
- **Minimal Comments:** Comments only where business logic needs explanation
- **PEP 8 Compliance:** Followed Python style guide for indentation, line length, and naming conventions
- **Comprehensive Error Handling:** Implemented error handlers for common HTTP status codes
- **Structured Logging:** Timestamps help debug timing issues
- **Environment-Based Configuration:** No hardcoded values in source code, easy configuration for different environments

**Code Example:**
```python
def get_system_info():
    """Collect comprehensive system information."""
    return {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_version': platform.platform(),
        'architecture': platform.machine(),
        'cpu_count': os.cpu_count(),
        'python_version': platform.python_version()
    }
```

## API Documentation

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
    ![alt text](screenshots/01-main-endpoint.png)

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
    ![alt text](screenshots/02-health-check.png)

## Testing commands

```bash
python app.py #Default Configuration The service will start at: http://0.0.0.0:5000

# Custom Configuration on Linux/Mac:
PORT=8080 python app.py # Change port
HOST=127.0.0.1 PORT=3000 python app.py # Change host and port
DEBUG=true python app.py # Enable debug mode

# Custom Configuration on  Windows PowerShell:
$env:HOST="127.0.0.1"; $env:PORT=8080; python app.py
```

## Terminal Output Examples

Application Startup:

```text
2026-01-28 22:02:58,501 - __main__ - INFO - Starting DevOps Info Service on 0.0.0.0:8813 (DEBUG=False)
 * Serving Flask app 'app'
 * Debug mode: off
```

Request Logging:

```text
2026-01-28 22:03:13,068 - __main__ - INFO - Request to / from 127.0.0.1
2026-01-28 22:03:13,116 - werkzeug - INFO - 127.0.0.1 - - [28/Jan/2026 22:03:13] "GET / HTTP/1.1" 200 -
```

## Challenges & Solutions

###  Windows Port Access Restrictions

**Problem:**
When trying to bind to certain ports in Windows, received error: "An attempt was made to access a socket in a way forbidden by its access permissions". This occurred regardless of which port was used with the command $env:HOST="127.0.0.1"; $env:PORT=3000; python app.py.

**Root Cause:**
Windows has strict socket permissions, and ports below 1024 often require administrator privileges. Additionally, Windows Firewall or antivirus software can block socket creation.

**Solution:**

1. Use ports above 1024: Changed to port 5000 or 8080 which don't require admin rights
2. Run PowerShell as Administrator: For ports that require elevated privileges

## GitHub Community

### Importance of Starring Repositories
Starring repositories on GitHub is crucial in open source development for several reasons:

- **Discovery & Visibility:** Stars help projects gain visibility in GitHub search and recommendations. More stars often indicate a trustworthy and useful project.

- **Appreciation & Motivation:** Stars show appreciation to maintainers, encouraging them to continue development and support.

- **Bookmarking:** Stars serve as personal bookmarks for interesting projects you might want to reference or contribute to later.

- **Professional Profile:** Your starred repositories appear on your GitHub profile, showcasing your interests and engagement with the developer community.


### Value of Following Developers
Following classmates, professors, and industry professionals provides significant benefits:

- **Learning Opportunities:** You can see how experienced developers solve problems, structure projects, and write code.

- **Networking:** Building connections within the DevOps community can lead to collaboration opportunities, job prospects, and knowledge sharing.

- **Project Discovery:** Following others helps you discover new tools, libraries, and best practices through their activity and starred repositories.

- **Community Building:** In educational settings, following classmates creates a supportive learning environment where you can share knowledge and help each other.

- **Career Growth:** Following industry leaders keeps you updated on trends and shows potential employers your active engagement in the field.