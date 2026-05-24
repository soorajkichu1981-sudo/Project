import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
from io import BytesIO

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify Analytics 2023",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Styles ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --gold:      #C9A84C;
    --gold-light:#E8CC80;
    --cream:     #F5EDD6;
    --obsidian:  #0D0D0D;
    --charcoal:  #161616;
    --card:      #1C1C1C;
    --border:    #2A2A2A;
    --text-muted:#888888;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--obsidian) !important;
    color: var(--cream) !important;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stHeader"] { background: var(--obsidian) !important; }
[data-testid="stSidebar"] {
    background: var(--charcoal) !important;
    border-right: 1px solid var(--border);
}

/* ── Sidebar nav buttons ── */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--cream);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 0.08em;
    padding: 0.65rem 1.2rem;
    margin-bottom: 0.4rem;
    border-radius: 4px;
    transition: all 0.25s;
    text-align: left;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--gold);
    border-color: var(--gold);
    color: var(--obsidian);
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--gold) !important;
    border-radius: 6px !important;
    padding: 1.2rem !important;
}
[data-testid="metric-container"] label { color: var(--text-muted) !important; font-size: 0.75rem !important; letter-spacing: 0.1em !important; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: var(--gold-light) !important; font-family: 'Playfair Display', serif !important; font-size: 1.8rem !important; }

/* ── Section headers ── */
.luxury-heading {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: 0.02em;
    margin-bottom: 0.2rem;
}
.luxury-subheading {
    font-size: 0.8rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1.2rem;
}

/* ── Gold divider ── */
.gold-divider {
    border: none;
    border-top: 1px solid var(--gold);
    margin: 2rem 0;
    opacity: 0.35;
}

/* ── Hero (home) ── */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.8rem;
    font-weight: 900;
    line-height: 1.1;
    color: var(--cream);
}
.hero-accent { color: var(--gold); }
.hero-subtitle {
    font-size: 1rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.5rem;
}
.hero-body {
    font-size: 1.05rem;
    color: #B0A898;
    line-height: 1.8;
    max-width: 560px;
    margin-top: 1.4rem;
}
.pill {
    display: inline-block;
    background: var(--card);
    border: 1px solid var(--gold);
    color: var(--gold-light);
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    margin-right: 0.5rem;
    margin-top: 1.2rem;
}

/* ── About cards ── */
.about-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.8rem;
    margin-bottom: 1rem;
}
.about-card h3 {
    font-family: 'Playfair Display', serif;
    color: var(--gold-light);
    margin-bottom: 0.5rem;
}
.about-card p { color: #B0A898; line-height: 1.7; font-size: 0.95rem; }

/* ── Chart wrapper ── */
.chart-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 1px dashed var(--gold) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Matplotlib theme ────────────────────────────────────────────────────────────
OBSIDIAN   = "#0D0D0D"
CARD       = "#1C1C1C"
GOLD       = "#C9A84C"
GOLD_LIGHT = "#E8CC80"
CREAM      = "#F5EDD6"
MUTED      = "#888888"
PALETTE    = ["#C9A84C","#E8CC80","#A07830","#8B6914","#F5C842","#6B4F10","#D4A853","#FFD87A","#7A5A28","#B8952A"]

def apply_chart_style(fig, ax):
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.title.set_color(CREAM)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2A2A2A")
    ax.grid(axis='y', color='#2A2A2A', linewidth=0.6)
    ax.grid(axis='x', visible=False)

# ─── Session state ───────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 2rem 0;'>
        <div style='font-size:2.5rem;'>🎵</div>
        <div style='font-family:"Playfair Display",serif; font-size:1.2rem; color:#C9A84C; margin-top:0.4rem;'>Spotify Analytics</div>
        <div style='font-size:0.7rem; letter-spacing:0.2em; color:#555; text-transform:uppercase; margin-top:0.2rem;'>2023 Edition</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠  Home"):
        st.session_state.page = "Home"
    if st.button("📊  Dashboard"):
        st.session_state.page = "Dashboard"
    if st.button("ℹ️  About"):
        st.session_state.page = "About"

    st.markdown("<hr style='border-color:#2A2A2A; margin:2rem 0 1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.7rem; color:#444; text-align:center; letter-spacing:0.1em;'>UPLOAD YOUR DATA</p>", unsafe_allow_html=True)
    uploaded = st.file_uploader("spotify-2023.csv", type=["csv"], label_visibility="collapsed")
    st.markdown("<p style='font-size:0.68rem; color:#555; text-align:center; margin-top:0.5rem;'>Upload the Spotify 2023 dataset<br>to power all visualisations</p>", unsafe_allow_html=True)

# ─── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, encoding='latin-1')
    df['release_date'] = pd.to_datetime(
        df['released_year'].astype(str) + '-' +
        df['released_month'].astype(str) + '-' +
        df['released_day'].astype(str),
        errors='coerce'
    )
    df.drop(columns=['released_year','released_month','released_day'], inplace=True, errors='ignore')
    df.drop(columns=['bpm','key','mode'], inplace=True, errors='ignore')

    if 574 in df.index:
        df = df.drop([574])
    df['streams'] = pd.to_numeric(df['streams'], errors='coerce')
    df = df.sort_values('streams', ascending=False)
    df = df.drop_duplicates(subset='track_name', keep='first')
    df.drop(columns=['in_shazam_charts'], inplace=True, errors='ignore')

    if 'in_deezer_playlists' in df.columns:
        df['in_deezer_playlists'] = pd.to_numeric(
            df['in_deezer_playlists'].astype(str).str.replace(',',''), errors='coerce'
        )
    return df

df = None
if uploaded:
    df = load_data(uploaded)

# ══════════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Home":
    col_hero, col_img = st.columns([3, 2], gap="large")
    with col_hero:
        st.markdown("""
        <div class='hero-subtitle'>Data Intelligence Platform</div>
        <div class='hero-title'>Spotify <span class='hero-accent'>2023</span><br>Analytics</div>
        <div class='hero-body'>
            Uncover the sonic patterns behind the world's most-streamed music.
            From chart-topping collaborations to audio feature correlations —
            every insight rendered with precision.
        </div>
        <span class='pill'>🎧 953 Tracks</span>
        <span class='pill'>📅 2023 Data</span>
        <span class='pill'>🔬 7 Audio Features</span>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("→  Open Dashboard", key="go_dash"):
            st.session_state.page = "Dashboard"
            st.rerun()

    with col_img:
        # Decorative feature preview chart
        fig, ax = plt.subplots(figsize=(5, 4))
        apply_chart_style(fig, ax)
        labels  = ['Dance', 'Energy', 'Valence', 'Acoustic', 'Speech']
        values  = [66, 64, 51, 27, 11]
        bars    = ax.barh(labels, values, color=[GOLD, GOLD_LIGHT, "#A07830", "#8B6914", "#6B4F10"], height=0.55)
        ax.set_xlim(0, 100)
        ax.set_title("Avg Audio Profile", fontsize=11, pad=10)
        for bar, val in zip(bars, values):
            ax.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                    f"{val}%", va='center', color=CREAM, fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # Feature highlights
    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "📈", "Stream Rankings", "Explore the top 10 most-streamed songs and see what catapulted them to the summit."),
        (c2, "🎤", "Artist Impact",   "Find out which artists dominated 2023 with the most charting hits."),
        (c3, "🔗", "Feature Science", "Correlation heatmaps and regression plots reveal what audio traits drive streams."),
    ]:
        with col:
            st.markdown(f"""
            <div class='about-card' style='text-align:center;'>
                <div style='font-size:2rem; margin-bottom:0.6rem;'>{icon}</div>
                <h3 style='font-size:1rem;'>{title}</h3>
                <p style='font-size:0.88rem;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Dashboard":
    if df is None:
        st.markdown("""
        <div style='text-align:center; padding:5rem 2rem;'>
            <div style='font-size:3rem;'>📂</div>
            <div style='font-family:"Playfair Display",serif; font-size:1.8rem; color:#C9A84C; margin:1rem 0;'>No Data Loaded</div>
            <p style='color:#888;'>Upload <strong style='color:#C9A84C;'>spotify-2023.csv</strong> via the sidebar to begin exploring.</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # ── KPI row ──────────────────────────────────────────────────────────────────
    st.markdown("<div class='luxury-subheading'>Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>2023 at a Glance</div>", unsafe_allow_html=True)
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Tracks",      f"{len(df):,}")
    k2.metric("Total Streams",     f"{df['streams'].sum()/1e9:.2f}B")
    k3.metric("Unique Artists",    f"{df['artist(s)_name'].nunique():,}")
    k4.metric("Avg Danceability",  f"{df['danceability_%'].mean():.0f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Artists ──────────────────────────────────────────────────────────────
    st.markdown("<div class='luxury-subheading'>Artist Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>Top 10 Artists by Hits</div>", unsafe_allow_html=True)

    artist_counts = df['artist(s)_name'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(12, 5))
    apply_chart_style(fig, ax)
    bars = ax.bar(artist_counts.index, artist_counts.values,
                  color=PALETTE[:len(artist_counts)], width=0.6, edgecolor='none')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(int(bar.get_height())), ha='center', va='bottom', color=CREAM, fontsize=9)
    ax.set_title("Top 10 Artists — Number of Chart Hits in 2023", fontsize=12, pad=12)
    ax.set_xlabel("Artist", labelpad=8)
    ax.set_ylabel("Number of Hits", labelpad=8)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # ── Top Songs & Artist Count ─────────────────────────────────────────────────
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("<div class='luxury-subheading'>Stream Royalty</div>", unsafe_allow_html=True)
        st.markdown("<div class='luxury-heading'>Top 10 Songs</div>", unsafe_allow_html=True)
        top10 = df.head(10)
        fig, ax = plt.subplots(figsize=(7, 5))
        apply_chart_style(fig, ax)
        ax.barh(top10['track_name'][::-1], top10['streams'][::-1]/1e6,
                color=GOLD, edgecolor='none', height=0.6)
        ax.set_xlabel("Streams (Millions)", labelpad=8)
        ax.set_title("Most Streamed Songs — 2023", fontsize=11, pad=10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown("<div class='luxury-subheading'>Collaboration Effect</div>", unsafe_allow_html=True)
        st.markdown("<div class='luxury-heading'>Artists per Track vs Streams</div>", unsafe_allow_html=True)
        collab = df.groupby('artist_count')['streams'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(7, 5))
        apply_chart_style(fig, ax)
        ax.bar(collab['artist_count'].astype(str), collab['streams']/1e6,
               color=PALETTE[:len(collab)], edgecolor='none', width=0.55)
        ax.set_xlabel("Number of Artists", labelpad=8)
        ax.set_ylabel("Avg Streams (Millions)", labelpad=8)
        ax.set_title("Avg Streams by Collaboration Size", fontsize=11, pad=10)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # ── Regression Plots ─────────────────────────────────────────────────────────
    st.markdown("<div class='luxury-subheading'>Platform Reach</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>Streams vs Playlist Inclusion</div>", unsafe_allow_html=True)

    col_c, col_d = st.columns(2, gap="large")
    for col, y_col, label, color in [
        (col_c, 'in_spotify_playlists', 'Spotify Playlists', GOLD),
        (col_d, 'in_deezer_playlists',  'Deezer Playlists',  GOLD_LIGHT),
    ]:
        with col:
            fig, ax = plt.subplots(figsize=(7, 5))
            apply_chart_style(fig, ax)
            sub = df[['streams', y_col]].dropna()
            ax.scatter(sub['streams']/1e6, sub[y_col], color=color,
                       alpha=0.35, s=18, edgecolors='none')
            m, b = np.polyfit(sub['streams']/1e6, sub[y_col], 1)
            xs = np.linspace(sub['streams'].min()/1e6, sub['streams'].max()/1e6, 200)
            ax.plot(xs, m*xs + b, color=CREAM, linewidth=1.8, linestyle='--')
            ax.set_xlabel("Streams (Millions)", labelpad=8)
            ax.set_ylabel(label, labelpad=8)
            ax.set_title(f"Streams vs {label}", fontsize=11, pad=10)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # ── Correlation Heatmap ───────────────────────────────────────────────────────
    st.markdown("<div class='luxury-subheading'>Audio DNA</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>Feature Correlation Heatmap</div>", unsafe_allow_html=True)

    features = ['danceability_%','valence_%','energy_%','acousticness_%',
                'instrumentalness_%','liveness_%','speechiness_%']
    corr = df[features].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    apply_chart_style(fig, ax)
    cmap = sns.diverging_palette(20, 45, s=80, l=40, as_cmap=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='RdYlGn',
                vmin=-1, vmax=1, ax=ax,
                annot_kws={"size": 9, "color": CREAM},
                linewidths=0.5, linecolor='#2A2A2A',
                cbar_kws={"shrink": 0.8})
    ax.set_title("Correlation Between Audio Features", fontsize=12, pad=14)
    ax.tick_params(axis='x', rotation=35)
    ax.tick_params(axis='y', rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    # ── Release Timeline ──────────────────────────────────────────────────────────
    st.markdown("<div class='luxury-subheading'>Release Patterns</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>Monthly Stream Volume</div>", unsafe_allow_html=True)

    df['month'] = pd.to_datetime(df['release_date']).dt.month
    monthly = df.groupby('month')['streams'].sum().reset_index()
    month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly['month_name'] = monthly['month'].apply(lambda x: month_names[x-1] if 1<=x<=12 else str(x))

    fig, ax = plt.subplots(figsize=(12, 4))
    apply_chart_style(fig, ax)
    ax.fill_between(range(len(monthly)), monthly['streams']/1e9, alpha=0.25, color=GOLD)
    ax.plot(range(len(monthly)), monthly['streams']/1e9,
            color=GOLD, linewidth=2.5, marker='o', markersize=6, markerfacecolor=CREAM)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels(monthly['month_name'])
    ax.set_ylabel("Total Streams (Billions)", labelpad=8)
    ax.set_title("Cumulative Streams by Release Month", fontsize=11, pad=10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


elif st.session_state.page == "About":
    st.markdown("<div class='luxury-subheading'>About This Project</div>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-heading'>Spotify Analytics Platform</div>", unsafe_allow_html=True)
    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown("""
        <div class='about-card'>
            <h3>Project Overview</h3>
            <p>
                This analytics platform transforms raw Spotify chart data from 2023 into
                a refined suite of visual insights. Built with Streamlit, Pandas, Seaborn, and
                Matplotlib, it reveals patterns in streaming behaviour, artist prominence,
                platform reach, and audio characteristics that define modern hit music.
            </p>
        </div>
        <div class='about-card'>
            <h3>Dataset</h3>
            <p>
                The dataset encompasses the most-streamed songs on Spotify in 2023 —
                roughly 950+ tracks — with attributes spanning stream counts, playlist
                inclusions across Spotify, Apple Music, and Deezer, and seven normalised
                audio features including danceability, valence, energy, acousticness,
                instrumentalness, liveness, and speechiness.
            </p>
        </div>
        <div class='about-card'>
            <h3>Methodology</h3>
            <p>
                Raw data is cleaned by removing duplicates, fixing numeric types,
                constructing a unified release date column, and dropping sparse fields.
                All charts are rendered using a custom dark luxury theme for visual
                consistency and readability.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='about-card'>
            <h3>Tech Stack</h3>
            <p>🐍 Python 3.11</p>
            <p>📊 Streamlit</p>
            <p>🐼 Pandas</p>
            <p>🎨 Matplotlib</p>
            <p>🌊 Seaborn</p>
            <p>🔢 NumPy</p>
        </div>
        <div class='about-card'>
            <h3>Visualisations</h3>
            <p>📌 Top 10 Artists</p>
            <p>🎵 Top 10 Songs</p>
            <p>🤝 Collaboration Effect</p>
            <p>🔗 Playlist Regressions</p>
            <p>🌡️ Feature Heatmap</p>
            <p>📅 Release Timeline</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='gold-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding:1rem 0 3rem;'>
        <div style='font-family:"Playfair Display",serif; font-size:1rem; color:#555;'>
            Crafted with precision · Data tells a story
        </div>
        <div style='font-size:0.75rem; color:#333; margin-top:0.5rem; letter-spacing:0.1em;'>
            SPOTIFY ANALYTICS 2023 · BUILT WITH STREAMLIT
        </div>
    </div>
    """, unsafe_allow_html=True)