from flask import Flask, request, jsonify, render_template, redirect, url_for
import joblib
import numpy as np
from flask_cors import CORS
from pymongo import MongoClient
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from the React frontend

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB connection string
db = client['cancer']  # Replace with your database name
users_collection = db['users']  # Collection for user data

# Load the trained model
model_path = os.path.join('model', 'cancer_classification1.pickle1')
model = joblib.load(model_path)

# Define the root route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Define the signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        # Store the user data in the database without hashing the password
        user_data = {
            'full_name': full_name,
            'email': email,
            'password': password  # Storing plain text password (not recommended)
        }
        users_collection.insert_one(user_data)

        # Redirect to login page after signup
        return redirect(url_for('login'))

    return render_template('signup.html')

# Define the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists in the database
        user = users_collection.find_one({'email': email, 'password': password})
        if user:
            return redirect(url_for('prediction'))  # Redirect to prediction page after successful login
        else:
            return "Invalid credentials!"  # You can render an error message on the login page instead
    return render_template('login.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get data from request
    data = request.json
    features = [data['concave_points_worst'], data['perimeter_worst'], data['concave_points_mean'],
                data['radius_worst'], data['perimeter_mean'], data['area_worst'],
                data['radius_mean'], data['area_mean'], data['concavity_mean'],
                data['concavity_worst'], data['compactness_mean']]

    # Convert features to numpy array for prediction
    final_features = [np.array(features)]

    # Make prediction using the loaded model
    prediction = model.predict(final_features)
    
    # Convert prediction result to a response
    if prediction[0]==1:
        output='Malignant'
    else:
        output='Benign'
    
    return jsonify({'prediction': output})

# Define the prediction page
@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
