import os
import pickle
import numpy as np
import librosa
import librosa.display
import tensorflow as tf
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['ser_app']
users_collection = db['users']

# Load the trained model and scaler
MODEL_PATH = "C:\\Users\\soham\\OneDrive\\Desktop\\SGP-3\\SER\\backend\\ravdess_emotion_model.h5"
SCALER_PATH = "C:\\Users\\soham\\OneDrive\\Desktop\\SGP-3\\SER\\backend\\ravdess_scaler.pkl"
model = tf.keras.models.load_model(MODEL_PATH)
with open(SCALER_PATH, 'rb') as f:
    scaler = pickle.load(f)

# Emotion Labels
EMOTIONS = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]

# Improved feature extraction
def extract_features(audio_path):
    try:
        # Load audio with error handling
        y, sr = librosa.load(audio_path, sr=22050, duration=3)  # Fixed duration for consistency
        
        # Basic audio preprocessing
        y = librosa.effects.preemphasis(y)  # Reduce noise
        
        # Extract features with more robust parameters
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40, n_fft=2048, hop_length=512)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048, hop_length=512)
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
        
        # Calculate mean features
        mfcc = np.mean(mfcc.T, axis=0)
        chroma = np.mean(chroma.T, axis=0)
        mel = np.mean(mel.T, axis=0)

        features = np.hstack([mfcc, chroma, mel])
        features = np.nan_to_num(features)

        # Ensure consistent feature size
        expected_features = 63
        if features.shape[0] != expected_features:
            if features.shape[0] < expected_features:
                features = np.pad(features, (0, expected_features - features.shape[0]))
            else:
                features = features[:expected_features]

        return features
    except Exception as e:
        print(f"Feature extraction error: {e}")
        return None

@app.route('/')
def home():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('signin'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        # Enhanced audio validation
        y, sr = librosa.load(filepath, sr=None)  # First load to check duration
        if len(y)/sr < 0.5:  # Minimum 0.5 second duration
            return jsonify({'error': 'Audio too short (min 0.5 seconds required)'}), 400
        
        features = extract_features(filepath)
        if features is None:
            return jsonify({'error': 'Feature extraction failed - possibly corrupt audio'}), 400
        
        # Scale the features
        features = scaler.transform([features])
        
        # Get prediction probabilities
        prediction = model.predict(features, verbose=0)[0]
        
        # Convert to percentages and round
        percentages = [round(float(p)*100, 2) for p in prediction]
        
        # Get top emotion
        emotion_idx = np.argmax(prediction)
        predicted_emotion = EMOTIONS[emotion_idx]
        confidence = percentages[emotion_idx]
        
        # Validate confidence threshold
        if confidence < 20:  # 20% minimum confidence threshold
            return jsonify({
                'emotion': 'uncertain',
                'message': 'Low confidence in prediction',
                'probabilities': dict(zip(EMOTIONS, percentages))
            })
        
        return jsonify({
            'emotion': predicted_emotion,
            'confidence': confidence,
            'probabilities': dict(zip(EMOTIONS, percentages))
        })
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': 'Audio processing failed. Please try again.'}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# Authentication Routes (unchanged)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = generate_password_hash(request.form['password'].strip())
        if users_collection.find_one({'email': email}):
            flash('Email already exists!', 'danger')
            return redirect(url_for('signup'))
        users_collection.insert_one({'email': email, 'password': password, 'verified': True})
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        user = users_collection.find_one({'email': email})
        if not user:
            flash('User not found!', 'danger')
            return redirect(url_for('signin'))
        if not user['verified']:
            flash('Email not verified! Check your inbox.', 'warning')
            return redirect(url_for('signin'))
        if check_password_hash(user['password'], password):
            session['user'] = email
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect password!', 'danger')
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out!', 'info')
    return redirect(url_for('signin'))

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)