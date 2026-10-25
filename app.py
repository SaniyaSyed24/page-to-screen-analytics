from pathlib import Path
import sqlite3

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "page_to_screen.db"

st.set_page_config(
    page_title="Page to Screen | Adaptation Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    :root {
      --ink: #f5f0e8;
      --muted: #b8b1a6;
      --panel: #171a20;
      --panel-2: #20242c;
      --line: rgba(255,255,255,.09);
      --accent: #d8a86e;
      --accent-2: #a9c5a0;
    }
    .stApp {
      background:
        radial-gradient(ellipse at 5% 0%, rgba(216,168,110,.09), transparent 32%),
        radial-gradient(ellipse at 100% 5%, rgba(169,197,160,.06), transparent 28%),
        #101217;
      color: var(--ink);
      font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stHeader"] { background: rgba(16,18,23,.85); }
    [data-testid="stSidebar"] {
      background: #15181e;
      border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif; }
    .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { letter-spacing: -.025em; }
    h1, .serif { font-family: 'Playfair Display', Georgia, serif !important; }
    .hero {
      padding: 1.7rem 1.9rem;
      border: 1px solid rgba(216,168,110,.23);
      border-radius: 24px;
      background: linear-gradient(115deg, rgba(216,168,110,.12), rgba(32,36,44,.88) 48%, rgba(169,197,160,.07));
      margin-bottom: 1.4rem;
      position: relative;
      overflow: hidden;
    }
    .eyebrow {
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: .17em;
      font-size: .72rem;
      font-weight: 700;
      margin-bottom: .55rem;
    }
    .hero h1 { font-size: clamp(2rem, 4vw, 3.25rem); line-height: 1.1; margin: 0; }
    .hero p { color: var(--muted); font-size: 1rem; max-width: 760px; margin: .8rem 0 0 0; }
    .hero-tag {
      display: inline-block;
      border: 1px solid rgba(216,168,110,.35);
      border-radius: 999px;
      color: #e6c79f;
      padding: .28rem .65rem;
      font-size: .76rem;
      margin-top: 1rem;
    }
    .section-label {
      color: var(--accent);
      text-transform: uppercase;
      font-size: .72rem;
      letter-spacing: .14em;
      font-weight: 700;
      margin: .5rem 0 .85rem;
    }
    .metric-card {
      background: linear-gradient(145deg, #1c2028, #171a20);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1.1rem 1.15rem 1rem;
      min-height: 126px;
      box-shadow: 0 12px 28px rgba(0,0,0,.12);
    }
    .metric-top { display:flex; align-items:center; gap:.55rem; color:var(--muted); font-size:.82rem; }
    .metric-icon { color:var(--accent); font-size:1rem; }
    .metric-value { color:var(--ink); font-size:2rem; line-height:1.2; font-weight:700; margin-top:.65rem; }
    .metric-note { color:#898f9b; font-size:.72rem; margin-top:.25rem; }
    .panel {
      background: rgba(23,26,32,.88);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1.1rem 1.2rem;
      height: 100%;
    }
    .panel h3 { margin-top:0; font-size:1.08rem; }
    .muted { color: var(--muted); font-size:.88rem; }
    .stButton button, .stDownloadButton button {
      border-radius: 10px;
      border: 1px solid rgba(216,168,110,.4);
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
      background: #1a1d24;
      border-color: var(--line);
      border-radius: 10px;
    }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
    hr { border-color: var(--line); }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

def query_df(conn, sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)

def metric_card(icon, label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-top"><span class="metric-icon">{icon}</span><span>{label}</span></div>
          <div class="metric-value">{value:,}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not DB_PATH.exists():
    st.markdown('<div class="hero"><div class="eyebrow">Reading stories across screens</div><h1>Page to Screen</h1><p>Create the SQLite database before opening the explorer.</p></div>', unsafe_allow_html=True)
    st.warning("Database not found. Run `python src/load_data.py` in your terminal, then refresh.")
    st.stop()

with sqlite3.connect(DB_PATH) as conn:
    books_count = int(query_df(conn, "SELECT COUNT(*) n FROM books")["n"][0])
    shows_count = int(query_df(conn, "SELECT COUNT(*) n FROM tv_shows")["n"][0])
    adaptations_count = int(query_df(conn, "SELECT COUNT(*) n FROM adaptations")["n"][0])
    platforms_count = int(query_df(conn, "SELECT COUNT(*) n FROM platforms")["n"][0])

    genres = query_df(conn, """
        SELECT COALESCE(NULLIF(TRIM(b.genre), ''), 'Unknown') genre,
               COUNT(DISTINCT a.adaptation_id) adaptations
        FROM adaptations a JOIN books b ON b.book_id = a.book_id
        GROUP BY COALESCE(NULLIF(TRIM(b.genre), ''), 'Unknown')
        ORDER BY adaptations DESC, genre
    """)
    years = query_df(conn, """
        SELECT s.first_release_year release_year,
               COUNT(DISTINCT a.adaptation_id) adaptations
        FROM adaptations a JOIN tv_shows s ON s.show_id = a.show_id
        WHERE s.first_release_year IS NOT NULL
        GROUP BY s.first_release_year ORDER BY s.first_release_year
    """)
    platforms_df = query_df(conn, """
        SELECT p.platform_name platform,
               COUNT(DISTINCT a.adaptation_id) adaptations
        FROM platforms p
        JOIN show_platforms sp ON sp.platform_id = p.platform_id
        JOIN tv_shows s ON s.show_id = sp.show_id
        JOIN adaptations a ON a.show_id = s.show_id
        GROUP BY p.platform_name ORDER BY adaptations DESC, platform
    """)
    detail = query_df(conn, """
        SELECT b.title AS book_title, b.author, b.publication_year, b.genre,
               s.title AS tv_title, s.first_release_year, s.end_year, s.episode_count,
               GROUP_CONCAT(DISTINCT p.platform_name) AS platform,
               b.book_source_url, s.tv_source_url, a.relationship_source_url
        FROM adaptations a
        JOIN books b ON b.book_id = a.book_id
        JOIN tv_shows s ON s.show_id = a.show_id
        LEFT JOIN show_platforms sp ON sp.show_id = s.show_id
        LEFT JOIN platforms p ON p.platform_id = sp.platform_id
        GROUP BY a.adaptation_id
        ORDER BY s.first_release_year DESC, s.title
    """)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Reading stories across screens</div>
      <h1>Page to Screen <span style="color:#d8a86e">↗</span></h1>
      <p>A research explorer for the books behind television stories. Discover source novels,
      adaptation timelines, genres and platform distribution in one place.</p>
      <span class="hero-tag">BOOKS · TELEVISION · ADAPTATION DATA</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Collection overview</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4, gap="medium")
with m1: metric_card("▤", "Books", books_count, "Source titles in the database")
with m2: metric_card("▣", "TV shows", shows_count, "Series linked to source books")
with m3: metric_card("↗", "Adaptation links", adaptations_count, "Book-to-screen relationships")
with m4: metric_card("◉", "Platforms", platforms_count, "Platform names represented")

st.markdown("")
with st.sidebar:
    st.markdown("## 📚 Page to Screen")
    st.caption("Adaptation intelligence")
    st.divider()
    st.markdown("### Find an adaptation")
    search = st.text_input("Search titles or authors", placeholder="e.g. The Witcher")
    genre_options = sorted([g for g in detail["genre"].dropna().unique().tolist() if str(g).strip()])
    selected_genres = st.multiselect("Book genre", genre_options, placeholder="All genres")
    platform_options = sorted(
        {v.strip() for cell in detail["platform"].dropna().astype(str) for v in cell.split(",") if v.strip()}
    )
    selected_platforms = st.multiselect("Platform", platform_options, placeholder="All platforms")
    if not years.empty:
        min_year = int(years["release_year"].min())
        max_year = int(years["release_year"].max())
        year_range = st.slider("TV first-release year", min_year, max_year, (min_year, max_year))
    else:
        year_range = (1900, 2100)
    st.divider()
    st.caption("Counts and charts are computed from the local SQLite database. Source links should be reviewed before drawing conclusions.")

filtered = detail.copy()
if search.strip():
    needle = search.strip().casefold()
    mask = (
        filtered["book_title"].fillna("").str.casefold().str.contains(needle, regex=False)
        | filtered["tv_title"].fillna("").str.casefold().str.contains(needle, regex=False)
        | filtered["author"].fillna("").str.casefold().str.contains(needle, regex=False)
    )
    filtered = filtered[mask]
if selected_genres:
    filtered = filtered[filtered["genre"].isin(selected_genres)]
if selected_platforms:
    filtered = filtered[
        filtered["platform"].fillna("").apply(
            lambda cell: any(p in [x.strip() for x in cell.split(",")] for p in selected_platforms)
        )
    ]
if not filtered.empty:
    filtered = filtered[
        filtered["first_release_year"].isna()
        | filtered["first_release_year"].between(year_range[0], year_range[1])
    ]

    
# Adaptation timeline statistics for the current selection
gap_data = filtered.copy()

gap_data["publication_year"] = pd.to_numeric(
    gap_data["publication_year"], errors="coerce"
)
gap_data["first_release_year"] = pd.to_numeric(
    gap_data["first_release_year"], errors="coerce"
)

gap_data = gap_data.dropna(
    subset=["publication_year", "first_release_year"]
).copy()

gap_data["years_to_adaptation"] = (
    gap_data["first_release_year"] - gap_data["publication_year"]
)

st.markdown(
    '<div class="section-label">Adaptation timeline insights</div>',
    unsafe_allow_html=True,
)

if gap_data.empty:
    st.info("No complete publication and TV release years in this selection.")
else:
    average_gap = round(gap_data["years_to_adaptation"].mean(), 1)
    shortest_gap = int(gap_data["years_to_adaptation"].min())
    longest_gap = int(gap_data["years_to_adaptation"].max())
    long_gaps = int(
        (gap_data["years_to_adaptation"] > 100).sum()
    )

    g1, g2, g3, g4 = st.columns(4, gap="medium")

    with g1:
        metric_card(
            "◷", "Average time gap", average_gap,
            "Years from publication to TV debut"
        )

    with g2:
        metric_card(
            "↘", "Shortest time gap", shortest_gap,
            "Years in the current selection"
        )

    with g3:
        metric_card(
            "↗", "Longest time gap", longest_gap,
            "Years in the current selection"
        )

    with g4:
        metric_card(
            "!", "Gaps over 100 years", long_gaps,
            "Records to review, not confirmed errors"
        )

    st.caption(
        "Statistics use the years recorded in the database. "
        "They are descriptive, not independently verified historical facts."
    )


# Charts use the same filtered adaptation rows as the explorer.
st.markdown('<div class="section-label">Explore the collection</div>', unsafe_allow_html=True)
if filtered.empty:
    st.info("No records match those filters. Try clearing one or more filters.")
else:
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown('<div class="panel"><h3>Adaptations by genre</h3><div class="muted">Count of linked adaptations in the current selection</div></div>', unsafe_allow_html=True)
        genre_filtered = (
            filtered.assign(genre=filtered["genre"].fillna("Unknown").replace("", "Unknown"))
            .groupby("genre", as_index=False)["tv_title"].nunique()
            .rename(columns={"tv_title": "Adaptations"})
            .sort_values("Adaptations", ascending=False)
            .set_index("genre")
        )
        st.bar_chart(genre_filtered, color="#d8a86e", height=300)
    with right:
        st.markdown('<div class="panel"><h3>First TV release by year</h3><div class="muted">How the selected adaptations are distributed over time</div></div>', unsafe_allow_html=True)
        timeline = (
            filtered.dropna(subset=["first_release_year"])
            .groupby("first_release_year", as_index=False)["tv_title"].nunique()
            .rename(columns={"first_release_year": "Year", "tv_title": "Adaptations"})
            .set_index("Year")
        )
        if timeline.empty:
            st.caption("No release-year values available for the current selection.")
        else:
            st.bar_chart(timeline, color="#a9c5a0", height=300)

    if not platforms_df.empty:
        st.markdown('<div class="section-label">Platform landscape</div>', unsafe_allow_html=True)
        platform_filtered = (
            filtered.dropna(subset=["platform"])
            .assign(platform=filtered["platform"].fillna("").str.split(","))
            .explode("platform")
        )
        platform_filtered["platform"] = platform_filtered["platform"].str.strip()
        platform_filtered = platform_filtered[platform_filtered["platform"] != ""]
        platform_chart = (
            platform_filtered.groupby("platform", as_index=False)["tv_title"].nunique()
            .rename(columns={"tv_title": "Adaptations"})
            .sort_values("Adaptations", ascending=False)
            .head(12)
            .set_index("platform")
        )
        if not platform_chart.empty:
            st.bar_chart(platform_chart, color="#9aaee8", height=260)

st.markdown('<div class="section-label">Adaptation explorer</div>', unsafe_allow_html=True)
st.markdown("Search, filter, and inspect the source details behind each relationship.")
if filtered.empty:
    st.info("The explorer is empty because no records match the current filters.")
else:
    display = filtered[
        ["book_title", "author", "publication_year", "genre", "tv_title",
         "first_release_year", "end_year", "episode_count", "platform"]
    ].rename(columns={
        "book_title": "Book",
        "author": "Author",
        "publication_year": "Published",
        "genre": "Genre",
        "tv_title": "TV adaptation",
        "first_release_year": "TV debut",
        "end_year": "Final year",
        "episode_count": "Episodes",
        "platform": "Platform(s)",
    })
    st.dataframe(display, width="stretch", hide_index=True, height=390)

    st.markdown("#### Source links")
    choice_options = {
        f"{row.book_title} → {row.tv_title}": idx
        for idx, row in filtered.reset_index(drop=True).iterrows()
    }
    chosen = st.selectbox("Choose an adaptation to inspect sources", list(choice_options.keys()))
    selected_row = filtered.reset_index(drop=True).iloc[choice_options[chosen]]
    link1, link2, link3 = st.columns(3)
    with link1:
        st.markdown(f"[Book source ↗]({selected_row['book_source_url']})")
    with link2:
        st.markdown(f"[TV show source ↗]({selected_row['tv_source_url']})")
    with link3:
        st.markdown(f"[Adaptation relationship source ↗]({selected_row['relationship_source_url']})")

    export = filtered.drop(columns=[], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export filtered records as CSV",
        data=export,
        file_name="page_to_screen_filtered.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Page to Screen · Portfolio project · Metrics reflect the records currently loaded. "
    "A populated source URL is not, by itself, proof that the linked page validates every field."
)
