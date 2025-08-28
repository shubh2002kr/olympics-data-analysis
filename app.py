# app.py
# Olympics Data Analysis — Built by Shubh Kumar
# Run: streamlit run app.py

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------- App Config ----------------------
st.set_page_config(page_title="Olympics Data Analysis", page_icon="🏅", layout="wide")

# ---------------------- Helpers -------------------------
@st.cache_data(show_spinner=False)
def load_data(athlete_events_file: io.BytesIO, noc_regions_file: io.BytesIO) -> pd.DataFrame:
    ae = pd.read_csv(athlete_events_file)
    noc = pd.read_csv(noc_regions_file)

    # Standardize column names just in case
    ae.columns = [c.strip() for c in ae.columns]
    noc.columns = [c.strip() for c in noc.columns]

    # Merge NOC codes to regions/countries
    df = ae.merge(noc, how="left", on="NOC")
    # Clean types
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    if "Age" in df.columns:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    if "Height" in df.columns:
        df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
    if "Weight" in df.columns:
        df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

    # Medal normalization
    df["Medal"] = df["Medal"].fillna("No Medal")
    df["HasMedal"] = (df["Medal"] != "No Medal").astype(int)

    # A robust "team-medal" dedup key to avoid counting the same medal multiple times for team events
    # One medal per team per event per Games
    dedup_cols = ["Games", "Season", "Year", "Sport", "Event", "NOC", "Medal"]
    df_team_medals = (
        df.loc[df["Medal"] != "No Medal", dedup_cols]
        .drop_duplicates()
        .assign(Count=1)
    )

    return df, df_team_medals


def compute_kpis(df: pd.DataFrame, df_team_medals: pd.DataFrame, season_filter, years, countries):
    dff = df.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]

    if years:
        dff = dff[(dff["Year"] >= years[0]) & (dff["Year"] <= years[1])]

    if countries:
        dff = dff[dff["NOC"].isin(countries)]

    medals_df = df_team_medals.copy()
    if season_filter != "Both":
        medals_df = medals_df[medals_df["Season"] == season_filter]
    if years:
        medals_df = medals_df[(medals_df["Year"] >= years[0]) & (medals_df["Year"] <= years[1])]
    if countries:
        medals_df = medals_df[medals_df["NOC"].isin(countries)]

    total_medals = int(medals_df["Count"].sum())
    total_athletes = dff["ID"].nunique() if "ID" in dff.columns else dff[["Name","Year","Event"]].drop_duplicates().shape[0]
    total_countries = dff["NOC"].nunique()
    total_sports = dff["Sport"].nunique()

    return total_medals, total_athletes, total_countries, total_sports


def medals_over_time(df_team_medals: pd.DataFrame, season_filter, countries_sel):
    dff = df_team_medals.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    if countries_sel:
        dff = dff[dff["NOC"].isin(countries_sel)]
    grp = dff.groupby(["Year", "NOC"], as_index=False)["Count"].sum()
    if grp.empty: 
        return px.line(title="No data to display")
    fig = px.line(grp, x="Year", y="Count", color="NOC", markers=True,
                  title="Medals Over Time (team-adjusted)")
    fig.update_layout(hovermode="x unified", xaxis=dict(dtick=4))
    return fig


def top_countries(df_team_medals: pd.DataFrame, season_filter, years, top_n=10):
    dff = df_team_medals.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    if years:
        dff = dff[(dff["Year"] >= years[0]) & (dff["Year"] <= years[1])]

    grp = dff.groupby("NOC", as_index=False)["Count"].sum().sort_values("Count", ascending=False).head(top_n)
    if grp.empty: 
        return px.bar(title="No data to display")
    fig = px.bar(grp, x="NOC", y="Count", title=f"Top {top_n} Countries by Medals", text_auto=True)
    fig.update_layout(xaxis_title="NOC", yaxis_title="Medals")
    return fig


def gender_participation(df: pd.DataFrame, season_filter):
    dff = df.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    # Unique athletes per Games by Sex (ID + Games)
    if "ID" in dff.columns:
        dff_unique = dff.drop_duplicates(subset=["Games", "ID", "Sex"])
    else:
        dff_unique = dff.drop_duplicates(subset=["Games", "Name", "Sex"])
    gp = dff_unique.groupby(["Year", "Sex"], as_index=False).size().rename(columns={"size":"Participants"})
    if gp.empty: 
        return px.area(title="No data to display")
    fig = px.area(gp, x="Year", y="Participants", color="Sex",
                  title="Gender Participation Over Time", groupnorm=None)
    fig.update_layout(hovermode="x unified", xaxis=dict(dtick=4))
    return fig


def sport_popularity(df: pd.DataFrame, season_filter, years, countries_sel):
    dff = df.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    if years:
        dff = dff[(dff["Year"] >= years[0]) & (dff["Year"] <= years[1])]
    if countries_sel:
        dff = dff[dff["NOC"].isin(countries_sel)]

    # Participation by sport (unique athlete entries per Games+Event+ID)
    if "ID" in dff.columns:
        dff_unique = dff.drop_duplicates(subset=["Games", "Sport", "Event", "ID"])
    else:
        dff_unique = dff.drop_duplicates(subset=["Games", "Sport", "Event", "Name"])

    sp = dff_unique.groupby("Sport", as_index=False).size().rename(columns={"size":"Entries"})
    sp = sp.sort_values("Entries", ascending=False).head(20)
    if sp.empty:
        return px.bar(title="No data to display")
    fig = px.bar(sp, x="Entries", y="Sport", orientation="h", title="Top Sports by Participation (Top 20)", text_auto=True)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    return fig


def top_athletes(df: pd.DataFrame, season_filter, years, countries_sel, top_n=15):
    dff = df.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    if years:
        dff = dff[(dff["Year"] >= years[0]) & (dff["Year"] <= years[1])]
    if countries_sel:
        dff = dff[dff["NOC"].isin(countries_sel)]

    # Athletes by medal count (team-adjusted: medal per athlete per event per Games)
    medal_rows = dff[dff["Medal"] != "No Medal"]
    if medal_rows.empty:
        return px.bar(title="No data to display")
    dedup = medal_rows.drop_duplicates(subset=["Games", "Event", "Medal", "Name"])
    grp = dedup.groupby(["Name", "NOC"], as_index=False).size().rename(columns={"size":"Medals"})
    grp = grp.sort_values("Medals", ascending=False).head(top_n)
    fig = px.bar(grp, x="Medals", y="Name", color="NOC", orientation="h",
                 title=f"Top {top_n} Athletes by Medal Count (team-adjusted)", text_auto=True)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    return fig


def medals_breakdown(df: pd.DataFrame, season_filter, years, countries_sel):
    dff = df.copy()
    if season_filter != "Both":
        dff = dff[dff["Season"] == season_filter]
    if years:
        dff = dff[(dff["Year"] >= years[0]) & (dff["Year"] <= years[1])]
    if countries_sel:
        dff = dff[dff["NOC"].isin(countries_sel)]

    medal_rows = dff[dff["Medal"].isin(["Gold","Silver","Bronze"])]
    if medal_rows.empty:
        return px.bar(title="No data to display")
    # Team-adjusted: one row per team medal per Games+Event+Medal+NOC
    dedup = medal_rows.drop_duplicates(subset=["Games", "Event", "Medal", "NOC"])
    grp = dedup.groupby(["NOC", "Medal"], as_index=False).size().rename(columns={"size":"Count"})
    fig = px.bar(grp, x="NOC", y="Count", color="Medal", barmode="group", title="Medal Breakdown by Country")
    return fig


# ---------------------- Sidebar -------------------------
st.sidebar.title("🏅 Olympics Data Analysis")
st.sidebar.caption("Upload the Kaggle dataset files:\n- athlete_events.csv\n- noc_regions.csv")

ae_file = st.sidebar.file_uploader("athlete_events.csv", type=["csv"])
noc_file = st.sidebar.file_uploader("noc_regions.csv", type=["csv"])

with st.sidebar.expander("Filters", expanded=True):
    season = st.selectbox("Season", ["Both", "Summer", "Winter"], index=0)
    st.caption("Tip: Use country filters to compare nations.")
    countries_selection_mode = st.radio("Country Selection", ["All", "Pick countries"], index=0, horizontal=True)
    picked_countries = None
    year_range = None

# ---------------------- Data Load -----------------------
if ae_file is None or noc_file is None:
    st.info("↖️ Please upload **athlete_events.csv** and **noc_regions.csv** to begin.")
    st.stop()

df, df_team_medals = load_data(ae_file, noc_file)

# Build dynamic filter options after data loads
all_years = sorted(df["Year"].dropna().unique().astype(int).tolist())
min_year, max_year = (min(all_years), max(all_years)) if all_years else (0, 0)
with st.sidebar.expander("More Filters", expanded=True):
    year_range = st.slider("Year Range", min_value=int(min_year), max_value=int(max_year),
                           value=(int(min_year), int(max_year)), step=4)
    all_nocs = sorted(df["NOC"].dropna().unique().tolist())
    if countries_selection_mode == "Pick countries":
        picked_countries = st.multiselect("Countries (NOC)", options=all_nocs, default=["USA","URS","CHN","GBR","IND"])

# ---------------------- Header --------------------------
st.title("🏅 Olympics Data Analysis")
st.caption("Built by **Shubh Kumar** — Explore medals, participation, and sport popularity over time.")

# ---------------------- KPIs ----------------------------
m1, m2, m3, m4 = st.columns(4)
total_medals, total_athletes, total_countries, total_sports = compute_kpis(
    df, df_team_medals, season, year_range, picked_countries if countries_selection_mode=="Pick countries" else None
)
m1.metric("Total Medals (team-adjusted)", f"{total_medals:,}")
m2.metric("Unique Athletes", f"{total_athletes:,}")
m3.metric("Countries Participated", f"{total_countries:,}")
m4.metric("Sports", f"{total_sports:,}")

st.markdown("---")

# ---------------------- Tabs ----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Medals Over Time",
    "🥇 Top Countries",
    "⚖️ Gender Participation",
    "🏟️ Sport Popularity",
    "👤 Top Athletes"
])

with tab1:
    fig = medals_over_time(
        df_team_medals,
        season,
        picked_countries if countries_selection_mode=="Pick countries" else None
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Medal Table (team-adjusted)")
    # Build a pivot of medals by country and year (team-adjusted)
    dff = df_team_medals.copy()
    if season != "Both":
        dff = dff[dff["Season"] == season]
    if year_range:
        dff = dff[(dff["Year"] >= year_range[0]) & (dff["Year"] <= year_range[1])]
    if countries_selection_mode == "Pick countries" and picked_countries:
        dff = dff[dff["NOC"].isin(picked_countries)]
    table = dff.groupby(["Year","NOC"], as_index=False)["Count"].sum()
    if not table.empty:
        pivot = table.pivot(index="Year", columns="NOC", values="Count").fillna(0).astype(int)
        st.dataframe(pivot, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

with tab2:
    fig = top_countries(df_team_medals, season, year_range, top_n=12)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = medals_breakdown(
        df,
        season,
        year_range,
        picked_countries if countries_selection_mode=="Pick countries" else None
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig = gender_participation(df, season)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Participation by Country & Sex (Table)")
    # Unique athletes per Games-country-sex
    if "ID" in df.columns:
        dff_u = df.drop_duplicates(subset=["Games","NOC","Sex","ID"])
    else:
        dff_u = df.drop_duplicates(subset=["Games","NOC","Sex","Name"])
    if season != "Both":
        dff_u = dff_u[dff_u["Season"] == season]
    if year_range:
        dff_u = dff_u[(dff_u["Year"] >= year_range[0]) & (dff_u["Year"] <= year_range[1])]
    if countries_selection_mode == "Pick countries" and picked_countries:
        dff_u = dff_u[dff_u["NOC"].isin(picked_countries)]
    part_table = dff_u.groupby(["Year","NOC","Sex"], as_index=False).size().rename(columns={"size":"Participants"})
    st.dataframe(part_table, use_container_width=True)

with tab4:
    fig = sport_popularity(
        df,
        season,
        year_range,
        picked_countries if countries_selection_mode=="Pick countries" else None
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sport-Event Participation Heatmap (Top 15 Sports)")
    # Heatmap of participation by Year vs Sport
    if "ID" in df.columns:
        dff_h = df.drop_duplicates(subset=["Games","Sport","Event","ID"])
    else:
        dff_h = df.drop_duplicates(subset=["Games","Sport","Event","Name"])
    if season != "Both":
        dff_h = dff_h[dff_h["Season"] == season]
    if year_range:
        dff_h = dff_h[(dff_h["Year"] >= year_range[0]) & (dff_h["Year"] <= year_range[1])]
    if countries_selection_mode == "Pick countries" and picked_countries:
        dff_h = dff_h[dff_h["NOC"].isin(picked_countries)]

    top_sports = (
        dff_h.groupby("Sport", as_index=False)
        .size().rename(columns={"size":"Entries"})
        .sort_values("Entries", ascending=False).head(15)["Sport"].tolist()
    )
    dff_h = dff_h[dff_h["Sport"].isin(top_sports)]
    heat = (
        dff_h.groupby(["Year","Sport"], as_index=False)
        .size().rename(columns={"size":"Entries"})
    )
    if not heat.empty:
        heat_pivot = heat.pivot(index="Sport", columns="Year", values="Entries").fillna(0)
        # Make a simple image-like heatmap via plotly imshow
        fig_h = px.imshow(
            heat_pivot.values,
            labels=dict(x="Year", y="Sport", color="Entries"),
            x=heat_pivot.columns, y=heat_pivot.index,
            title="Participation Heatmap"
        )
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("No data for the selected filters.")

with tab5:
    fig = top_athletes(
        df,
        season,
        year_range,
        picked_countries if countries_selection_mode=="Pick countries" else None,
        top_n=20
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------- Footer --------------------------
st.markdown("---")
st.caption(
    "Data source format compatible with Kaggle's **athlete_events.csv** and **noc_regions.csv**. "
    "Team-adjusted counting prevents double-counting medals in team events."
)
