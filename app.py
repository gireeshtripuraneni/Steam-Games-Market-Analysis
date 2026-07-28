
# Steam Games Market Analysis Dashboard
# Data Visualization Final Project


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------
# Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="Steam Games Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------

st.markdown("""
<style>

.main {
    background-color:#F8FAFC;
}

.block-container{
    padding-top:1.5rem;
    padding-bottom:2rem;
}

h1,h2,h3{
    color:#1E3A8A;
}

[data-testid="stMetricValue"]{
    font-size:34px;
    color:#2563EB;
    font-weight:bold;
}

[data-testid="stMetricLabel"]{
    font-size:16px;
}

footer{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Load Dataset
# ------------------------------------------------------------

import gdown
import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    file_id = "17X7MhTvbqW3N6YeuATl0TOKxEYyOqwUm"
    output = "games.csv"

    if not os.path.exists(output):
        gdown.download(
            f"https://drive.google.com/uc?id={file_id}",
            output,
            quiet=False
        )

    return pd.read_csv(
        output,
        quotechar='"',
        engine="python"
    )

df = load_data()

# ------------------------------------------------------------
# Data Cleaning
# ------------------------------------------------------------

# Columns expected to be numeric
numeric_columns = [
    "Price",
    "User score",
    "Recommendations",
    "Positive",
    "Negative",
    "Peak CCU",
    "Required age",
    "Average playtime forever",
    "Average playtime two weeks",
    "Median playtime forever",
    "Median playtime two weeks",
    "Achievements",
    "Metacritic score"
]

for col in numeric_columns:
    if col in df.columns:

        # Convert to string
        df[col] = df[col].astype(str)

        # Remove commas
        df[col] = df[col].str.replace(",", "", regex=False)

        # Remove blanks
        df[col] = df[col].replace(["", "nan", "None"], pd.NA)

        # Convert to numeric
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Fill numeric NaNs
for col in numeric_columns:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# Remove duplicate AppIDs
if "AppID" in df.columns:
    df = df.drop_duplicates(subset="AppID")

# Convert release date
if "Release date" in df.columns:
    df["Release date"] = pd.to_datetime(
        df["Release date"],
        errors="coerce"
    )

    df["Release Year"] = df["Release date"].dt.year
    


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

st.title("🎮 Steam Games Market Analysis Dashboard")

st.markdown(
"""
Welcome to the interactive Steam Games dashboard.

This dashboard explores trends in game popularity,
pricing strategies, publishers, developers, genres,
and player engagement using the Steam Games Dataset.
"""
)

st.divider()

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------

st.sidebar.header("🎛️ Dashboard Controls")

st.sidebar.markdown(
"""
Use the filters below to explore different
segments of the Steam Games dataset.
"""
)

st.sidebar.divider()

# ------------------------------------------------------------
# Genre Filter
# ------------------------------------------------------------

genres = sorted(df["Genres"].dropna().unique())

selected_genre = st.sidebar.selectbox(
    "🎮 Select Genre",
    ["All"] + list(genres)
)

# ------------------------------------------------------------
# Publisher Filter
# ------------------------------------------------------------

publishers = sorted(df["Publishers"].dropna().unique())

selected_publisher = st.sidebar.selectbox(
    "🏢 Select Publisher",
    ["All"] + list(publishers)
)

# ------------------------------------------------------------
# Required Age Filter
# ------------------------------------------------------------

ages = sorted(df["Required age"].dropna().astype(int).unique())

selected_age = st.sidebar.selectbox(
    "🔞 Required Age",
    ["All"] + list(ages)
)

# ------------------------------------------------------------
# Price Range
# ------------------------------------------------------------

price_range = st.sidebar.slider(
    "💲 Price Range ($)",
    min_value=float(df["Price"].min()),
    max_value=float(df["Price"].max()),
    value=(
        float(df["Price"].min()),
        float(df["Price"].max())
    )
)

st.sidebar.divider()



# ------------------------------------------------------------
# Apply Filters
# ------------------------------------------------------------

filtered_df = df.copy(deep=True)

# Genre
if selected_genre != "All":
    filtered_df = filtered_df[
        filtered_df["Genres"] == selected_genre
    ]

# Publisher
if selected_publisher != "All":
    filtered_df = filtered_df[
        filtered_df["Publishers"] == selected_publisher
    ]

# Required Age
if selected_age != "All":
    filtered_df = filtered_df[
        filtered_df["Required age"] == selected_age
    ]

# Price
filtered_df = filtered_df[
    (filtered_df["Price"] >= price_range[0]) &
    (filtered_df["Price"] <= price_range[1])
]

st.sidebar.markdown("### 📈 Dataset Summary")

st.sidebar.write(f"Games Available: **{len(filtered_df):,}**")

st.sidebar.divider()

with st.expander("📂 Dataset Information"):

    st.write("Rows :", df.shape[0])

    st.write("Columns :", df.shape[1])
    
    st.write("### Dataset Preview")
    
    st.dataframe(
    df.head(),
    use_container_width=True)
    
st.subheader("📊 Key Performance Indicators")

col1,col2,col3,col4=st.columns(4)

with col1:

    st.metric(
        "🎮 Total Games",
        f"{len(filtered_df):,}"
    )

with col2:

    st.metric(
        "💲 Average Price",
        f"${filtered_df['Price'].mean():.2f}"
    )

with col3:

    st.metric(
        "⭐ Average User Score",
        f"{filtered_df['User score'].mean():.2f}"
    )

with col4:

    st.metric(
        "👍 Total Recommendations",
        f"{int(filtered_df['Recommendations'].sum()):,}"
    )

st.divider()

overview_tab,market_tab,performance_tab,insight_tab=st.tabs(

[
    "🏠 Overview",
    "📈 Market Analysis",
    "🎮 Game Performance",
    "📊 Insights"
]

)

with overview_tab:

    st.header("🏠 Overview")

    st.markdown(
        "This section provides an overview of the Steam Games dataset, highlighting the most popular games, genre distribution, and pricing trends."
    )

    # --------------------------------------------------------
    # Row 1
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    # ==========================
    # Top 10 Games
    # ==========================

    with col1:

        st.subheader("🏆 Top 10 Games by Positive Reviews")
        

        top_games = (
            filtered_df.nlargest(10, "Positive")
            [["AppID", "Positive"]]
        )

        fig = px.bar(
            top_games,
            x="Positive",
            y="AppID",
            labels={"AppID": "Game"},
            
            orientation="h",
            color="Positive",
            color_continuous_scale="Blues",
            title="Most Positively Reviewed Games"
        )

        fig.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            height=500,
            margin=dict(l=20, r=20, t=50, b=20)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # Genre Distribution
    # ==========================

    with col2:

        st.subheader("🎮 Genre Distribution")

        genre_counts = (
            filtered_df["Genres"]
            .value_counts()
            .head(15)
            .reset_index()
        )

        genre_counts.columns = ["Genre", "Count"]

        fig = px.treemap(
            genre_counts,
            path=["Genre"],
            values="Count",
            color="Count",
            color_continuous_scale="Viridis"
        )

        fig.update_layout(
            height=500,
            margin=dict(l=10, r=10, t=30, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # Row 2
    # --------------------------------------------------------

    col3, col4 = st.columns(2)

    # ==========================
    # Price Distribution
    # ==========================

    with col3:

        st.subheader("💵 Free vs Paid Games")

        payment_data = pd.DataFrame({
            "Type": ["Free", "Paid"],
            "Count": [
                (filtered_df["Price"] == 0).sum(),
                (filtered_df["Price"] > 0).sum()
            ]
  })

        fig = px.pie(
            payment_data,
            values="Count",
            names="Type",
            hole=0.6,
            color_discrete_sequence=["#2ECC71", "#3498DB"],
            title="Distribution of Free vs Paid Games"
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label"
        )

        fig.update_layout(height=450)

        st.plotly_chart(fig, use_container_width=True)

    # ==========================
    # User Score Distribution
    # ==========================

    with col4:

        top_genres = filtered_df["Genres"].value_counts().head(6).index

        box_df = filtered_df[
        filtered_df["Genres"].isin(top_genres)
        ]

        fig = px.box(
        box_df,
        x="Genres",
        y="Price",
        color="Genres",
        title="Price Distribution by Genre"
        )

        fig.update_layout(height=450)

        st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # Dataset Summary
    # --------------------------------------------------------

    st.subheader("📋 Overview Statistics")

    summary = pd.DataFrame({
    "Metric": [
        "Total Games",
        "Average Price",
        "Average User Score",
        "Average Recommendations",
        "Maximum Peak CCU"
    ],
    "Value": [
        f"{len(filtered_df):,}",
        f"${filtered_df['Price'].mean():.2f}",
        f"{filtered_df['User score'].mean():.2f}",
        f"{filtered_df['Recommendations'].mean():,.0f}",
        f"{filtered_df['Peak CCU'].max():,.0f}"
    ]
})

summary["Value"] = summary["Value"].astype(str)

st.dataframe(summary, use_container_width=True)


with market_tab:

    st.header("📈 Market Analysis")

    col1, col2 = st.columns(2)

    # ==========================================
    # Correlation Heatmap
    # ==========================================

    with col1:

        st.subheader("📊 Correlation Heatmap")

        corr_columns = [
            "Price",
            "User score",
            "Positive",
            "Negative",
            "Recommendations",
            "Peak CCU"
        ]

        corr = filtered_df[corr_columns].corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            title="Correlation Between Numerical Features"
        )

        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # Top Publishers
    # ==========================================

    with col2:

        publisher_counts = (
            filtered_df["Publishers"]
            .dropna()
            .str.split(",")
            .explode()
            .str.strip()
            .value_counts()
            .head(10)
            .reset_index()
        )

        publisher_counts.columns = ["Publisher", "Number of Games"]

        fig = px.bar(
            publisher_counts,
            x="Number of Games",
            y="Publisher",
            orientation="h",
            color="Number of Games",
            color_continuous_scale="Viridis",
            title="Top 10 Publishers"
        )

        fig.update_layout(
            height=500,
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

with performance_tab:

    st.header("🎮 Game Performance")

    st.markdown("""
    Analyze the performance of individual Steam games based on
    ratings, recommendations, popularity, and pricing.
    """)

    # -------------------------------------------------------
    # Row 1
    # -------------------------------------------------------

    col1, col2 = st.columns(2)

    # ==========================================
    # Top Rated Games
    # ==========================================

    with col1:

        st.subheader("⭐ Top Rated Games")

        top_rated = (
            filtered_df.nlargest(10, "User score")
            [["AppID", "User score"]]
        )

        fig = px.bar(
            top_rated,
            x="User score",
            y="AppID",
            orientation="h",
            color="User score",
            color_continuous_scale="Viridis",
            title="Top 10 Games by User Score"
        )

        fig.update_layout(
            height=450,
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # Most Recommended Games
    # ==========================================

    with col2:

        st.subheader("👍 Most Recommended Games")

        recommended = (
            filtered_df.nlargest(10, "Recommendations")
            [["AppID", "Recommendations"]]
        )

        fig = px.bar(
            recommended,
            x="Recommendations",
            y="AppID",
            orientation="h",
            color="Recommendations",
            color_continuous_scale="Blues",
            title="Top 10 Most Recommended Games"
        )

        fig.update_layout(
            height=450,
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------
    # Row 2
    # -------------------------------------------------------

    col3, col4 = st.columns(2)

    # ==========================================
    # Peak Concurrent Users
    # ==========================================

    with col3:

        st.subheader("🔥 Peak Concurrent Users")

        peak_games = (
            filtered_df.nlargest(10, "Peak CCU")
            [["AppID", "Peak CCU"]]
        )

        fig = px.bar(
            peak_games,
            x="Peak CCU",
            y="AppID",
            orientation="h",
            color="Peak CCU",
            color_continuous_scale="Oranges",
            title="Top Games by Peak Concurrent Users"
        )

        fig.update_layout(
            height=450,
            yaxis=dict(categoryorder="total ascending"),
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # Price vs User Score
    # ==========================================

    with col4:

        st.subheader("🎯 Price vs User Score")

        scatter_df = filtered_df[
            (filtered_df["User score"] > 0)
            & (filtered_df["Recommendations"] > 0)
        ]

        fig = px.scatter(
            scatter_df,
            x="Price",
            y="User score",
            size="Recommendations",
            hover_name="AppID",
            color="Recommendations",
            color_continuous_scale="Turbo",
            title="Price vs User Score"
        )

        fig.update_layout(height=450)

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------------------------------------
    # Full Width Chart
    # -------------------------------------------------------

    st.subheader("🏅 Top Games by Metacritic Score")

    metacritic = (
        filtered_df[filtered_df["Metacritic score"] > 0]
        .nlargest(10, "Metacritic score")
        [["AppID", "Metacritic score"]]
    )

    fig = px.bar(
        metacritic,
        x="Metacritic score",
        y="AppID",
        orientation="h",
        color="Metacritic score",
        color_continuous_scale="Greens",
        title="Top 10 Games by Metacritic Score"
    )

    fig.update_layout(
        height=500,
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

with insight_tab:

    st.header("📊 Insights & Conclusions")

    st.markdown("""
    This section summarizes the most important findings from the Steam Games dataset.
    """)

    # ==========================================================
    # KPI Metrics
    # ==========================================================

    total_games = len(filtered_df)

    avg_price = filtered_df["Price"].mean()

    avg_user_score = filtered_df["User score"].mean()

    avg_meta = filtered_df["Metacritic score"].replace(0, pd.NA).mean()

    highest_ccu = filtered_df["Peak CCU"].max()

    highest_recommendations = filtered_df["Recommendations"].max()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎮 Total Games", f"{total_games:,}")
        st.metric("💰 Average Price", f"${avg_price:.2f}")

    with col2:
        st.metric("⭐ Avg User Score", f"{avg_user_score:.1f}")
        st.metric("🏆 Avg Metacritic", f"{avg_meta:.1f}")

    with col3:
        st.metric("🔥 Highest Peak CCU", f"{highest_ccu:,}")
        st.metric("👍 Highest Recommendations", f"{highest_recommendations:,}")

    st.divider()

    # ==========================================================
    # Most Common Genre
    # ==========================================================

    st.subheader("🎮 Most Popular Genres")

    genre_counts = (
        filtered_df["Genres"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(10)
        .reset_index()
    )

    genre_counts.columns = ["Genre", "Games"]

    fig = px.bar(
        genre_counts,
        x="Games",
        y="Genre",
        orientation="h",
        color="Games",
        color_continuous_scale="Viridis",
        title="Top 10 Genres"
    )

    fig.update_layout(
        height=450,
        yaxis=dict(categoryorder="total ascending"),
        coloraxis_showscale=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==========================================================
    # Key Insights
    # ==========================================================

    st.subheader("📌 Key Insights")

    st.success(f"""
    • The dataset contains **{total_games:,}** Steam games.

    • The average game price is **${avg_price:.2f}**.

    • The average user score is **{avg_user_score:.1f}**.

    • The highest peak concurrent players recorded is **{highest_ccu:,}**.

    • Games with higher positive reviews generally receive more recommendations.

    • Windows is the dominant gaming platform across the dataset.

    • Action and Indie genres appear most frequently in the Steam marketplace.

    • User ratings and review counts are strong indicators of game popularity.
    """)

    st.info("""
    **Conclusion**

    Steam offers a diverse marketplace with thousands of games across multiple genres.
    Player engagement is strongly associated with positive reviews and recommendations,
    while pricing alone is not a strong predictor of a game's success. Overall, user
    satisfaction and community engagement play a much larger role in determining a game's
    popularity than its price.
    """)
    
st.divider()

st.caption(
"""
Steam Games Market Analysis Dashboard

Developed using Streamlit • Plotly • Pandas

Data Source: Steam Games Dataset (Kaggle)
"""
)

