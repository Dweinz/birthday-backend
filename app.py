from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DB = 'players.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                rounds_completed INTEGER,
                total_score INTEGER
            )
        ''')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    with sqlite3.connect(DB) as conn:
        try:
            conn.execute('INSERT INTO players (username, rounds_completed, total_score) VALUES (?, 0, 0)', (username,))
            return jsonify({'message': 'User registered'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'message': 'User already exists'}), 200

@app.route('/progress/<username>', methods=['GET'])
def get_progress(username):
    with sqlite3.connect(DB) as conn:
        cur = conn.execute('SELECT rounds_completed, total_score FROM players WHERE username = ?', (username,))
        row = cur.fetchone()
        if row:
            return jsonify({'username': username, 'rounds_completed': row[0], 'total_score': row[1]})
        return jsonify({'error': 'User not found'}), 404

@app.route('/scoreboard', methods=['GET'])
def get_scoreboard():
    with sqlite3.connect(DB) as conn:
        cur = conn.execute('''
            SELECT username, rounds_completed, total_score
            FROM players
            ORDER BY total_score DESC
        ''')
        users = [
            {'username': row[0], 'rounds_completed': row[1], 'total_score': row[2]}
            for row in cur.fetchall()
        ]
        return jsonify(users)


@app.route('/progress', methods=['POST'])
def update_progress():
    data = request.get_json()
    username = data.get('username')
    rounds = data.get('rounds_completed')
    score = data.get('total_score')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    with sqlite3.connect(DB) as conn:
        cur = conn.execute('SELECT * FROM players WHERE username = ?', (username,))
        if not cur.fetchone():
            return jsonify({'error': 'User not found'}), 404

        conn.execute('''
            UPDATE players
            SET rounds_completed = ?, total_score = ?
            WHERE username = ?
        ''', (rounds, score, username))
        return jsonify({'message': 'Progress updated'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
