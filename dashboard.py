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

# --- NLTK Setup ---
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

# Extend stopwords with additional filler, pronouns, and auxiliaries
EXTRA_STOPWORDS = set([
    'he','she','it','they','we','i','you','me','my','your','his','her','their',
    'is','are','was','were','be','been','am','do','does','did','have','has','had',
    'will','shall','would','should','can','could','may','might','must',
    'the','a','an','in','on','at','of','for','with','about','as','to','from',
    'this','that','these','those','and','but','or','if','then','so','because','just','like','also'
])
STOPWORDS.update(EXTRA_STOPWORDS)

# --- CONFIG ---
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LITERA],
    title="Reddit Sentiment AI Dashboard",
    update_title="Updating...",
    index_string='''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            <link rel="icon" type="image/png" sizes="16x16" href="/assets/16x16.png">
            <link rel="icon" type="image/png" sizes="32x32" href="/assets/32x32.png">
            <link rel="icon" type="image/png" sizes="96x96" href="/assets/96x96.png">
            {%favicon%}
            {%css%}
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
)

analyzer = SentimentIntensityAnalyzer()
MAX_DATA_POINTS = 1000
CSV_FILE_PATH = 'live_reddit_comments.csv'

# --- SENTIMENT ANALYSIS ---
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

# --- TRENDING & UNIQUE WORDS ---
def get_trending_words(comments, top_n=10):
    words = []
    for comment in comments:
        comment_words = re.findall(r'\b\w+\b', comment.lower())
        words.extend([w for w in comment_words if w not in STOPWORDS])
    counter = Counter(words)
    return counter.most_common(top_n)

def get_unique_words(new_comments, old_comments):
    new_words = set()
    for comment in new_comments:
        new_words.update(re.findall(r'\b\w+\b', comment.lower()))
    old_words = set()
    for comment in old_comments:
        old_words.update(re.findall(r'\b\w+\b', comment.lower()))
    unique = new_words - old_words
    return list(unique)[:20]

# --- APP LAYOUT ---
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Reddit Sentiment AI Dashboard", className="text-center mb-4",
                            style={"font-family":"Montserrat, sans-serif", "color":"#2C3E50"}), width=12)),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),

    # KPI Cards
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Total Comments"), html.H2(id="total-comments-kpi")]), color="light", outline=True), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Positive %"), html.H2(id="positive-pct-kpi")]), color="light", outline=True), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Negative %"), html.H2(id="negative-pct-kpi")]), color="light", outline=True), width=3),
        dbc.Col(dbc.Card(dbc.CardBody([html.H6("Neutral %"), html.H2(id="neutral-pct-kpi")]), color="light", outline=True), width=3)
    ], className="mb-4"),

    # Charts Row
    dbc.Row([
        dbc.Col(dcc.Graph(id='sentiment-pie-chart', config={'displayModeBar': False}), width=4),
        dbc.Col(dcc.Graph(id='sentiment-time-series', config={'displayModeBar': False}), width=8)
    ], className="mb-4"),

    # Trending, Unique, Top Comments
    dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Trending Words", style={"color":"#2980B9"}),
            dcc.Graph(id='trending-words-bar', config={'displayModeBar': False}),
            html.H5("Unique Words", style={"color":"#27AE60"}),
            html.Ul(id='unique-words-list', className="small"),
            html.H5("Top Comments", style={"color":"#8E44AD"}),
            html.Ul(id='top-comments-list', className="small")
        ]), color="light", outline=True, style={"border":"3px solid black"}), width=6),

        dbc.Col(dbc.Card(dbc.CardBody([
            html.H5("Live Comment Feed", style={"color":"#34495E"}),
            html.Div(id='live-comment-feed', style={"maxHeight":"400px","overflowY":"scroll"})
        ]), color="light", outline=True, style={"border":"3px solid black"}), width=6)
    ], className="mb-4")
], fluid=True, style={"backgroundColor":"#F8F9FA"})

# --- CALLBACK ---
@app.callback(
    [Output('total-comments-kpi','children'),
     Output('positive-pct-kpi','children'),
     Output('negative-pct-kpi','children'),
     Output('neutral-pct-kpi','children'),
     Output('sentiment-pie-chart','figure'),
     Output('sentiment-time-series','figure'),
     Output('trending-words-bar','figure'),
     Output('unique-words-list','children'),
     Output('top-comments-list','children'),
     Output('live-comment-feed','children')],
    [Input('interval-component','n_intervals')]
)
def update_dashboard(n):
    empty_fig = go.Figure()
    empty_feed = [dbc.Alert("Waiting for data...", color="info")]
    empty_return = "0","0.00%","0.00%","0.00%", empty_fig, empty_fig, empty_fig, [], [], empty_feed

    try:
        df = pd.read_csv(CSV_FILE_PATH)
        if df.empty or 'comment' not in df.columns or 'timestamp' not in df.columns:
            return empty_return
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
    except Exception as e:
        print("CSV read error:", e)
        return empty_return

    try:
        df_recent = df.tail(MAX_DATA_POINTS)
        df_recent['sentiment'] = df_recent['comment'].apply(get_sentiment)
        total_comments = len(df_recent)
        sentiment_counts = df_recent['sentiment'].value_counts()
        pos_pct = (sentiment_counts.get('Positive',0)/total_comments)*100
        neg_pct = (sentiment_counts.get('Negative',0)/total_comments)*100
        neu_pct = (sentiment_counts.get('Neutral',0)/total_comments)*100
        kpi_total = f"{total_comments:,}"
        kpi_pos = f"{pos_pct:.2f}%"
        kpi_neg = f"{neg_pct:.2f}%"
        kpi_neu = f"{neu_pct:.2f}%"

        # Pie Chart
        color_map = {'Positive':'#2ECC71','Negative':'#E74C3C','Neutral':'#F1C40F'}
        pie_fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.4,
            marker_colors=[color_map[l] for l in sentiment_counts.index]
        )])
        pie_fig.update_layout(title="Sentiment Distribution", template='plotly_white', showlegend=True)

        # Time Series
        df_ts = df_recent.set_index('timestamp')
        df_resampled = df_ts.groupby([pd.Grouper(freq='10s'),'sentiment']).size().unstack(fill_value=0)
        for s in ['Positive','Negative','Neutral']:
            if s not in df_resampled.columns:
                df_resampled[s] = 0
        time_fig = go.Figure()
        for s, color in color_map.items():
            time_fig.add_trace(go.Scatter(
                x=df_resampled.index,
                y=df_resampled[s],
                mode='lines+markers',
                name=s,
                line=dict(color=color, width=3),
                fill='tozeroy'
            ))
        time_fig.update_layout(title="Sentiment Over Time", template='plotly_white',
                               xaxis_title="Time", yaxis_title="Comment Count")

        # Trending Words (filtered)
        trending_words = get_trending_words(df_recent['comment'].tail(200)) or []
        if trending_words:
            words, counts = zip(*trending_words)
            trending_fig = px.bar(x=words, y=counts, text=counts, labels={'x':'Word','y':'Count'}, title='Trending Words')
            trending_fig.update_layout(template='plotly_white', title_font_color='#2980B9')
        else:
            trending_fig = empty_fig

        # Unique Words
        unique_words = get_unique_words(df_recent['comment'].tail(50), df_recent['comment'].tail(200).head(150)) or []
        unique_list_items = [html.Li(word) for word in unique_words]

        # Top Comments
        top_comments = df_recent.sort_values(by='timestamp', ascending=False).head(5)['comment'].tolist()
        top_comments_items = [html.Li(comment[:200]+"..." if len(comment)>200 else comment) for comment in top_comments]

        # Live Feed
        last_comments = df_recent.tail(10).iloc[::-1]
        feed_elements = []
        for _, row in last_comments.iterrows():
            color = "success" if row['sentiment']=="Positive" else "danger" if row['sentiment']=="Negative" else "warning"
            feed_elements.append(dbc.Alert(f"{row['comment'][:250]}...", color=color, dismissable=False, className="mb-1 small"))

        # Negative Spike Alert
        recent_resample = df_ts.groupby([pd.Grouper(freq='30s'),'sentiment']).size().unstack(fill_value=0)
        if 'Negative' in recent_resample.columns:
            recent_neg_pct = (recent_resample['Negative'].iloc[-1]/recent_resample.iloc[-1].sum())*100
            if recent_neg_pct>50:
                feed_elements.insert(0, dbc.Alert("⚠️ High Negative Sentiment Spike Detected!", color="danger", className="text-center"))

        return kpi_total,kpi_pos,kpi_neg,kpi_neu,pie_fig,time_fig,trending_fig,unique_list_items,top_comments_items,feed_elements

    except Exception as e:
        print("Callback processing error:", e)
        return empty_return

# --- RUN APP ---
if __name__ == '__main__':
    app.run(debug=True)

