from flask import Flask, render_template, request

# Initialize the Flask app
app = Flask(__name__)

# Define a route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods = ['POST','GET'])
def submit():
    if request.method == 'POST':
        img = request.files['inputfile']
        if img.filename != '':
            img_path = "static/uploads/"+img.filename
            img.save(img_path)
            return render_template('index.html')
    
    return "Please Enter an Image!"
    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
