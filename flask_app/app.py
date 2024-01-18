import os
from flask import session
from flask import Flask, request, redirect, url_for, flash, render_template
from flask import jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChatConversation, GeneratedImage
import csv
from openai import OpenAI
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# Database configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1234@db:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Convert Path
# database_path = os.path.abspath(r'flask_app\instance\database.db')
# formatted_path = 'sqlite:///' + database_path.replace('\\', '/')

# # Set the SQLAlchemy Database URI
# app.config['SQLALCHEMY_DATABASE_URI'] = formatted_path
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    with open('gpt_store/output.csv', 'r', encoding='utf-8') as file:
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
    with open('prompts/prompts.csv', 'r', encoding='utf-8') as file: 
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' , port=5000)
