"""
Unit tests for DevOps Info Service Flask application.
"""

import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к app.py чтобы импортировать
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_system_info, get_uptime, get_service_info

@pytest.fixture
def client():
    """Фикстура: создаём тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ========== ТЕСТЫ ДЛЯ ЭНДПОИНТА / ==========

def test_index_status_code(client):
    """Тест 1: Проверяем, что главная страница возвращает 200 OK"""
    response = client.get('/')
    assert response.status_code == 200

def test_index_is_json(client):
    """Тест 2: Проверяем, что ответ — это JSON"""
    response = client.get('/')
    assert response.is_json

def test_index_has_required_sections(client):
    """Тест 3: Проверяем, что есть все основные секции"""
    response = client.get('/')
    data = response.get_json()
    
    assert 'service' in data
    assert 'system' in data
    assert 'runtime' in data
    assert 'request' in data
    assert 'endpoints' in data

def test_index_service_info(client):
    """Тест 4: Проверяем информацию о сервисе"""
    response = client.get('/')
    service = response.get_json()['service']
    
    assert service['name'] == 'devops-info-service'
    assert service['version'] == '1.0.0'
    assert service['framework'] == 'Flask'
    assert isinstance(service['description'], str)

def test_index_system_info_fields(client):
    """Тест 5: Проверяем, что системная информация содержит все поля"""
    response = client.get('/')
    system = response.get_json()['system']
    
    expected_fields = ['hostname', 'platform', 'platform_version', 
                      'architecture', 'cpu_count', 'python_version']
    
    for field in expected_fields:
        assert field in system
    
    # Проверяем типы данных
    assert isinstance(system['hostname'], str)
    assert isinstance(system['cpu_count'], int)
    assert isinstance(system['python_version'], str)

def test_index_runtime_info(client):
    """Тест 6: Проверяем информацию о времени работы"""
    response = client.get('/')
    runtime = response.get_json()['runtime']
    
    assert 'uptime_seconds' in runtime
    assert 'uptime_human' in runtime
    assert 'current_time' in runtime
    assert 'timezone' in runtime
    
    # uptime_seconds должен быть положительным числом
    assert runtime['uptime_seconds'] >= 0
    assert isinstance(runtime['uptime_seconds'], int)

def test_index_request_info(client):
    """Тест 7: Проверяем информацию о запросе"""
    response = client.get('/')
    request_info = response.get_json()['request']
    
    assert 'client_ip' in request_info
    assert 'user_agent' in request_info
    assert 'method' in request_info
    assert 'path' in request_info
    
    assert request_info['method'] == 'GET'
    assert request_info['path'] == '/'

def test_index_endpoints_list(client):
    """Тест 8: Проверяем список эндпоинтов"""
    response = client.get('/')
    endpoints = response.get_json()['endpoints']
    
    assert isinstance(endpoints, list)
    assert len(endpoints) >= 2
    
    # Проверяем, что есть / и /health
    paths = [e['path'] for e in endpoints]
    assert '/' in paths
    assert '/health' in paths

# ========== ТЕСТЫ ДЛЯ ЭНДПОИНТА /HEALTH ==========

def test_health_status_code(client):
    """Тест 9: Проверяем, что health endpoint доступен"""
    response = client.get('/health')
    assert response.status_code == 200

def test_health_is_json(client):
    """Тест 10: Проверяем, что health возвращает JSON"""
    response = client.get('/health')
    assert response.is_json

def test_health_response_structure(client):
    """Тест 11: Проверяем структуру ответа health"""
    response = client.get('/health')
    data = response.get_json()
    
    assert 'status' in data
    assert 'timestamp' in data
    assert 'uptime_seconds' in data
    
    assert data['status'] == 'healthy'
    assert data['uptime_seconds'] >= 0

def test_health_timestamp_format(client):
    """Тест 12: Проверяем, что timestamp в правильном формате"""
    response = client.get('/health')
    timestamp = response.get_json()['timestamp']
    
    # Пробуем распарсить ISO формат даты
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        is_valid = True
    except ValueError:
        is_valid = False
    
    assert is_valid

# ========== ТЕСТЫ ДЛЯ ОБРАБОТЧИКОВ ОШИБОК ==========

def test_404_not_found(client):
    """Тест 13: Проверяем, что несуществующий путь возвращает 404"""
    response = client.get('/non-existent-path')
    assert response.status_code == 404
    
    data = response.get_json()
    assert 'error' in data
    assert 'message' in data
    assert data['error'] == 'Not Found'

def test_method_not_allowed(client):
    """Тест 14: Проверяем POST на GET endpoint"""
    response = client.post('/')
    assert response.status_code in [405, 404]  # 405 Method Not Allowed

# ========== ТЕСТЫ ДЛЯ ХЕЛПЕР-ФУНКЦИЙ ==========

def test_get_system_info_function():
    """Тест 15: Проверяем функцию get_system_info"""
    info = get_system_info()
    
    assert isinstance(info, dict)
    assert 'hostname' in info
    assert 'platform' in info
    assert 'cpu_count' in info
    assert info['cpu_count'] > 0

def test_get_uptime_function():
    """Тест 16: Проверяем функцию get_uptime"""
    uptime = get_uptime()
    
    assert 'seconds' in uptime
    assert 'human' in uptime
    assert uptime['seconds'] >= 0
    assert isinstance(uptime['human'], str)

def test_get_service_info_function():
    """Тест 17: Проверяем функцию get_service_info"""
    info = get_service_info()
    
    assert info['name'] == 'devops-info-service'
    assert info['version'] == '1.0.0'