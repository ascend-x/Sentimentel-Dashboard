import praw
import csv
import datetime
import os

# --- Reddit API credentials ---
CLIENT_ID = "hMjcX_XPVvK7GKcEVPIbQg"
CLIENT_SECRET = "WWGXjgdH8ysRp6T3ugl3r-YFjvXnyw"
USER_AGENT = "sentiment-analyzer/0.0.1 by ascend-x"
USERNAME = "Nandakishore_V"
PASSWORD = "Nandakishore181206@"

# --- Output file path ---
os.makedirs("data", exist_ok=True)
OUTPUT_FILE = "data/live_reddit_comments.csv"

# --- Create CSV with header if missing ---
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "comment"])

# --- Reddit client setup ---
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    username=USERNAME,
    password=PASSWORD,
)

# --- Subreddits to monitor ---
subreddit = reddit.subreddit(
    "technology+science+worldnews+AskReddit+todayilearned+funny+movies+music+books+health+environment+space+gaming"
)

print(f"[+] Streaming comments from r/{subreddit.display_name}")
print(f"[+] Saving data to {OUTPUT_FILE}\n")

# --- Stream live comments ---
try:
    for comment in subreddit.stream.comments(skip_existing=True):
        timestamp = datetime.datetime.utcnow().isoformat()
        text = comment.body.replace("\n", " ").replace("\r", " ")
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, text])
        print(f"[{timestamp}] Logged: {text[:80]}...")
except KeyboardInterrupt:
    print("\n[!] Stream stopped by user.")
except Exception as e:
    print(f"[!] An error occurred: {e}")
