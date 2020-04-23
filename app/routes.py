from app import app, db
import os 
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Message, UserData
import sys
from flask import (
    jsonify,
    request,
    redirect
)

@app.route('/')

@app.route('/index')    #decorators modifying the function following it
def index():
    return "Hello, World!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return jsonify({
            "status": "Logged In",
            "authenticated": True
        })
    if request.json:
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return jsonify({
                "status": "Invalid username or password",
                "currentUser": "none",
                "authenticated": False
            })
        login_user(user, remember=True)
        return jsonify({
            "status": "Logged In",
            "currentUser": username,
            "authenticated": current_user.is_authenticated
        })
  
    return jsonify({
        "status": "Login Error",
        "currentUser": "none",
        "authenticated": False
    })

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user:
        logout_user()
        return jsonify({
            "status": "Logged Out"
        })


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    retypePassword = request.json.get('retypePassword', None)
    if password != retypePassword:
        return jsonify({
            "status": "Passwords do not match",
            "password1": password,
            "password2": retypePassword,
            "authenticated": False
        })
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return jsonify({
            "status": "Username already in use",
            "authenticated": False
        })
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    data = UserData(messagesSent=0, author=user)
    db.session.add(data)
    db.session.commit()
    login_user(user, remember=True)
    return jsonify({
        "status": "New user " + username + " registered",
        "authenticated": True
    })

    
@app.route('/landing', methods=['GET', 'POST'])
def landing():
    if not current_user.is_authenticated:
        return jsonify({
            "status": "Page Blocked",
            "authenticated": False
        })
    
    user = User.query.filter_by(id=current_user.get_id()).first()
    username = user.username
    return jsonify({
        "username": username,
        "authenticated": True,
        "ID": current_user.get_id(),
        "messagesSent": current_user.userData[0].messagesSent
    })

@app.route('/send', methods=['GET', 'POST'])
def send():
    if not current_user.is_authenticated:
        return jsonify({
            "status": "Page Blocked",
            "authenticated": False
        })
    body = request.json.get('body', None)
    order = request.json.get('order', None)
    user = current_user
    current_user.userData[0].messagesSent += 1
    m = Message(body=body, author=user, order=order)
    db.session.add(m);
    db.session.commit();
    return jsonify({
        "username": user.username,
        "authenticated": True,
        "ID": user.get_id(),
        "message": m.body,
        "timestamp": m.timestamp,

    })

@app.route('/pullMessages', methods=['GET', 'POST'])
def pullMessages():
    user = current_user
    messages = user.messages
    json_messages = []
    for m in messages:
        json_messages.append(
            {
                "body": m.body,
                "timestamp": m.timestamp,
                "order": m.order
            }
        )
    return jsonify(json_messages)

@app.route('/generateReply')
def generateReply():
    if not current_user.is_authenticated:
        return jsonify({
            "status": "Page Blocked",
            "authenticated": False
        })
    body = "Mock Generator"
    order = 2
    user = current_user
    m = Message(body=body, author=user, order=order)
    db.session.add(m);
    db.session.commit();
    return jsonify({
        "body": m.body,
        "timestamp": m.timestamp,
        "order": m.order,
    })

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)