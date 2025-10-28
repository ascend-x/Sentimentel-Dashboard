import praw
import csv
import datetime
import os

CLIENT_ID = "hMjcX_XPVvK7GKcEVPIbQg"
CLIENT_SECRET = "WWGXjgdH8ysRp6T3ugl3r-YFjvXnyw"
USER_AGENT = "sentiment-analyzer/0.0.1 by ascend-x"
USERNAME = "Nandakishore_V"
PASSWORD = "Nandakishore181206@"

# Name of the output file
OUTPUT_FILE = "live_reddit_comments.csv"

# Create the file and write the header if it doesn't exist
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "comment"])

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    username=USERNAME,
    password=PASSWORD,
)

subreddit = reddit.subreddit("politics") # Switched to a more active subreddit for demo

print(f"Streaming comments from r/{subreddit.display_name}...")
print(f"Saving data to {OUTPUT_FILE}")

try:
    for comment in subreddit.stream.comments(skip_existing=True):
        timestamp = datetime.datetime.utcnow().isoformat()
        text = comment.body.replace("\n", " ").replace("\r", " ")
        # Append the new comment to the CSV
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, text])
        print(f"Logged: {text[:80]}...")
except KeyboardInterrupt:
    print("\nStream stopped.")
except Exception as e:
    print(f"An error occurred: {e}")
