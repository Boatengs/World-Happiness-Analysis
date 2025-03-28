#import necessary libraries for dashboard interactivity
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

st.set_page_config(page_title="World Happiness Dashboard", layout="wide")

st.markdown("""
    <style>
    body { background: linear-gradient(to bottom right, #f0f8ff, #ffffff); }
    .main { padding: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; padding: 10px; }
    .sidebar .sidebar-content { background-color: black; }
    header { background-color: #004080; padding: 20px; border-radius: 10px; color: white; text-align: center; }
    footer { background-color: #f8f9fa; padding: 12px; text-align: center; font-size: 0.9rem; color: #444; border-top: 1px solid #ccc; margin-top: 2rem; }
    </style>
    <header>
        <h1>World Happiness Report Dashboard</h1>
        <p>Analyze global happiness trends and uncover impactful insights</p>
    </header>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload the World Happiness CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Awesome! You have successfully uploaded a file.")

    continent_map = {
        "Africa": ["Nigeria", "Kenya", "South Africa", "Egypt", "Morocco"],
        "Asia": ["India", "China", "Japan", "South Korea", "Indonesia", "Singapore", "Israel"],
        "Europe": ["Finland", "Norway", "Denmark", "Germany", "France", "Italy", "Netherlands", "Sweden", "Switzerland", "Ireland", "United Kingdom"],
        "North America": ["United States", "Canada", "Mexico"],
        "South America": ["Brazil", "Argentina", "Colombia", "Chile"],
        "Oceania": ["Australia", "New Zealand"],
        "Antarctica": []
    }
    def get_continent(country):
        for continent, countries in continent_map.items():
            if country in countries:
                return continent
        return "Other"

    df['Region'] = df['Country'].apply(get_continent)

    st.sidebar.header("Dashboard Filters")

    color_options = {
        "Tealrose": px.colors.diverging.Tealrose,
        "Temps": px.colors.diverging.Temps,
        "IceFire": px.colors.cyclical.IceFire,
        "Oranges": px.colors.sequential.Oranges,
        "Purples": px.colors.sequential.Purples,
        "Greens": px.colors.sequential.Greens,
        "Viridis": px.colors.sequential.Viridis,
        "Bold": px.colors.qualitative.Bold
    }
    color_choice = st.sidebar.selectbox("Choose Color Palette", list(color_options.keys()))

    indicator_options = ["None", "All", "GDP_per_Capita", "Life_Expectancy", "Freedom", "Social_support", "Corruption_Perception", "Generosity", "Family"]
    indicator = st.sidebar.selectbox("Select Key Indicator", indicator_options)
    if indicator == "All":
        indicator = "GDP_per_Capita"
    elif indicator == "None":
        indicator = None

    countries = sorted(df["Country"].dropna().unique().tolist())
    countries.insert(0, "All")
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=[])

    regions = df["Region"].dropna().unique().tolist()
    regions.insert(0, "All")
    selected_regions = st.sidebar.multiselect("Select Regions", regions, default=[])

    df_filtered = df.copy()
    if "All" not in selected_countries and selected_countries:
        df_filtered = df_filtered[df_filtered["Country"].isin(selected_countries)]
    if "All" not in selected_regions and selected_regions:
        df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]

    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Overview", "Modeling", "Download"])

    with tab1:
        st.markdown("""
        <div style='background-color: #ffffff; padding: 2rem; border-radius: 10px; box-shadow: 0px 4px 20px rgba(0,0,0,0.1);'>
            <h2 style='color: #2C3E50;'>Description</h2>
            <p><strong>Key Question:</strong> What factors contribute most to happiness?</p>
            <p><strong>Key Variables:</strong> Happiness Score, GDP per Capita, Social Support, Freedom, Corruption Perception</p>
            <p><strong>Data Source:</strong> World Happiness Report (2015-2019)</p>
            <p>
                This dashboard serves as a strategic tool for exploring the multifaceted dimensions of global happiness. 
                By leveraging data from the World Happiness Report, it empowers users to uncover patterns, compare countries, 
                and assess how critical indicators influence happiness. 
                Policymakers, researchers, and data enthusiasts can interact with rich visualizations to understand where 
                improvements can be made and what drives well-being worldwide.
            </p>
        </div>
        <br/>
        <div style='background-color: #e8f0fe; padding: 1.5rem; border-left: 5px solid #007acc; border-radius: 5px;'>
            <h4 style='color: #2C3E50;'>Key Takeaways from the Analysis</h4>
            <ul>
                <li><strong>GDP and Social Support Drive Happiness:</strong> Countries with higher GDP per Capita and stronger Social Support systems consistently report higher happiness scores.</li>
                <li><strong>Freedom and Corruption Perception Matter:</strong> Freedom to make life choices and low corruption perception are powerful contributors to happiness.</li>
                <li><strong>Regional Differences Are Striking:</strong> Nordic countries consistently top the rankings, while some regions like Africa and parts of Asia show lower scores.</li>
                <li><strong>Modeling Insights:</strong> High R² and low RMSE values indicate strong prediction accuracy based on selected indicators.</li>
            </ul>
        </div>
        <br/>
        <div style='background-color: #f8f9fa; padding: 2rem; border-left: 6px solid #2980B9; border-radius: 5px;'>
            <h3 style='color: #2C3E50;'>Summary</h3>
            <p>This dashboard helps visualize and explore global happiness trends across countries and regions.</p>
            <p>Users can examine how key indicators like GDP, social support, and life expectancy relate to happiness scores.</p>
        </div>
        <br/>
        <div style='background-color: #eef2f5; padding: 1.5rem; border-left: 5px solid #1abc9c; border-radius: 5px;'>
            <h4 style='color: #2C3E50;'> Instructions</h4>
            <ul>
                <li>Start by uploading the World Happiness CSV file using the uploader at the top.</li>
                <li>Use the sidebar to filter by countries, regions, and select a color palette for your visuals.</li>
                <li>Navigate through the tabs: Summary, Overview (Visualizations), Modeling (ML Insights), Download (data export).</li>
            </ul>
        </div>
        <br/>
        <div style='background-color: #fcfcfc; padding: 1.5rem; border-left: 5px solid #8e44ad; border-radius: 5px;'>
            <h4 style='color: #2C3E50;'>Glossary Abbreviations</h4>
            <ul>
                <li><strong>GDP_per_Capita</strong>: Gross Domestic Product per person, adjusted for purchasing power.</li>
                <li><strong>Social_support</strong>: Availability of support from friends, family, or community.</li>
                <li><strong>Freedom</strong>: Perceived freedom to make life choices.</li>
                <li><strong>Corruption_Perception</strong>: Perception of government and institutional corruption.</li>
                <li><strong>Generosity</strong>: Willingness to help others and donate to good causes.</li>
                <li><strong>RMSE</strong>: Root Mean Squared Error — measures model prediction error.</li>
                <li><strong>R²</strong>: Coefficient of Determination — shows how well the model explains the variance in happiness.</li>
            </ul>
        </div>
        <br/>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Overview Visualizations")

        if not df_filtered.empty:
            fig1 = px.scatter(
                df_filtered,
                x=indicator,
                y="Happiness_Score",
                color="Region",
                hover_name="Country",
                title=f"{indicator} vs Happiness Score",
                color_discrete_sequence=color_options[color_choice]
            )
            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("Line Plot: Happiness Score Over Time")
            if "Year" in df.columns:
                fig_line = px.line(
                    df_filtered,
                    x="Year",
                    y="Happiness_Score",
                    color="Country",
                    title="Happiness Score Trends Over Time",
                    color_discrete_sequence=color_options[color_choice]
                )
                st.plotly_chart(fig_line, use_container_width=True)

            st.subheader("Histogram of Happiness Scores")
            fig_hist = px.histogram(
                df_filtered,
                x="Happiness_Score",
                nbins=30,
                title="Distribution of Happiness Scores",
                color_discrete_sequence=color_options[color_choice]
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            st.subheader("Average Happiness by Region")
            region_avg = df_filtered.groupby("Region")["Happiness_Score"].mean().reset_index()
            fig_bar = px.bar(
                region_avg,
                x="Region",
                y="Happiness_Score",
                color="Region",
                title="Average Happiness Score by Region",
                color_discrete_sequence=color_options[color_choice]
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("Please select at least one country and one region to view visualizations.")

    with tab3:
        st.subheader("Predicting Happiness Score")
        features = ["GDP_per_Capita", "Social_support", "Freedom", "Corruption_Perception"]
        X = df_filtered[features].dropna()
        y = df_filtered.loc[X.index, "Happiness_Score"]

        if not X.empty and len(X) > 5:
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)

            r2 = r2_score(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))

            st.write(f"**R² Score:** {r2:.4f}")
            st.write(f"**RMSE:** {rmse:.2f}")

            pred_df = pd.DataFrame({"Actual": y, "Predicted": y_pred})
            fig = px.scatter(pred_df, x="Actual", y="Predicted", title="Actual vs Predicted Happiness Score")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough data to train a model. Please adjust your filters.")

    with tab4:
        st.subheader("Download Filtered Dataset")
        st.dataframe(df_filtered)

        csv = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_happiness_data.csv",
            mime="text/csv"
        )

# Footer
st.markdown("""
<footer style='background-color: #f8f9fa; padding: 12px; text-align: center; font-size: 0.9rem; color: #444; border-top: 1px solid #ccc; margin-top: 2rem;'>
Sam Boateng 2025 | AI Communication and Visualization
</footer>
""", unsafe_allow_html=True)
