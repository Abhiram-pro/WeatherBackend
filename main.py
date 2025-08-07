from flask import Flask, request, jsonify
import snscrape.modules.twitter as sntwitter
from transformers import pipeline

app = Flask(__name__)

# Load the BART summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to fetch latest tweets
def fetch_latest_tweets(username, max_tweets=3):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterUserScraper(username).get_items()):
        if i >= max_tweets:
            break
        tweets.append(tweet.content)
    return " ".join(tweets)

@app.route('/weather-summary', methods=['GET'])
def weather_summary():
    username = request.args.get('username', default='balaji25_t', type=str)
    try:
        tweets = fetch_latest_tweets(username)
        if not tweets:
            return jsonify({"summary": "No recent tweets found."})

        # Truncate to 1024 characters to avoid token overflow
        if len(tweets) > 1024:
            tweets = tweets[:1024]

        summary = summarizer(tweets, max_length=60, min_length=20, do_sample=False)[0]['summary_text']
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
