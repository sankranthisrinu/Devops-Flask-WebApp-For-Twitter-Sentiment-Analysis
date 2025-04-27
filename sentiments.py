from flask import Blueprint, render_template, request
import matplotlib.pyplot as plt
import os
import csv
import re
from textblob import TextBlob
import matplotlib
import random
from datetime import datetime, timedelta
matplotlib.use('agg')

# Register this file as a blueprint
second = Blueprint("second", __name__, static_folder="static", template_folder="templates")

# Render page when URL is called
@second.route("/sentiment_analyzer")
def sentiment_analyzer():
    return render_template("sentiment_analyzer.html")

# Mock Tweet class to simulate Twitter data
class Tweet:
    """Mock Tweet object that mimics the structure needed by the application"""
    def __init__(self, text):
        self.text = text
        
# Mock data generator
def generate_mock_tweets(keyword, count=10):
    """Generate mock tweets related to the keyword"""
    positive_templates = [
        "I really love {keyword}! It's amazing!", 
        "{keyword} is the best thing ever!", 
        "Just tried {keyword} and I'm impressed!",
        "Can't believe how good {keyword} is! Highly recommend!",
        "The new {keyword} features are fantastic!",
        "I'm a big fan of {keyword}, definitely 5 stars!",
        "{keyword} exceeded my expectations today!"
    ]
    
    negative_templates = [
        "Not happy with {keyword}, disappointed.",
        "{keyword} is terrible, wouldn't recommend.",
        "Had a bad experience with {keyword} today.",
        "Why is {keyword} so frustrating to use?",
        "{keyword} needs to improve their service.",
        "I regret buying {keyword}, total waste of money.",
        "Avoid {keyword} at all costs, trust me on this."
    ]
    
    neutral_templates = [
        "Just learned about {keyword}.",
        "Has anyone used {keyword} before?",
        "Looking for information about {keyword}.",
        "What's your opinion on {keyword}?",
        "{keyword} seems to be trending these days.",
        "I've heard mixed reviews about {keyword}.",
        "Not sure how I feel about {keyword} yet."
    ]
    
    templates = {
        'positive': positive_templates,
        'negative': negative_templates,
        'neutral': neutral_templates
    }
    
    tweets = []
    
    # Create a balanced set of tweets (approx 40% positive, 30% negative, 30% neutral)
    for i in range(count):
        if i < count * 0.4:
            template = random.choice(templates['positive'])
        elif i < count * 0.7:
            template = random.choice(templates['negative'])
        else:
            template = random.choice(templates['neutral'])
            
        text = template.format(keyword=keyword)
        tweets.append(Tweet(text))
    
    # Shuffle the tweets to randomize the order
    random.shuffle(tweets)
    return tweets

# Class with main logic
class SentimentAnalysis:
    def __init__(self):
        self.tweets = []
        self.tweetText = []

    # This function uses mock data instead of Twitter API
    def DownloadData(self, keyword, tweets):
        try:
            # Convert tweets to integer
            tweets = int(tweets)
            
            # Generate mock tweets instead of using Twitter API
            self.tweets = generate_mock_tweets(keyword, tweets)
            
            # Open/create a file to append data to
            csvFile = open('result.csv', 'a')
            
            # Use csv writer
            csvWriter = csv.writer(csvFile)

            # Creating variables to store sentiment info
            polarity = 0
            positive = 0
            wpositive = 0
            spositive = 0
            negative = 0
            wnegative = 0
            snegative = 0
            neutral = 0

            # Iterating through mock tweets
            for tweet in self.tweets:
                # Append cleaned tweet text to list
                clean_text = self.cleanTweet(tweet.text)
                self.tweetText.append(clean_text.encode('utf-8'))
                analysis = TextBlob(tweet.text)
                polarity += analysis.sentiment.polarity

                # Categorize sentiment
                if analysis.sentiment.polarity == 0:
                    neutral += 1
                elif 0 < analysis.sentiment.polarity <= 0.3:
                    wpositive += 1
                elif 0.3 < analysis.sentiment.polarity <= 0.6:
                    positive += 1
                elif 0.6 < analysis.sentiment.polarity <= 1:
                    spositive += 1
                elif -0.3 < analysis.sentiment.polarity <= 0:
                    wnegative += 1
                elif -0.6 < analysis.sentiment.polarity <= -0.3:
                    negative += 1
                elif -1 < analysis.sentiment.polarity <= -0.6:
                    snegative += 1

            # Write to csv and close file
            csvWriter.writerow(self.tweetText)
            csvFile.close()

            # Calculate percentages
            positive = self.percentage(positive, tweets)
            wpositive = self.percentage(wpositive, tweets)
            spositive = self.percentage(spositive, tweets)
            negative = self.percentage(negative, tweets)
            wnegative = self.percentage(wnegative, tweets)
            snegative = self.percentage(snegative, tweets)
            neutral = self.percentage(neutral, tweets)

            # Calculate average polarity
            polarity = polarity / tweets if tweets > 0 else 0

            # Determine overall sentiment for HTML display
            if polarity == 0:
                htmlpolarity = "Neutral"
            elif 0 < polarity <= 0.3:
                htmlpolarity = "Weakly Positive"
            elif 0.3 < polarity <= 0.6:
                htmlpolarity = "Positive"
            elif 0.6 < polarity <= 1:
                htmlpolarity = "Strongly Positive"
            elif -0.3 < polarity <= 0:
                htmlpolarity = "Weakly Negative"
            elif -0.6 < polarity <= -0.3:
                htmlpolarity = "Negative"
            elif -1 < polarity <= -0.6:
                htmlpolarity = "Strongly Negative"
            else:
                htmlpolarity = "Unknown"

            # Generate pie chart
            self.plotPieChart(positive, wpositive, spositive, negative,
                            wnegative, snegative, neutral, keyword, tweets)
            print(f"Analysis complete - Polarity: {polarity}, Sentiment: {htmlpolarity}")
            return polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets
            
        except Exception as e:
            print(f"Error in DownloadData: {e}")
            # Return default values in case of error
            return 0, "Error", 0, 0, 0, 0, 0, 0, 0, keyword, 0

    def cleanTweet(self, tweet):
        # Remove links, special characters, etc. from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    # Function to calculate percentage
    def percentage(self, part, whole):
        if whole == 0:
            return "0.00"
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    # Function to plot and save pie chart
    def plotPieChart(self, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword, tweets):
        try:
            # Convert string percentages to float for the chart
            sizes = [float(positive), float(wpositive), float(spositive), 
                     float(neutral), float(negative), float(wnegative), float(snegative)]
            
            # Skip chart creation if all values are zero
            if sum(sizes) == 0:
                print("No data to plot")
                return
            
            # Create a larger figure with better proportions    
            fig = plt.figure(figsize=(10, 8))
            
            labels = ['Positive [' + str(positive) + '%]', 'Weakly Positive [' + str(wpositive) + '%]',
                    'Strongly Positive [' + str(spositive) + '%]', 'Neutral [' + str(neutral) + '%]',
                    'Negative [' + str(negative) + '%]', 'Weakly Negative [' + str(wnegative) + '%]',
                    'Strongly Negative [' + str(snegative) + '%]']
            
            colors = ['yellowgreen', 'lightgreen', 'darkgreen', 'gold', 'red', 'lightsalmon', 'darkred']
            patches, texts = plt.pie(sizes, colors=colors, startangle=90)
            plt.legend(patches, labels, loc="best")
            plt.axis('equal')
            
            # Add title with more padding
            plt.title(f'Sentiment Analysis for "{keyword}" ({tweets} tweets)', pad=20, fontsize=14)
            
            # Adjust layout to provide more space at the top
            plt.subplots_adjust(top=0.85)
            
            # Create the images directory if it doesn't exist
            os.makedirs('static/images', exist_ok=True)
            
            # Use a platform-independent path for the image
            strFile = os.path.join('static', 'images', 'plot1.png')
            
            # Remove the file if it exists
            if os.path.isfile(strFile):
                os.remove(strFile)
                
            # Save with higher DPI for better quality and tight bounding box
            plt.savefig(strFile, dpi=100, bbox_inches='tight')
            plt.close()  # Close figure to free memory
            print(f"Chart saved to {strFile}")
            
        except Exception as e:
            print(f"Error in plotPieChart: {e}")

@second.route('/sentiment_logic', methods=['POST', 'GET'])
def sentiment_logic():
    try:
        # Get user input from HTML form
        keyword = request.form.get('keyword', 'default')
        tweets = request.form.get('tweets', '10')
        
        # Basic validation
        if not keyword or keyword.strip() == '':
            keyword = 'example'
        
        try:
            tweet_count = int(tweets)
            if tweet_count <= 0:
                tweet_count = 10
        except ValueError:
            tweet_count = 10
        
        sa = SentimentAnalysis()
        
        # Set variables for Jinja template
        polarity, htmlpolarity, positive, wpositive, spositive, negative, wnegative, snegative, neutral, keyword1, tweet1 = sa.DownloadData(
            keyword, tweet_count)
        
        return render_template('sentiment_analyzer.html', 
                              polarity=polarity, 
                              htmlpolarity=htmlpolarity, 
                              positive=positive, 
                              wpositive=wpositive, 
                              spositive=spositive, 
                              negative=negative, 
                              wnegative=wnegative, 
                              snegative=snegative, 
                              neutral=neutral, 
                              keyword=keyword1, 
                              tweets=tweet1,
                              demo_mode=True)  # Add flag to indicate demo mode
    
    except Exception as e:
        print(f"Error in sentiment_logic: {e}")
        return render_template('sentiment_analyzer.html', error=str(e))

@second.route('/visualize')
def visualize():
    return render_template('PieChart.html')