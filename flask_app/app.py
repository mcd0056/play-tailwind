import os
from flask import session
from flask import Flask, request, redirect, url_for, flash, render_template
from flask import jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, ChatConversation, GeneratedImage
import csv
from openai import OpenAI
import base64
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# # Database configuration (PostgreSQL)
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@db:5432/postgres"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Convert Path
database_path = os.path.abspath(r'flask_app\instance\database.db')
formatted_path = 'sqlite:///' + database_path.replace('\\', '/')

# Set the SQLAlchemy Database URI
app.config['SQLALCHEMY_DATABASE_URI'] = formatted_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Initialize the database
db.init_app(app)

# Script to print all Users
@app.route('/print_users')
def print_users():
    users = User.query.all()
    for user in users:
        print(f'ID: {user.id}, Username: {user.username}, Email: {user.email}')
    return "Users printed to console"

# ---------------------------------------   PAGE ROUTES   --------------------------------------- #

### Home route ###
@app.route('/')
def index():
    return render_template('index.html')

### Signup route ###
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please login.')
            return redirect(url_for('login'))

        # Hash the password for security
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new User
        new_user = User(email=email, password=hashed_password, username=username)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.')
        return redirect(url_for('login'))

    return render_template('signup.html')


### Login route ###
@app.route('/signin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Find user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            session['email'] = email
            flash('You have been successfully logged in.')
            return redirect(url_for('dashboard')) 

        else:
            # User not found or password incorrect
            flash('Invalid email or password. Please try again.')
            return redirect(url_for('login'))

    return render_template('signin.html')

@app.route('/get_api_key', methods=['POST'])
def get_api_key():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    
    if user and email == user.email:
        return jsonify({"openai_api_key": user.openai_api_key})
    else:
        return jsonify({"error": "Invalid credentials"}), 401


### Dashboard route ###
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

### Logout route ###
@app.route('/logout')
def logout():
    return redirect(url_for('index'))

# ---------------------------------------   MAIN   --------------------------------------- #

################# GPT STORE #####################
@app.route('/get-gpt-store-data')
def get_gpt_store_data():
    gpt_store_data = []
    # with open('gpt_store/output.csv', 'r', encoding='utf-8') as file:
    with open('flask_app\\gpt_store\\output.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None) # Skip the header row
        for row in csv_reader:
            gpt_store_data.append({
                'name': row[0],
                'description': row[1],
                'image_url': row[2],  
                'link_to_gpt': row[3]  
            })
    return jsonify(gpt_store_data)

################# PROMPTS #####################
@app.route('/get-prompts-data', methods=['GET'])
def get_prompt_data():
    prompts_data = []
    # with open('prompts/prompts.csv', 'r', encoding='utf-8') as file:
    with open('flask_app\\prompts\\prompts.csv', 'r', encoding='utf-8') as file: 
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            prompts_data.append({
                'act': row[0],
                'prompt': row[1]
            })
    return jsonify(prompts_data)

################# List ASSISTANTS ##############
@app.route('/list-assistants')
def list_assistants():
    email = session.get('email')
    session['email'] = email
    # Retrieve the logged-in user from the database
    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    # Check if the user has an API key
    if not user.openai_api_key:
        return jsonify({'error': 'OpenAI API key not set for the user'}), 400

    # Use the user's OpenAI API key for the client
    client = OpenAI(api_key=user.openai_api_key)

    try:
        my_assistants = client.beta.assistants.list(order="desc", limit="20")

        assistants_list = []
        for assistant in my_assistants.data:
            assistants_list.append({
                'id': assistant.id,
                'name': assistant.name,
                'model': assistant.model,  
            })

        return jsonify(assistants_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
################# Get Conversations ##############
@app.route('/get-conversations')
def get_conversations():
    if 'email' not in session:
        return jsonify([]) 

    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return jsonify([])

    conversations = ChatConversation.query.filter_by(user_id=user.id).order_by(ChatConversation.timestamp.desc()).all()
    return jsonify([
        {
            'id': conv.id,
            'message': conv.message,
            'response': conv.response,
        } for conv in conversations
    ])

### Get username route ###
@app.route('/get-username')
def get_username():
    if 'email' in session:
        return jsonify({'email': session['email']})
    return jsonify({'email': 'Guest'})

### Delete conversation route ###
@app.route('/delete-conversation/<int:conv_id>', methods=['POST'])
def delete_conversation(conv_id):
    conversation = ChatConversation.query.get(conv_id)
    if conversation:
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'}), 404
    
############### Fetch user images ###############
@app.route('/fetch-user-images', methods=['GET'])
def fetch_user_images():
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    images = GeneratedImage.query.filter_by(user_id=user.id).all()
    if not images:
        return jsonify({'error': 'No images found for user'}), 404

    image_data = [{
        'prompt': image.prompt, 
        'image_data': base64.b64encode(image.image_data).decode('utf-8'),  # Convert binary data to base64
        'timestamp': image.timestamp.isoformat()
    } for image in images]

    return jsonify({'images': image_data})

#### Upadate API key route ####
@app.route('/update-api-key', methods=['POST'])
def update_api_key():
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    new_api_key = data.get('api_key')
    if not new_api_key:
        return jsonify({'error': 'API key is required'}), 400

    user.openai_api_key = new_api_key
    db.session.commit()

    return jsonify({'message': 'API key updated successfully'})



@app.route('/chatbot-response', methods=['POST'])
def chatbot_response():
    user_input = request.json['message']
    response_text = ""  

    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user and user.openai_api_key:
            payload = {
                'user_input': user_input,
                'openai_api_key': user.openai_api_key
            }

            try:
                response = requests.post(
                    'http://localhost:8000/get-response/', 
                    json=payload
                )
                response.raise_for_status()
                response_data = response.json()

                # Extract only the 'output' part of the response
                response_text = response_data.get('response', {}).get('output', '')
            except requests.RequestException as e:
                print("Failed to get response from FastAPI:", e)
                return jsonify({'message': 'Error communicating with AI service'}), 500

            new_conversation = ChatConversation(user_id=user.id, message=user_input, response=response_text)
            db.session.add(new_conversation)
            db.session.commit()
            print("Conversation saved")
            return jsonify({'response': response_text})
        else:
            return jsonify({'message': 'User not found or API key not set'}), 404
    else:
        return jsonify({'message': 'User not logged in'}), 401

################### CHATBOT 2 - GPT-3.5 Turbo ####################

@app.route('/chat_three', methods=['POST'])
def chat_with_gpt_route():
    data = request.get_json()

    prompt_type = data.get('prompt_type', 'default') 
    user_message = data.get('user_message', '')
    system_prompt = data.get('system_prompt', 'You are a helpful assistant') 
    # Use default values if the incoming data contains None
    max_tokens = data.get('max_tokens', 150) or 150
    presence_penalty = data.get('presence_penalty', 0) or 0.0
    temperature = data.get('temperature', 1) or 1.0
    top_p = data.get('top_p', 1) or 1.0

    if not user_message:
        return jsonify({"error": "User message is required"}), 400
    
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user and user.openai_api_key:
            fastapi_server_url = "http://localhost:8000/chat_three"  # Replace with actual FastAPI server URL
            fastapi_data = {
                "prompt_type": prompt_type, 
                "user_message": user_message, 
                "system_prompt": system_prompt, 
                "max_tokens": max_tokens, 
                "presence_penalty": presence_penalty, 
                "temperature": temperature, 
                "top_p": top_p, 
                "openai_api_key": user.openai_api_key
            }
            print("Sending data to FastAPI:", fastapi_data)
            response = requests.post(fastapi_server_url, json=fastapi_data)
            
            if response.status_code == 200:
                response_data = response.json()
                new_conversation = ChatConversation(user_id=user.id, message=user_message, response=response_data['response'])
                db.session.add(new_conversation)
                try:
                    db.session.commit()
                    print("Conversation saved")
                except Exception as e:
                    print("Failed to save conversation:", e)
                    db.session.rollback()
                return jsonify(response_data)
            else:
                return jsonify({"error": "Error from FastAPI server"}), response.status_code
        else:
            return jsonify({'message': 'User not found or API key not set'}), 404
    else:
        return jsonify({'message': 'User not logged in'}), 401
    
############################################## CHATBOT 4 - GPT Vision ##############################################    
# Directory to save uploaded images temporarily
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Retrieve the logged-in user from the database
    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    # Check if the user has an API key
    if not user.openai_api_key:
        return jsonify({'error': 'OpenAI API key not set for the user'}), 400

    # Use the user's OpenAI API key for the client
    client = user.openai_api_key

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    prompt = request.form.get('prompt')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Encoding the image to base64
        base64_image = encode_image(file_path)

        print("Prompt:", prompt)  # Debugging
        print("Image:", base64_image)

        # Prepare the headers for OpenAI API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {client}"
        }

        # Payload for the GPT-4 Vision API
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        # Send request to OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Delete the temporarily saved file
        os.remove(file_path)

        # Return the response
        print("Response:", response.json())
        return jsonify(response.json())

    else:
        return jsonify({"error": "Invalid file type"}), 400    


    
@app.route('/generate-image', methods=['POST'])
def image_endpoint():
    response_text = ""
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    data = request.json
    user = User.query.filter_by(email=session['email']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    fastapi_payload = {
        'prompt': prompt,
        'size': data.get('size', "512x512"),
        'quality': data.get('quality', "standard"),
        'n': data.get('n', 1),
        'openai_api_key': user.openai_api_key
    }

    try:
        response = requests.post('http://localhost:8000/generate-image/', json=fastapi_payload)
        response.raise_for_status()
        response_data = response.json()
        image_url = response_data.get('image_url')

        if not image_url:
            raise ValueError("No image URL returned")
        
        # Download the image and convert it to binary
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = response.content


        new_image = GeneratedImage(user_id=user.id, prompt=prompt, image_data=image_data, timestamp=datetime.utcnow())
        db.session.add(new_image)
        db.session.commit()
        
    except requests.RequestException as e:
        print("Failed to get response from FastAPI:", e)
        return jsonify({'error': 'Error communicating with image generation service'}), 500
    except ValueError as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500    

@app.route('/gpt16k', methods=['POST'])
def gpt16k():
    data = request.get_json()

    prompt_type = data.get('prompt_type', 'default') 
    user_message = data.get('user_message', '')
    system_prompt = data.get('system_prompt', 'You are a helpful assistant') 
    max_tokens = data.get('max_tokens', 150) or 10000
    presence_penalty = data.get('presence_penalty', 0) or 0.0
    temperature = data.get('temperature', 1) or 1.0
    top_p = data.get('top_p', 1) or 1.0

    if not user_message:
        return jsonify({"error": "User message is required"}), 400
    
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user and user.openai_api_key:
            fastapi_server_url = "http://localhost:8000/gpt16k"  # Replace with actual FastAPI server URL
            fastapi_data = {
                "prompt_type": prompt_type, 
                "user_message": user_message, 
                "system_prompt": system_prompt, 
                "max_tokens": max_tokens, 
                "presence_penalty": presence_penalty, 
                "temperature": temperature, 
                "top_p": top_p, 
                "openai_api_key": user.openai_api_key
            }
            print("Sending data to FastAPI:", fastapi_data)
            response = requests.post(fastapi_server_url, json=fastapi_data)
            
            if response.status_code == 200:
                response_data = response.json()
                new_conversation = ChatConversation(user_id=user.id, message=user_message, response=response_data['response'])
                db.session.add(new_conversation)
                try:
                    db.session.commit()
                    print("Conversation saved")
                except Exception as e:
                    print("Failed to save conversation:", e)
                    db.session.rollback()
                return jsonify(response_data)
            else:
                return jsonify({"error": "Error from FastAPI server"}), response.status_code
        else:
            return jsonify({'message': 'User not found or API key not set'}), 404
    else:
        return jsonify({'message': 'User not logged in'}), 401  


@app.route('/webchat', methods=['POST'])
def webchat():
    if 'email' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    data = request.get_json()
    if not client:
        return jsonify({'error': 'User not found or API key not set'}), 404
    
    assistant_id = data.get('assistant_id')
    user_input = data.get('message', '')
    thread_id = data.get('thread_id')

    if not user_input:
        return jsonify({"error": "User message is required"}), 400
    
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        if user and user.openai_api_key:
            client = OpenAI(api_key=user.openai_api_key)
            fastapi_server_url = "http://localhost:8000/webchat"  # Replace with actual FastAPI server URL
            fastapi_data = {
                "assistant_id": assistant_id,
                "user_input": user_input,
                "thread_id": thread_id,
                "openai_api_key": user.openai_api_key
            }
            print("Sending data to FastAPI:", fastapi_data)
            response = requests.post(fastapi_server_url, json=fastapi_data)
            
            if response.status_code == 200:
                response_data = response.json()
                new_conversation = ChatConversation(user_id=user.id, message=user_input, response=response_data['response'])
                db.session.add(new_conversation)
                try:
                    db.session.commit()
                    print("Conversation saved")
                except Exception as e:
                    print("Failed to save conversation:", e)
                    db.session.rollback()
                return jsonify(response_data)
            else:
                return jsonify({"error": "Error from FastAPI server"}), response.status_code
        else:
            return jsonify({'message': 'User not found or API key not set'}), 404
    else:
        return jsonify({'message': 'User not logged in'}), 401
    




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port=5000)
