from flask import Flask, jsonify, request
import os
from psycopg_pool import ConnectionPool

def db_connect():
    db_password = open('/run/secrets/pg_password').read().strip()
    url = (
        f"host={os.environ.get('DB_HOST')} "
        f"dbname={os.environ.get('DB_DATABASE')} "
        f"user={os.environ.get('DB_USER')} "
        f"password={db_password}"
    )
    pool = ConnectionPool(url)
    pool.wait()
    return pool

pool = db_connect()
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Flask + PostgreSQL</h1><a href="/items">/items</a>'

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "version": os.environ.get("APP_VERSION")
    })

@app.route('/items', methods=['GET', 'POST'])
def items():
    with pool.connection() as conn:
        with conn.cursor() as cur:
            if request.method == 'POST':
                body = request.get_json()
                cur.execute(
                    'INSERT INTO item (priority, task) VALUES (%s, %s)',
                    (body['priority'], body['task'])
                )
                conn.commit()
                return {'message': 'item saved!'}, 201

            cur.execute('SELECT item_id, priority, task FROM item')
            return [
                {'id': r[0], 'priority': r[1], 'task': r[2]}
                for r in cur
            ], 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

