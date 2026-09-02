# World Happiness Analysis — Animated Dashboard Walkthrough

This project is now designed as a **ready-to-explore analytical dashboard**, not a file-upload utility. The application loads a pinned public mirror of the World Happiness Report historical data automatically, normalizes the changing annual schemas, and opens directly into the visual analysis.

## 1. Data flow

```text
Pinned WHR historical data
        ↓
2015–2019 filter
        ↓
Normalize annual column-name changes
        ↓
Recover historical region labels where later files omit them
        ↓
Interactive + animated visual analysis
        ↓
2015–2018 model training
        ↓
2019 out-of-time holdout evaluation
```

### What this tells us

A visitor can open the app and immediately explore the analysis. There is no dependency on a user knowing which CSV to upload or whether that file matches the expected schema.

The source URL is pinned to a specific Git commit so the dashboard is reproducible rather than silently changing when an upstream repository changes.

## 2. Animated global happiness map

The first major output is a Plotly choropleth containing a **Play** control for 2015 through 2019.

Each frame shows country-level happiness score with rank available on hover.

### What this tells us

The map is most useful for seeing broad geographic patterns and how those patterns shift over time. It should not be used to imply that neighboring countries are statistically equivalent; it is a geographic view of country-level scores.

## 3. Country ranking race

A second animated chart shows the highest-ranked countries for each year.

The number of countries displayed can be adjusted from the dashboard sidebar.

### What this tells us

The ranking animation makes movement at the top of the distribution easier to see than a static five-year table. Because rank is relative, a country's position can change even when its own score moves only modestly.

## 4. Regional comparison

For the selected snapshot year, the dashboard calculates average happiness score by region. It also plots regional mean scores across the complete 2015–2019 period.

### What this tells us

Regional aggregation helps summarize broad patterns, but averages hide substantial country-level variation. The country map and regional chart should therefore be read together rather than treating the regional mean as representative of every country within that region.

## 5. Animated factor relationships

The dashboard lets the user switch between:

- GDP per capita
- social support
- life expectancy
- freedom
- generosity
- perceptions of corruption

For each factor, an animated scatterplot shows how its relationship with happiness score changes across years.

### What this tells us

These plots show **association**, not causation. A positive relationship between a factor and happiness score does not establish that changing that factor alone would produce the observed change in happiness.

## 6. Factor association summary

The app computes Pearson correlations between happiness score and the normalized factor columns across the 2015–2019 data.

### What this tells us

Correlation is a useful descriptive screening tool. It identifies variables that move with happiness score in this dataset, but it does not control for confounding or establish policy effects.

## 7. Out-of-time model evaluation

The previous dashboard fit a regression to the same filtered rows used for evaluation. That can make model quality look stronger than it really is.

The updated model uses:

```text
Training period: 2015–2018
Holdout period: 2019
```

Features:

```text
GDP per capita
Social support
Life expectancy
Freedom
Perceptions of corruption
```

Outputs displayed in the dashboard:

- 2019 holdout R²
- 2019 holdout RMSE
- 2019 holdout MAE
- actual-vs-predicted scatterplot
- fitted coefficient chart

### What this tells us

The error metrics now represent performance on a later year that the model did not use for fitting. That makes them a more meaningful test of whether the earlier-year relationship generalizes to 2019.

The coefficients remain descriptive associations. They should not be described as causal contributions to national happiness.

## 8. Human-readable code standard

Comments in `app.py` are used where they explain analytical intent, such as why region labels are recovered from earlier years or why the model uses a time-based holdout. The code avoids comments that merely repeat obvious syntax.

The dashboard itself also includes interpretation directly below major outputs so a reviewer does not have to infer what each visual is supposed to demonstrate.

## 9. Reproducibility and source

The project uses historical World Happiness Report releases for 2015–2019. The application reads a pinned public combined-data mirror rather than requiring a local upload.

The World Happiness Report provides historical report appendices and data-sharing information for these annual editions.

## 10. Current limitations

- Annual WHR schemas changed across the period and require explicit normalization.
- Some later-year files omit region, so the dashboard reuses a country's known historical region where possible.
- Country naming differences can affect geographic rendering for a small number of locations.
- The linear model is intentionally simple and should be treated as an interpretable baseline.
- Correlations and regression coefficients are not causal estimates.

## Reviewer path

1. Open `app.py` to see the data normalization and analytical workflow.
2. Run `streamlit run app.py`.
3. Press **Play** on the global map and country-ranking charts.
4. Switch the factor selector and watch the relationships change across years.
5. Review the 2019 holdout metrics and actual-vs-predicted chart.
6. Read the interpretation text directly beneath the outputs before drawing conclusions.
