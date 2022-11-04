from datetime import datetime
from time import time
import flask
from app import app,conn
from flask import abort, render_template, request
from src.user import User
from apsw import Error
from flask_login import login_required, current_user
import bleach

@app.post("/api/new")
@login_required
def new():
    try:
        data = request.get_json()
        if data is None:
            abort(400, "missing data")
        if 'to' not in data or 'message' not in data:
            abort(400, "missing to or message")
        if len(data['message']) == 0:
            abort(400, "empty message")
        if current_user.username in data['to']:
            abort(400, "ERROR: you can't send a message to yourself")
        if type(data['to']) != list:
            abort(400, "ERROR: message recipients must be a list")
        to = data['to']
        if len(to) == 0:
            abort(400, "ERROR: message must have at least one recipient")
        for user in to:
            if type(user) != str:
                abort(400, "ERROR: to must be a list of strings")
            if User.get(user) is None:
                abort(404, f"User {user} does not exist")
        # Check if the message capacity is exceeded
        c = conn[0].cursor()
        stmt = "SELECT COUNT(*) FROM messages WHERE sender = ?;"
        c.execute(stmt, (current_user.username,))
        count = (c.fetchone() or [None])[0]
        c.close()
        if count >= app.config['MAX_MESSAGES']:
            abort(400, "ERROR: message capacity exceeded")
        message = data['message']
        sender = current_user.username
        c = conn[0].cursor()
        timestamp = int(time())
        stmt = f"INSERT INTO messages (sender, datetime, message) VALUES (?,?,?) RETURNING *;"
        c.execute(stmt, (sender, timestamp, message))
        row = c.fetchone() or [None]
        message_id = row[0]
        stmt = f"INSERT INTO message_to_user (message_id, user) VALUES (?,?);"
        for user in to:
            c.execute(stmt, (message_id, user))
        c.close()
        return "Ok", 201
    except Error as e:
        return f'ERROR: {e}', 500

def get_message(cursor, id):
    stmt = f"SELECT * FROM messages WHERE id = ?;"
    cursor.execute(stmt, (id,))
    row = cursor.fetchone()
    if row is None:
        return None
    message = {
        'id': row[0],
        'sender': row[1],
        'message': row[3],
        'datetime': row[4]
    }
    stmt = f"SELECT * FROM message_to_user WHERE message_id = ?;"
    cursor.execute(stmt, (id,))
    rows = cursor.fetchall()
    message['to'] = [row[1] for row in rows]
    return message

@app.get("/api/messages")
@login_required
def messages():
    try:
        stmt = f"SELECT message_id FROM message_to_user WHERE user = ? AND deleted = FALSE;"
        c = conn[0].execute(stmt,(current_user.username,)) 
        rows = c.fetchall()
        rows = [row[0] for row in rows]
        messages = [get_message(c, row) for row in rows]
        c.close()
        return messages, 200
    except Error as e:
        return f'ERROR: {e}', 500

@app.get("/api/messages/sent")
@login_required
def sent():
    try:
        stmt = f"SELECT id, sender, message, datetime FROM messages WHERE sender = ? AND sender_deleted = FALSE;"
        c = conn[0].execute(stmt, (current_user.username,))
        rows = c.fetchall()
        rows = [dict(zip(['id', 'sender', 'message', 'datetime'], row)) for row in rows]
        for row in rows:
            stmt = f"SELECT * FROM message_to_user WHERE message_id = ?;"
            c.execute(stmt, (row["id"],))
            to_rows = c.fetchall()
            row['to'] = [to_row[1] for to_row in to_rows]
        c.close()
        return rows, 200
    except Error as e:
        return f'ERROR: {e}', 500

@app.get("/api/messages/<int:id>")
@login_required
def message(id):
    try:
        c = conn[0].cursor()
        message = get_message(c, id)
        c.close()
        return message, 200
    except Error as e:
        return f'ERROR: {e}', 500

@app.errorhandler(400)
@app.errorhandler(404)
def bad_request(error):
    return f'{error.description}', error.code

@app.get('/message/<int:id>')
@app.get('/message/<int:id>.html')
@login_required
def message_html(id):
    c = conn[0].cursor()
    message = get_message(c, id)
    c.close()
    if message is None:
        return 404, "Message not found"
    date = datetime.fromtimestamp(message['datetime'])
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    message["to"] = ", ".join(message["to"])
    return render_template('message.html', message=message, date=date)


@app.delete('/api/messages/hard/<int:id>')
@login_required
def delete_force(id):
    print("hard delete")
    # If the user is the sender, delete the message from the messages table
    stmt = f"SELECT * FROM messages WHERE id = ? AND sender = ?;"
    c = conn[0].execute(stmt, (id, current_user.username))
    rows = c.fetchall()
    c.close()
    if len(rows) == 0:
        return "ERROR: you can't delete this message", 403
    stmt = f"DELETE FROM messages WHERE id = ?;"
    c = conn[0].execute(stmt, (id,))
    c.close()
    # Delete the message from the message_to_user table
    stmt = f"DELETE FROM message_to_user WHERE message_id = ?;"
    c = conn[0].execute(stmt, (id,))
    c.close()
    return "Deleted", 204

@app.delete('/api/messages/<int:id>')
@login_required
def delete(id):
    try:
        # check if message exists
        c = conn[0].cursor()
        message = get_message(c, id)
        if message is None:
            abort(404, "Message not found")
        # if message is sent by current user, mark it as deleted
        stmt = f"UPDATE messages SET sender_deleted = 1 WHERE id = ? AND sender = ? RETURNING *;"
        c = conn[0].execute(stmt, (id, current_user.username))
        rows = c.fetchall()
        c.close()
        if len(rows) == 0:
            # If the user is a recipient, update the deleted field of the message for the user
            stmt = f"UPDATE message_to_user SET deleted = 1 WHERE message_id = ? AND user = ? RETURNING *; "
            c = conn[0].execute(stmt, (id, current_user.username))
            rows = c.fetchall()
            c.close()
            if len(rows) == 0:
                return "ERROR : You cant delete this message", 403
        # If the message has been deleted for all users, delete it from the messages table
        stmt = f"SELECT * FROM message_to_user WHERE message_id = ? AND deleted = FALSE;"
        c = conn[0].execute(stmt, (id,))
        rows = c.fetchall()
        c.close()

        if len(rows) == 0:
            stmt = f"DELETE FROM messages WHERE id = ? AND sender_deleted = TRUE;"
            c = conn[0].execute(stmt, (id,))
            c.close()
            # Delete the message from the message_to_user table
            stmt = f"DELETE FROM message_to_user WHERE message_id = ?;"
            c = conn[0].execute(stmt, (id,))
            c.close()

        return "Ok", 200
    except Error as e:
        return f'ERROR: {e}', 500


@app.get('/api/messages/owned/<int:id>')
@login_required
def owned(id):
    # Check if the message exists
    c = conn[0].cursor()
    message = get_message(c, id)
    c.close()
    if message is None:
        return "ERROR: Message not found", 404
    # Check if the user is the sender
    if message['sender'] == current_user.username:
        return "True", 200
    return "False", 200
