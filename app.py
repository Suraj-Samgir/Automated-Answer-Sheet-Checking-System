from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer, util

import pytesseract
from PIL import Image
import os
import google.generativeai as genai

# Initialize the Flask app
app = Flask(__name__)

# Set the path to the Tesseract-OCR executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this with your path

# Initialize the Gemini API with your API key from environment variables
genai.configure(api_key="AIzaSyBP4k6WmosnfuoUnRSyh-g4BlixOKhkXto")  # Ensure the API key is set as an environment variable

# Load pre-trained Sentence-BERT model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def matchStrings(original_text, student_text):
    # Original and student's text
    
    # student_text = "Plants use sunlight to create energy during photosynthesis."

    # Convert texts to embeddings
    original_embedding = model.encode(original_text, convert_to_tensor=True)
    student_embedding = model.encode(student_text, convert_to_tensor=True)

    # Calculate cosine similarity
    similarity = util.pytorch_cos_sim(original_embedding, student_embedding)

    # Convert similarity score to percentage
    similarity_percentage = float(similarity.item()) * 100
    # print(f"Similarity: {similarity_percentage:.2f}%")

    return similarity_percentage

def calcGrade(simPer):
    if(simPer >= 90):
        return 'A'
    elif(simPer >= 80 and simPer < 90):
        return 'B'
    elif(simPer >= 65 and simPer < 80):
        return 'C'
    elif(simPer >= 50 and simPer < 65):
        return 'D'
    elif(simPer >= 35 and simPer < 50):
        return 'E'
    else:
        return 'F'

# Define a route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods = ['POST','GET'])
def submit():
    if request.method == 'POST':
        image = request.files['inputfile']
        if image.filename != '':
            img_path = "static/uploads/"+image.filename
            image.save(img_path)

            # start of text extraction ........

            # Open the image using PIL
            img = Image.open(img_path)

            # Use Tesseract to do OCR on the image
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(img, config=custom_config)

            # Display the extracted text
            print("\nExtracted Text:")
            print(extracted_text)

            # Use the Gemini model for text generation (correction)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate corrected text from the extracted text
            prompt = f"Correct the following text without adding extra words: '{extracted_text}'."
            corrected_response = model.generate_content(prompt)  # Use the correct method to generate content

            # Extract the corrected text from the response
            corrected_text = corrected_response.text if corrected_response and hasattr(corrected_response, 'text') else 'No corrected text returned.'

            # Display the corrected text
            print("\nCorrected Text:")
            print(corrected_text)

            # start of text comparison .........

            original_text = "This image is for testing of EDI."
            similarity_percentage = matchStrings(original_text, corrected_text) 
            # similarity_percentage = matchStrings(corrected_text)           
            grade = calcGrade(similarity_percentage)

            return render_template('index.html',result=f"{similarity_percentage:.2f}", grade=grade)
    
    return "Please Enter an Image!"
    
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
