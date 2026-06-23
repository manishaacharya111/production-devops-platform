from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint']
)

@app.route('/')
def home():
    start = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/', status='200').inc()
    REQUEST_LATENCY.labels(endpoint='/').observe(time.time() - start)
    return jsonify({
        'status': 'healthy',
        'service': 'production-devops-platform',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status='200').inc()
    return jsonify({'status': 'ok'}), 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/error')
def error():
    REQUEST_COUNT.labels(method='GET', endpoint='/error', status='500').inc()
    return jsonify({'error': 'simulated error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)