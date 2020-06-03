from app.helper.messageData import getMessageData, getDateChunks
import threading
import json
from app import app, db, chatbot, grammar_checker, spell_checker
import os 
from datetime import datetime, timedelta
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Message, UserData
import sys
import truecase
from flask import (
    jsonify,
    request,
    redirect
)
import speech_recognition as sr
from werkzeug.datastructures import ImmutableMultiDict

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
        current_date = datetime.now()
        lastLogin = user.lastLogin
        if (current_date - timedelta(hours=24) < lastLogin) and (current_date.day > lastLogin.day):
        	user.userData[0].loginStreak += 1
        user.lastLogin = current_date
        return jsonify({
            "status": "Logged In",
            "lastLogin": lastLogin,
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
    data = UserData(messagesSent=0, wordCount=0, loginStreak=0, correctSentences=0,  author=user)
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
    period = request.json.get('period', None)
    user = User.query.filter_by(id=current_user.get_id()).first()
    messages = Message.query.filter_by(order=1, user_id=user.id).all()


    message_chunks = getMessageData(messages, period)
    print("MEssage CHUNKS ", message_chunks)
    correct_rates = [(sum(message_chunk)/len(message_chunk)*100 if len(message_chunk) else 0) for message_chunk in message_chunks]

    date_chunks = getDateChunks(period)

    return jsonify({
        "username": user.username,
        "authenticated": True,
        "ID": current_user.get_id(),
        "messagesSent": current_user.userData[0].messagesSent,
        "wordCount": current_user.userData[0].wordCount,
        "loginStreak": current_user.userData[0].loginStreak,
        "correctSentences": current_user.userData[0].correctSentences,
        "message_chunks": correct_rates,
        "date_chunks": date_chunks
    })

@app.route('/getAudio', methods=['GET', 'POST'])
def getAudio():
	if "file" not in request.files:
		return jsonify({
			"status": "No File Provided"	
		})	
	file = request.files['file']
	text = ""

	if file:
		data = None
		with open("speechToText.json", "r") as config_file:
			data = json.dumps(json.load(config_file))
		recognizer = sr.Recognizer()
		audio_file = sr.AudioFile(file)
		with audio_file as source:
			audio_data = recognizer.record(source)
			text = recognizer.recognize_google_cloud(audio_data, credentials_json=data)
		return jsonify({
			"body": text
		})
	return jsonify({
		"status": "No File"
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
    messagesSent = current_user.userData[0].messagesSent
    current_user.userData[0].wordCount += len(body.split(" "))
    m = Message(body=body, author=user, order=order)
    db.session.add(m)
    return generateReply(body, m)
    

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

# @app.route('/generateReply', methods=['GET', 'POST'])
def generateReply(body, db_message):
    if not current_user.is_authenticated:
        return jsonify({
            "status": "Page Blocked",
            "authenticated": False
        })
    # return jsonify({
	   #  "chatbot_response" : {
	   #      "body": "Response",
	   #      "timestamp": 10,
	   #      "order": 2
	   #  },
	   #  "grammar_correction" : {
    #         "body": "Response",
    #         "timestamp": 10,
    #         "order": 2
    #     }
    # })

    user = current_user
    message = addPunctuation(spell_checker.correct_sentence(truecase.get_true_case(body)))		# fix capitalization, spelling, and punctuation
    chatbot_body = ''
    print('Before Prediction')
    print('NUMBER OF THREADS: ', threading.active_count())
    if ('bye' in message.lower()):
        chatbot_body = 'See you later!'
    else:
        chatbot_body = chatbot.predictResponse(context=message)
    print('DOne Predicting')
    chatbot_body = truecase.get_true_case(chatbot_body)
    grammar_correction_response = grammar_checker.check_grammar(input_sentence=message)
    stripped_message = stripChars(message)
    stripped_correction = stripChars(grammar_correction_response)
    grammar_body = ''
    if stripped_message == stripped_correction or len(message.split(' ')) <= 2:
    	user.userData[0].correctSentences += 1
    	db_message.correct = 1
    else:
    	formatted_grammar_response = truecase.get_true_case(grammar_correction_response)
    	grammar_body = 'Did you mean: ' + formatted_grammar_response
    	db_message.correct = 0
    order = 2
    chatbot_response = Message(body=chatbot_body, author=user, order=order)
    
    
    db.session.add(chatbot_response)
    if grammar_body != '':
    	grammar_correction = Message(body=grammar_body, author=user, order=order)
    	db.session.add(grammar_correction)
    db.session.commit()
    return jsonify({
        "chatbot_response" : {
            "body": chatbot_response.body,
            "timestamp": chatbot_response.timestamp,
            "order": chatbot_response.order,
        },
        "grammar_correction" : {
            "body": grammar_body,
            "timestamp": 0 if grammar_body=='' else grammar_correction.timestamp,
            "order": 0 if grammar_body=='' else grammar_correction.order,
        }
    })



def stripChars(sequence):
	toRemove = set(['.', '?', ' ', '!'])
	return ''.join([c for c in sequence if c not in toRemove]).lower()

def addPunctuation(sentence):
    punctuation = ['.', '?', '!']
    if (sentence[-1] in punctuation):       # already puncuated
        return sentence
    question_words = ['who', 'what', 'where', 'when', 'why', 'how', 'do', 'which']
    if (0 in [sentence.lower().find(question_word) for question_word in question_words]):  # if sentence begins with question_word
        sentence += '?'
    return sentence



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
