import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

st.set_page_config(
    page_title="World Happiness | Animated Dashboard",
    page_icon="🌍",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/evanfrang/world_happiness/"
    "48136725441b2d5b8b7d7ee29aa41e7eb95db549/whs_years_updated.csv"
)
YEARS = [2015, 2016, 2017, 2018, 2019]

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 3rem;}
      .hero {
        padding: 1.25rem 1.4rem;
        border: 1px solid rgba(120,120,120,.18);
        border-radius: 18px;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, rgba(40,120,180,.10), rgba(120,70,180,.06));
      }
      .hero h1 {margin: 0 0 .35rem 0; font-size: 2rem;}
      .hero p {margin: 0; opacity: .78; max-width: 900px;}
      [data-testid="stMetric"] {
        border: 1px solid rgba(120,120,120,.18);
        border-radius: 14px;
        padding: .7rem .8rem;
      }
      .small-note {font-size: .9rem; opacity: .76;}
    </style>
    """,
    unsafe_allow_html=True,
)


def _first_numeric(frame: pd.DataFrame, candidates: list[str]) -> pd.Series:
    """Coalesce several year-specific source columns into one numeric series."""
    out = pd.Series(np.nan, index=frame.index, dtype="float64")
    for column in candidates:
        if column in frame.columns:
            out = out.fillna(pd.to_numeric(frame[column], errors="coerce"))
    return out


@st.cache_data(ttl=3600, show_spinner=False)
def load_happiness_data() -> pd.DataFrame:
    """Load a pinned public WHR mirror and normalize the 2015–2019 schemas."""
    raw = pd.read_csv(DATA_URL, low_memory=False)
    raw["Year"] = pd.to_numeric(raw["Year"], errors="coerce")
    raw = raw[raw["Year"].isin(YEARS)].copy()

    clean = pd.DataFrame(index=raw.index)
    clean["Country"] = raw["Country"].astype(str).str.strip()
    clean["Year"] = raw["Year"].astype(int)

    clean["Happiness_Score"] = _first_numeric(raw, ["Score", "Happiness Score"])
    clean["GDP_per_Capita"] = _first_numeric(
        raw,
        ["Economy (GDP per Capita)", "Economy..GDP.per.Capita.", "GDP per capita"],
    )
    clean["Social_Support"] = _first_numeric(raw, ["Family", "Social support"])
    clean["Life_Expectancy"] = _first_numeric(
        raw,
        ["Health (Life Expectancy)", "Health..Life.Expectancy.", "Healthy life expectancy"],
    )
    clean["Freedom"] = _first_numeric(raw, ["Freedom", "Freedom to make life choices"])
    clean["Corruption"] = _first_numeric(
        raw,
        ["Trust (Government Corruption)", "Trust..Government.Corruption.", "Perceptions of corruption"],
    )
    clean["Generosity"] = _first_numeric(raw, ["Generosity"])

    if "Region" in raw.columns:
        clean["Region"] = raw["Region"].replace("", np.nan)
    else:
        clean["Region"] = np.nan

    # Some later WHR files omit region. Reuse a country's known historical region
    # rather than silently dropping the country from regional views.
    region_lookup = (
        clean.dropna(subset=["Region"])
        .drop_duplicates("Country")
        .set_index("Country")["Region"]
        .to_dict()
    )
    clean["Region"] = clean.apply(
        lambda row: row["Region"] if pd.notna(row["Region"]) else region_lookup.get(row["Country"], "Other"),
        axis=1,
    )

    clean = clean.dropna(subset=["Country", "Happiness_Score"]).reset_index(drop=True)
    clean["Rank"] = clean.groupby("Year")["Happiness_Score"].rank(method="first", ascending=False).astype(int)
    return clean


try:
    df = load_happiness_data()
except Exception as exc:
    st.error("The dashboard could not load the pinned World Happiness dataset.")
    st.exception(exc)
    st.stop()

st.markdown(
    """
    <div class="hero">
      <h1>World Happiness Report — Animated Global Dashboard</h1>
      <p>
        Explore how happiness scores, country rankings and major explanatory factors changed from
        2015 to 2019. The dashboard loads the dataset automatically and opens directly into the analysis.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Explore")
    selected_year = st.slider("Snapshot year", min_value=min(YEARS), max_value=max(YEARS), value=max(YEARS), step=1)
    all_regions = sorted(df["Region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Regions", all_regions, default=all_regions)
    top_n = st.slider("Countries in ranking view", min_value=5, max_value=20, value=10, step=1)
    st.caption("Animated charts include their own ▶ Play control.")

filtered = df[df["Region"].isin(selected_regions)].copy()
year_df = filtered[filtered["Year"] == selected_year].sort_values("Happiness_Score", ascending=False)

if year_df.empty:
    st.warning("No countries match the current region filters.")
    st.stop()

leader = year_df.iloc[0]
avg_score = year_df["Happiness_Score"].mean()
median_score = year_df["Happiness_Score"].median()
score_spread = year_df["Happiness_Score"].max() - year_df["Happiness_Score"].min()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Countries", f"{len(year_df):,}")
m2.metric("Average score", f"{avg_score:.2f}")
m3.metric("Top country", leader["Country"], f"{leader['Happiness_Score']:.2f}")
m4.metric("Top-to-bottom spread", f"{score_spread:.2f}", f"Median {median_score:.2f}")

st.subheader("Global happiness over time")
map_df = filtered[["Country", "Year", "Happiness_Score", "Rank"]].dropna().copy()
map_fig = px.choropleth(
    map_df,
    locations="Country",
    locationmode="country names",
    color="Happiness_Score",
    hover_name="Country",
    hover_data={"Rank": True, "Year": False, "Happiness_Score": ":.2f"},
    animation_frame="Year",
    color_continuous_scale="Viridis",
    range_color=(2.5, 8.0),
    labels={"Happiness_Score": "Happiness score"},
)
map_fig.update_geos(showframe=False, showcoastlines=True, projection_type="natural earth")
map_fig.update_layout(
    height=560,
    margin=dict(l=0, r=0, t=20, b=0),
    coloraxis_colorbar_title="Score",
)
st.plotly_chart(map_fig, use_container_width=True)
st.caption("Use ▶ Play to watch country scores change from 2015 through 2019.")

left, right = st.columns([1.05, 0.95])

with left:
    st.subheader("Top-country ranking race")
    ranked = (
        filtered.sort_values(["Year", "Happiness_Score"], ascending=[True, False])
        .groupby("Year", group_keys=False)
        .head(top_n)
        .copy()
    )
    rank_fig = px.bar(
        ranked,
        x="Happiness_Score",
        y="Country",
        orientation="h",
        animation_frame="Year",
        animation_group="Country",
        color="Region",
        hover_data={"Rank": True, "Region": True, "Happiness_Score": ":.2f"},
        range_x=[max(0, ranked["Happiness_Score"].min() - 0.35), 8.1],
        labels={"Happiness_Score": "Happiness score"},
    )
    rank_fig.update_layout(height=520, yaxis={"categoryorder": "total ascending"}, legend_title_text="Region")
    st.plotly_chart(rank_fig, use_container_width=True)

with right:
    st.subheader(f"Regional averages — {selected_year}")
    region_snapshot = (
        year_df.groupby("Region", as_index=False)["Happiness_Score"]
        .mean()
        .sort_values("Happiness_Score", ascending=True)
    )
    region_fig = px.bar(
        region_snapshot,
        x="Happiness_Score",
        y="Region",
        orientation="h",
        text_auto=".2f",
        labels={"Happiness_Score": "Average happiness score"},
    )
    region_fig.update_layout(height=520, showlegend=False)
    st.plotly_chart(region_fig, use_container_width=True)

st.subheader("How key factors move with happiness")
factor = st.selectbox(
    "Factor",
    ["GDP_per_Capita", "Social_Support", "Life_Expectancy", "Freedom", "Generosity", "Corruption"],
    format_func=lambda x: x.replace("_", " "),
)

scatter_df = filtered.dropna(subset=[factor, "Happiness_Score"]).copy()
scatter_fig = px.scatter(
    scatter_df,
    x=factor,
    y="Happiness_Score",
    color="Region",
    hover_name="Country",
    animation_frame="Year",
    animation_group="Country",
    labels={
        factor: factor.replace("_", " "),
        "Happiness_Score": "Happiness score",
    },
)
scatter_fig.update_traces(marker=dict(size=10, opacity=0.72))
scatter_fig.update_layout(height=540)
st.plotly_chart(scatter_fig, use_container_width=True)
st.caption(
    "The scatterplot shows association, not causation. The WHR factor values should not be interpreted "
    "as isolated causal effects."
)

trend_col, factor_col = st.columns(2)

with trend_col:
    st.subheader("Regional trend")
    regional_trend = (
        filtered.groupby(["Year", "Region"], as_index=False)["Happiness_Score"].mean()
    )
    trend_fig = px.line(
        regional_trend,
        x="Year",
        y="Happiness_Score",
        color="Region",
        markers=True,
        labels={"Happiness_Score": "Average happiness score"},
    )
    trend_fig.update_xaxes(dtick=1)
    trend_fig.update_layout(height=430)
    st.plotly_chart(trend_fig, use_container_width=True)

with factor_col:
    st.subheader("Factor association")
    factor_columns = [
        "GDP_per_Capita",
        "Social_Support",
        "Life_Expectancy",
        "Freedom",
        "Generosity",
        "Corruption",
    ]
    corr = (
        df[["Happiness_Score"] + factor_columns]
        .corr(numeric_only=True)["Happiness_Score"]
        .drop("Happiness_Score")
        .sort_values()
        .reset_index()
    )
    corr.columns = ["Factor", "Correlation"]
    corr["Factor"] = corr["Factor"].str.replace("_", " ", regex=False)
    corr_fig = px.bar(
        corr,
        x="Correlation",
        y="Factor",
        orientation="h",
        text_auto=".2f",
        range_x=[-1, 1],
    )
    corr_fig.update_layout(height=430, showlegend=False)
    st.plotly_chart(corr_fig, use_container_width=True)

st.divider()
st.subheader("Holdout model: can earlier years explain 2019 scores?")

model_features = ["GDP_per_Capita", "Social_Support", "Life_Expectancy", "Freedom", "Corruption"]
model_df = df[["Year", "Country", "Happiness_Score"] + model_features].dropna().copy()
train_df = model_df[model_df["Year"] <= 2018]
test_df = model_df[model_df["Year"] == 2019]

model = LinearRegression()
model.fit(train_df[model_features], train_df["Happiness_Score"])
pred = model.predict(test_df[model_features])

r2 = r2_score(test_df["Happiness_Score"], pred)
rmse = np.sqrt(mean_squared_error(test_df["Happiness_Score"], pred))
mae = np.mean(np.abs(test_df["Happiness_Score"].to_numpy() - pred))

c1, c2, c3 = st.columns(3)
c1.metric("2019 holdout R²", f"{r2:.3f}")
c2.metric("2019 holdout RMSE", f"{rmse:.3f}")
c3.metric("2019 holdout MAE", f"{mae:.3f}")

prediction_df = pd.DataFrame(
    {
        "Country": test_df["Country"].to_numpy(),
        "Actual": test_df["Happiness_Score"].to_numpy(),
        "Predicted": pred,
    }
)
pred_fig = px.scatter(
    prediction_df,
    x="Actual",
    y="Predicted",
    hover_name="Country",
    labels={"Actual": "Actual 2019 score", "Predicted": "Predicted 2019 score"},
)
min_axis = min(prediction_df[["Actual", "Predicted"]].min())
max_axis = max(prediction_df[["Actual", "Predicted"]].max())
pred_fig.add_shape(
    type="line",
    x0=min_axis,
    y0=min_axis,
    x1=max_axis,
    y1=max_axis,
    line=dict(dash="dash"),
)
pred_fig.update_layout(height=500)
st.plotly_chart(pred_fig, use_container_width=True)

coef_df = pd.DataFrame(
    {
        "Factor": [name.replace("_", " ") for name in model_features],
        "Coefficient": model.coef_,
    }
).sort_values("Coefficient")
coef_fig = px.bar(
    coef_df,
    x="Coefficient",
    y="Factor",
    orientation="h",
    text_auto=".2f",
)
coef_fig.update_layout(height=390, showlegend=False)
st.plotly_chart(coef_fig, use_container_width=True)

st.markdown(
    """
    **How to read this model:** the regression is trained on 2015–2018 rows and evaluated on 2019,
    so the displayed error is genuinely out-of-time rather than an in-sample fit. Coefficients are
    descriptive associations within this feature set; they are not causal policy effects.
    """
)

with st.expander("Data and methodology notes"):
    st.markdown(
        """
        - **Coverage:** World Happiness Report country-level data, 2015–2019.
        - **Schema normalization:** WHR column names changed across annual files. The app coalesces
          equivalent GDP, social-support, health, freedom and corruption fields into a consistent schema.
        - **Region handling:** later files that omit region reuse the country's known region from earlier
          years when available.
        - **Modeling:** linear regression trains on 2015–2018 and tests on 2019.
        - **Interpretation:** correlations and coefficients are descriptive, not causal.
        """
    )

st.caption(
    "Source: World Happiness Report historical releases. The dashboard reads a pinned public mirror "
    "of the 2015–2019 files so the analysis is reproducible and does not require user uploads."
)
