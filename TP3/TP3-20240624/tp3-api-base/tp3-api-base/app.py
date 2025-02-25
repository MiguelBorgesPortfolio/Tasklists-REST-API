from flask import Flask, request, jsonify, g
from models import Database
from datetime import datetime, timezone

# ==========
#  Settings
# ==========

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
app.config['DEBUG'] = True

# ==========
#  Database
# ==========

# Creates an sqlite database in memory
db = Database(filename=':memory:', schema='schema.sql')
db.recreate()

# ===========
#  Web views
# ===========

@app.route('/')
def index():
    return app.send_static_file('index.html')

# ===========
#  API views
# ===========

@app.before_request
def before_request():
    auth = request.authorization
    if auth:
        user = db.execute_query('SELECT * FROM user WHERE username=? AND password=?', (
            auth.username, auth.password
        )).fetchone()
        g.user = user
    else:
        g.user = None

@app.route('/api/user/register/', methods=['POST'])
def user_register():
    """
    Registers a new user.
    Does not require authorization.
    """
    data = request.get_json()
    db.execute_update('INSERT INTO user (name, email, username, password) VALUES (?, ?, ?, ?)', (
        data['name'], data['email'], data['username'], data['password']
    ))
    return jsonify({'status': 'User registered successfully'}), 201

@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    """
    Returns or updates current user.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        # Returns user data
        return jsonify(g.user)
    else:
        # Updates user data
        data = request.get_json()
        db.execute_update('UPDATE user SET name=?, email=?, username=?, password=? WHERE id=?', (
            data['name'], data['email'], data['username'], data['password'], g.user['id']
        ))
        return jsonify({'status': 'User updated successfully'}), 200

@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    """
    Project list.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        # Returns the list of projects of a user
        projects = db.execute_query(
            'SELECT * FROM project WHERE user_id=?', (g.user['id'],)).fetchall()
        return jsonify(projects)
    else:
        # Adds a project to the list
        data = request.get_json()
        if 'title' not in data or not data['title']:
            return jsonify({'error': 'Invalid data'}), 400
        creation_date = datetime.now(timezone.utc).isoformat()
        project_id = db.execute_update(
            'INSERT INTO project (user_id, title, creation_date, last_updated) '
            'VALUES (?, ?, ?, ?)', (
            g.user['id'], data['title'], creation_date, creation_date
        ))
        return jsonify({'status': 'Project created successfully', 'id': project_id}), 201

@app.route('/api/projects/<int:pk>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(pk):
    """
    Project detail.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    project = db.execute_query(
        'SELECT * FROM project WHERE id=? AND user_id=?', (pk, g.user['id'])).fetchone()

    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if request.method == 'GET':
        # Returns a project
        return jsonify(project)
    elif request.method == 'PUT':
        # Updates a project
        data = request.get_json()
        db.execute_update(
            'UPDATE project SET title=?, last_updated=? WHERE id=? AND user_id=?', (
            data['title'], datetime.now(timezone.utc).isoformat(), pk, g.user['id']
        ))
        return jsonify({'status': 'Project updated successfully'}), 200
    else:
        # Deletes a project and associated tasks
        db.execute_update(
            'DELETE FROM task WHERE project_id=?', (pk,))
        db.execute_update(
            'DELETE FROM project WHERE id=? AND user_id=?',
            (pk, g.user['id']))
        return jsonify({'status':
                            'Project and associated tasks deleted successfully'}), 200

@app.route('/api/projects/<int:pk>/tasks/', methods=['GET', 'POST'])
def task_list(pk):
    """
    Task list.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    # Ensure the project belongs to the user
    project = db.execute_query(
        'SELECT * FROM project WHERE id=? AND user_id=?',
        (pk, g.user['id'])).fetchone()
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    if request.method == 'GET':
        # Returns the list of tasks of a project
        tasks = db.execute_query(
            'SELECT * FROM task WHERE project_id=?',
            (pk,)).fetchall()
        return jsonify(tasks)
    else:
        # Adds a task to project
        data = request.get_json()
        if 'title' not in data or not data['title']:
            return jsonify({'error': 'Invalid data'}), 400
        creation_date = datetime.now(timezone.utc).isoformat()
        task_id = db.execute_update(
            'INSERT INTO task (project_id, title, creation_date, completed)'
            ' VALUES (?, ?, ?, ?)', (
            pk, data['title'], creation_date, data['completed']
        ))
        return jsonify({'status': 'Task created successfully', 'id': task_id}), 201

@app.route('/api/projects/<int:project_id>/tasks/<int:task_id>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(project_id, task_id):
    """
    Task detail.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    # Ensure the task belongs to the project and the project belongs to the user
    project = db.execute_query(
        'SELECT * FROM project WHERE id=? AND user_id=?', (project_id, g.user['id'])).fetchone()
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    task = db.execute_query(
        'SELECT * FROM task WHERE id=? AND project_id=?',
        (task_id, project_id)).fetchone()
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'GET':
        # Returns a task
        return jsonify(task)
    elif request.method == 'PUT':
        # Updates a task
        data = request.get_json()
        db.execute_update('UPDATE task SET title=?, completed=? WHERE id=? AND project_id=?', (
            data['title'], data['completed'], task_id, project_id
        ))
        return jsonify({'status': 'Task updated successfully'}), 200
    else:
        # Deletes a task
        db.execute_update('DELETE FROM task WHERE id=? AND project_id=?', (task_id, project_id))
        return jsonify({'status': 'Task deleted successfully'}), 200

@app.route('/api/tasks/<int:task_id>/completed/', methods=['PATCH'])
def update_task_completed(task_id):
    """
    Updates only the completed status of a task.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    task = db.execute_query(
        'SELECT t.* FROM task t JOIN project p ON t.project_id = p.id WHERE t.id=? AND p.user_id=?',
        (task_id, g.user['id'])).fetchone()
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()
    db.execute_update('UPDATE task SET completed=? WHERE id=?', (
        data['completed'], task_id
    ))
    # Retorna o status atualizado para verificar se a atualização ocorreu corretamente
    updated_task = db.execute_query('SELECT * FROM task WHERE id=?', (task_id,)).fetchone()
    return jsonify({'status': 'Task completion status updated successfully',
                    'completed': updated_task['completed']}), 200

@app.route('/api/messages/', methods=['GET', 'POST'])
def message_list():
    """
    List and send messages.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        # Returns the list of messages for the user
        messages = db.execute_query(
            'SELECT * FROM message WHERE receiver_id=?', (g.user['id'],)).fetchall()
        return jsonify(messages)
    else:
        # Sends a message to another user
        data = request.get_json()
        if 'receiver_id' not in data or 'content' not in data or not data['content']:
            return jsonify({'error': 'Invalid data'}), 400
        timestamp = datetime.now(timezone.utc).isoformat()
        message_id = db.execute_update(
            'INSERT INTO message (sender_id, receiver_id, content, timestamp) '
            'VALUES (?, ?, ?, ?)', (
            g.user['id'], data['receiver_id'], data['content'], timestamp
        ))
        return jsonify({'status': 'Message sent successfully', 'id': message_id}), 201

@app.route('/api/messages/<int:message_id>/', methods=['GET', 'DELETE'])
def message_detail(message_id):
    """
    Message detail.
    Requires authorization.
    """
    if not g.user:
        return jsonify({'error': 'Unauthorized'}), 403

    message = db.execute_query(
        'SELECT * FROM message WHERE id=? AND (sender_id=? OR receiver_id=?)',
        (message_id, g.user['id'], g.user['id'])).fetchone()
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'GET':
        # Returns a message
        return jsonify(message)
    else:
        # Deletes a message
        db.execute_update('DELETE FROM message WHERE id=?', (message_id,))
        return jsonify({'status': 'Message deleted successfully'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
