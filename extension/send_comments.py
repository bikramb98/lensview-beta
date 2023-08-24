from flask import Flask, request, jsonify
from flask_cors import CORS  # Import the CORS module
from bs4 import BeautifulSoup
import pickle 
import time
import json
from get_comments import GetComments
from process_url import URLProcessing
import hashlib

app = Flask(__name__)
CORS(app)

url_processing = URLProcessing()

#TODO: Implement cleaning of URL and getting the hash of the URL here

# get_comments = GetComments(hashedURL="bddb69402b4c0f8bf503f5a53a50453c8f0ecfd8",lensID="0x8d88")

@app.route('/')
def home():
    return 'Server is running!'

@app.route('/api/analyze-url', methods=['GET', 'POST'])
def analyze_url():
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url', '')
        print(f"Received URL: {url}")
        processed_url = url_processing.get_cleaned_url(url)[0]
        url_for_sha = processed_url.encode('utf-8')
        hashed_var = hashlib.sha1(url_for_sha).hexdigest()
        # print(hashed_var)
        # url_sha1 = hashlib.sha1(str(processed_url)).hexdigest()
        print(f"sha:{str(hashed_var)}")

        get_comments = GetComments(hashedURL=str(hashed_var),lensID="0x8eb1")
        print(f"Processed URL: {processed_url}")
        post_id = get_comments.get_post_id()
        if post_id == 0:
            comments_list = ['Be the first one to comment on this webpage!']
        else:
            comments_list = get_comments.get_comments(post_id=post_id)
        # print("numb comments: ", len(comments_list))
        response_data = {'post_id': post_id, 'comments_list':comments_list}
    else:
        result = "Send a POST request with a URL"
    # return jsonify(result=comments_list)
    return json.dumps(response_data)

if __name__ == '__main__':
    app.run(port=5000)
