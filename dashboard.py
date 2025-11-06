import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))
STOPWORDS.update([
    # Pronouns and basic verbs
    'he','she','it','they','we','i','you','me','my','your','his','her','their','ours','them','him',
    'is','are','was','were','be','been','am','do','does','did','have','has','had','having',
    'will','shall','would','should','can','could','may','might','must',

    # Articles, prepositions, conjunctions
    'the','a','an','in','on','at','of','for','with','about','as','to','from','by','and','or','if','then',
    'so','because','also','just','like','that','this','these','those','there','here','when','where',

    # Conversational junk
    'get','got','people','think','really','make','made','know','even','say','said','see','go','went',
    'still','thing','things','back','much','many','lot','well','good','bad','yes','no','time','way',
    'now','today','something','someone','every','lot','please','need','going','right','sure','come',
    'take','look','thank','thanks','use','used','using','want','wanted','makes','done','help','actually','post','report',

    # Web and URL noise
    'http','https','www','com','org','net','amp','reddit','r','t','co','u','s','m','n',

    # Misc filler
    'one','two','three','first','second','thing','things','even','still','really','much','make',
    'could','should','would','yes','no','please','kind','right','left','said'
])
STOPWORDS = set(map(str.lower, STOPWORDS))


# --- CONFIG ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="SentimentPulse Dashboard",
)

analyzer = SentimentIntensityAnalyzer()
MAX_DATA_POINTS = 10000
CSV_FILE_PATH = 'data/live_reddit_comments.csv'

def get_sentiment(text):
    score = analyzer.polarity_scores(text)['compound']
    text_lower = text.lower()
    BOOSTS = {'urgent': -0.3, 'amazing': 0.3, 'breaking': 0.3, 'love': 0.3, 'hate': -0.3}
    for word, boost in BOOSTS.items():
        if word in text_lower:
            score += boost
    if "😡" in text or "😠" in text: score -= 0.4
    if "😍" in text or "😁" in text: score += 0.4
    exclamations = text.count("!")
    if exclamations > 2: score += 0.1 * min(exclamations, 5)
    return 'Positive' if score >= 0.05 else 'Negative' if score <= -0.05 else 'Neutral'

def get_trending_words(comments, top_n=10):
    words = []
    for comment in comments:
        # Keep only alphabetic words with 4+ letters
        tokens = re.findall(r'\b[a-zA-Z]{4,}\b', comment.lower())
        clean = [w for w in tokens if w not in STOPWORDS]
        words.extend(clean)
    # Return top N trending words
    return Counter(words).most_common(top_n)


def get_unique_words(new_comments, old_comments):
    new = set(w for c in new_comments for w in re.findall(r'\b\w+\b', c.lower()))
    old = set(w for c in old_comments for w in re.findall(r'\b\w+\b', c.lower()))
    return list(new - old)[:20]

# --- Custom CSS ---
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
        body {
            background-color: #0a0f14;
            font-family: 'Inter', sans-serif;
            color: #e8e8e8;
        }
        .metric-card {
            background: linear-gradient(145deg,#141c24,#0f1419);
            border-radius: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.6);
            padding: 25px;
            text-align: center;
            transition: 0.3s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,255,255,0.3);
        }
        .section-card {
            background: #10171f;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,255,255,0.05);
        }
        .feed-box {
            border-left: 5px solid #00adb5;
            background-color: #1a1f26;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 10px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
'''

# --- LAYOUT ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("SentimentPulse",
                            className="text-center mb-4 text-info fw-bold"), width=12)),

    dcc.Interval(id='interval-component', interval=3000, n_intervals=0),

    dbc.Row([
        dbc.Col(html.Div([html.H6("Total Comments"), html.H2(id="total-comments-kpi")],
                         className="metric-card"), width=3),
        dbc.Col(html.Div([html.H6("Positive %"), html.H2(id="positive-pct-kpi", className="text-success")],
                         className="metric-card"), width=3),
        dbc.Col(html.Div([html.H6("Negative %"), html.H2(id="negative-pct-kpi", className="text-danger")],
                         className="metric-card"), width=3),
        dbc.Col(html.Div([html.H6("Neutral %"), html.H2(id="neutral-pct-kpi", className="text-warning")],
                         className="metric-card"), width=3)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='sentiment-pie-chart', config={'displayModeBar': False},
                          style={'backgroundColor':'#10171f'}), width=4),
        dbc.Col(dcc.Graph(id='sentiment-time-series', config={'displayModeBar': False},
                          style={'backgroundColor':'#10171f'}), width=8)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.Div([
           html.H5("Trending Words", className="text-info mb-2"),
            dcc.Graph(id='trending-words-bar', config={'displayModeBar': False}),
        ], className="section-card"), width=6),

        dbc.Col(html.Div([
            html.H5("Live Comment Feed", className="text-primary mb-3"),
            html.Div(id='live-comment-feed', style={"maxHeight":"500px","overflowY":"scroll"})
        ], className="section-card"), width=6)
    ])
], fluid=True)

# --- CALLBACK LOGIC (same as before) ---
@app.callback(
    [Output('total-comments-kpi','children'),
     Output('positive-pct-kpi','children'),
     Output('negative-pct-kpi','children'),
     Output('neutral-pct-kpi','children'),
     Output('sentiment-pie-chart','figure'),
     Output('sentiment-time-series','figure'),
     Output('trending-words-bar','figure'),
     Output('live-comment-feed','children')],
    [Input('interval-component','n_intervals')]
)
def update_dashboard(n):
    empty = go.Figure()
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        if df.empty: raise Exception("No data")
    except:
        msg = dbc.Alert("Waiting for data...", color="secondary")
        return "0","0%","0%","0%",empty,empty,empty,[],[],[msg]

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df = df.tail(MAX_DATA_POINTS)
    df['sentiment'] = df['comment'].apply(get_sentiment)

    total = len(df)
    counts = df['sentiment'].value_counts()
    pos, neg, neu = counts.get('Positive',0), counts.get('Negative',0), counts.get('Neutral',0)

    pie = px.pie(df, names='sentiment', hole=0.4, color='sentiment',
                 color_discrete_map={'Positive':'#00ff88','Negative':'#ff4c4c','Neutral':'#f1c40f'})
    pie.update_layout(template='plotly_dark', title='Sentiment Distribution')

    ts = df.groupby([pd.Grouper(key='timestamp', freq='15s'),'sentiment']).size().unstack(fill_value=0)
    time_fig = go.Figure()
    for s, c in {'Positive':'#00ff88','Negative':'#ff4c4c','Neutral':'#f1c40f'}.items():
        time_fig.add_trace(go.Scatter(x=ts.index, y=ts[s], name=s, line=dict(color=c, width=3), fill='tozeroy'))
    time_fig.update_layout(template='plotly_dark', title="Sentiment Over Time")

    trending = get_trending_words(df['comment'])
    tw_fig = px.bar(x=[w for w,_ in trending], y=[c for _,c in trending], title="Trending Words",
                    text_auto=True, color=[c for _,c in trending], color_continuous_scale='teal')
    tw_fig.update_layout(template='plotly_dark')

    feed = []
    for _, row in df.tail(10).iloc[::-1].iterrows():
        color = "success" if row['sentiment']=="Positive" else "danger" if row['sentiment']=="Negative" else "warning"
        feed.append(html.Div(f"{row['comment'][:250]}...", className="feed-box text-" + color))

    return f"{total:,}", f"{(pos/total)*100:.2f}%", f"{(neg/total)*100:.2f}%", f"{(neu/total)*100:.2f}%", pie, time_fig, tw_fig, feed

if __name__ == '__main__':
    app.run_server(debug=True)
