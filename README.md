````markdown
# 🧠 Sentimentel-Dashboard  

A **real-time Reddit Sentiment Analysis Dashboard** that visualizes emotional trends, live discussions, and keyword insights — all powered by **Python, Dash, and VADER**.

---

## 🌐 Overview  

**Sentimentel-Dashboard** continuously collects live Reddit comments and performs sentiment analysis to determine how the online community feels about trending topics.  
It updates automatically, showing positive, negative, and neutral trends in real-time with interactive charts and live comment feeds.  

---

## 🖼️ Preview  

> *(Optional: Add a screenshot of your dashboard here)*  
> Example:  
> ![Dashboard Preview](assets/dashboard-preview.png)

---

## ⚙️ Tech Stack  

| Component | Technology |
|------------|-------------|
| **Frontend / Dashboard** | Dash + Plotly |
| **Sentiment Analysis** | NLTK (VADER Sentiment Analyzer) |
| **Streaming Engine** | PRAW (Python Reddit API Wrapper) |
| **Data Handling** | Pandas |
| **Language** | Python 3 |

---

## 🚀 Setup & Installation  

Follow the steps below carefully to run the dashboard successfully 👇  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/ascend-x/Sentimentel-Dashboard.git
cd Sentimentel-Dashboard/
````

---

### 2️⃣ Create and Activate Virtual Environment

#### 🧩 For Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🧩 For Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install All Required Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Download NLTK Data Files (One-time Setup)

```bash
python
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('stopwords')
>>> nltk.download('averaged_perceptron_tagger')
>>> exit()
```

This ensures all the required NLP tokenizers and analyzers are available locally.

---

## 🧰 Running the Application

### ▶️ Step 1: Start the Reddit Comment Stream

This script collects live Reddit comments and stores them in `live_reddit_comments.csv`.

```bash
python streamer_reddit.py
```

Keep this terminal window running — it continuously fetches data.

---

### ▶️ Step 2: Start the Dashboard

In a **new terminal (same environment)**:

```bash
python dashboard.py
```

Once it starts, open your browser and visit:

```
http://127.0.0.1:8050
```

---

## 📊 Dashboard Features

✅ **Live Reddit Feed:** Stream of the most recent Reddit comments.
✅ **Sentiment Metrics:** Displays total comments, positive %, and negative %.
✅ **Trending Words:** Updates automatically — filters out filler, stop, and grammar words.
✅ **Top Comments Panel:** Shows the most impactful or emotionally strong comments.
✅ **Neat Layout:** Sections separated with thick borders for clear visualization.
✅ **Calm Modern Theme:** A soft white, green, and blue visual scheme.
✅ **Accurate Sentiment Logic:** Uses NLTK’s VADER analyzer for real-time polarity scores.

---

## 🧪 Example Output

* **Total Comments:** 1,000
* **Positive Sentiment:** 36.4%
* **Negative Sentiment:** 40.1%
* **Neutral Sentiment:** 23.5%
* **Trending Keywords:** ["ai", "python", "amazing", "fun", "openai"]

---

## ⚡ Useful Tips

💡 Keep your **Reddit API credentials** active (if using private streams).
💡 The dashboard refreshes automatically — no need to reload manually.
💡 To restart the system, simply rerun `streamer_reddit.py` and then `dashboard.py`.

---

## 🧑‍💻 Author

**👤 Nandakishore V.**

> [@ascend-x](https://github.com/ascend-x)

---

## ⭐ Support

If this project helped you or inspired you,
please give it a ⭐ on GitHub — it helps the project grow!

---

## 📜 License

This project is released under the **MIT License**.
You’re free to use, modify, and distribute it with attribution.

---

🧠 *Sentimentel-Dashboard — Understanding emotions, one comment at a time.*


Those make the README look super professional on GitHub.
```
