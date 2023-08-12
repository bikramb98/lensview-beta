from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS module
from bs4 import BeautifulSoup
import pickle 
import time
from get_comments import GetComments

app = Flask(__name__)
CORS(app)

#TODO: Implement cleaning of URL and hasing here

get_comments = GetComments(hashedURL="bddb69402b4c0f8bf503f5a53a50453c8f0ecfd8",lensID="0x8d88")

@app.route('/')
def home():
    return 'Server is running!'

@app.route('/api/analyze-url', methods=['GET', 'POST'])
def analyze_url():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url', '')
        print(f"Received URL: {url}")
        post_id = get_comments.get_post_id()
        comments_list = get_comments.get_comments(post_id=post_id)
    else:
        result = "Send a POST request with a URL"
    return jsonify(result=comments_list)

if __name__ == '__main__':
    app.run(port=5000)
