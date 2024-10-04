from flask import Flask, request, jsonify, render_template
import cv2
import pytesseract
import re
import os

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the function to extract feature values using regex
def extract_feature_values(text):
    features = {}
    
    # Define regex patterns for each feature (assuming they follow a specific format)
    features['concave_points_worst'] = re.search(r'Concave Points \(Worst\):\s*([\d.]+)', text)
    features['perimeter_worst'] = re.search(r'Perimeter \(Worst\):\s*([\d.]+)', text)
    features['concave_points_mean'] = re.search(r'Concave Points \(Mean\):\s*([\d.]+)', text)
    features['radius_worst'] = re.search(r'Radius \(Worst\):\s*([\d.]+)', text)
    features['perimeter_mean'] = re.search(r'Perimeter \(Mean\):\s*([\d.]+)', text)
    features['area_worst'] = re.search(r'Area \(Worst\):\s*([\d.]+)', text)
    features['radius_mean'] = re.search(r'Radius \(Mean\):\s*([\d.]+)', text)
    features['area_mean'] = re.search(r'Area \(Mean\):\s*([\d.]+)', text)
    features['concavity_mean'] = re.search(r'Concavity \(Mean\):\s*([\d.]+)', text)
    features['concavity_worst'] = re.search(r'Concavity \(Worst\):\s*([\d.]+)', text)
    features['compactness_mean'] = re.search(r'Compactness \(Mean\):\s*([\d.]+)', text)
    
    # Extract the values and clean up the result
    for feature, match in features.items():
        if match:
            features[feature] = match.group(1)
        else:
            features[feature] = None  # Handle missing values

    return features

# Helper function to perform OCR on an image
def perform_ocr(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    
    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(binary_image)
    return text

# Root route to serve the index.html page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_report', methods=['POST'])
def upload_report():
    file = request.files['report']
    
    # Check if the uploaded file is an image
    if file and (file.filename.endswith('.png') or file.filename.endswith('.jpg') or file.filename.endswith('.jpeg')):
        # Save the uploaded image
        image_path = 'uploaded_report.jpg'
        file.save(image_path)
        
        # Extract text from the image
        extracted_text = perform_ocr(image_path)
        
        # Extract feature values from the OCR text
        extracted_values = extract_feature_values(extracted_text)
        
        # Clean up saved image
        os.remove(image_path)
        
        # Return the extracted feature values as JSON
        return jsonify(extracted_values)
    else:
        return jsonify({'error': 'File type not allowed. Please upload an image.'}), 400



if __name__ == '__main__':
    app.run(debug=True)
