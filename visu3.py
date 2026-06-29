import pandas as pd
import altair as alt

# --- Lecture du fichier ---
raw = pd.read_csv("dpt2020.csv", sep=";")
raw = raw[raw["preusuel"] != "_PRENOMS_RARES"]

# --- Somme des effectifs par prénom et par sexe ---
names = (
    raw.groupby(["preusuel", "sexe"])["nombre"]
    .sum()
    .unstack(fill_value=0)
)

# --- Conservation des prénoms voulus seulement,
# c'est-à-dire les prénoms mixtes donnés au moins 200 fois dans chaque sexe,
# et pour lesquels le ratio sexe majoritaire / minoritaire ne dépasse pas 50 ---
names = names.rename(columns={1: "M", 2: "F"})
names = names[(names["M"] > 200) & (names["F"] > 200)]
names["ratio"] = names[["M", "F"]].max(axis=1) / names[["M", "F"]].min(axis=1)
names = names[names["ratio"] <= 50]


# --- Calculs par année
# raw = raw[raw["annais"] != "XXXX"]
# raw["annais"] = raw["annais"].astype(int)

unisex_names = set(names.index)

names_by_year = (
    raw[raw["preusuel"].isin(unisex_names)]
    .groupby(["preusuel", "annais", "sexe"])["nombre"]
    .sum()
    .unstack(fill_value=0)
    .rename(columns={1: "M", 2: "F"})
    .reset_index()
)

# --- Définition du slider
all_time_toggle = alt.binding_checkbox(name="All time: ")
all_time_select = alt.param(name="all_time", value=True, bind=all_time_toggle)

year_slider = alt.binding_range(min=1905, max=2020, step=1, name="Central year: ")
year_select = alt.param(name="yr", value=1960, bind=year_slider)

# --- Création des points ---
points = (
    alt.Chart(names_by_year)
    .mark_circle(size=40)
    .encode(
        x=alt.X("M:Q", scale=alt.Scale(type="log", domainMin=alt.expr("all_time ? 100 : 20"), domainMax=alt.expr("all_time ? 500000 : 200000")), title="Total of boys"),
        y=alt.Y("F:Q", scale=alt.Scale(type="log", domainMin=alt.expr("all_time ? 100 : 20"), domainMax=alt.expr("all_time ? 500000 : 200000")), title="Total of girls"),
        color=alt.Color(
            "ratio:Q",
            scale=alt.Scale(
                type="log",
                scheme="plasma",
                domain=[1, 50],
                reverse=True
            ),
            legend=alt.Legend(title="M/F ratio")
        ),
        tooltip=[
            alt.Tooltip("preusuel:N", title="Prénom"),
            alt.Tooltip("M:Q", format=","),
            alt.Tooltip("F:Q", format=","),
            alt.Tooltip("ratio:Q", format=".1f", title="Ratio M/F"),
        ],
    )
    .transform_filter(
    "all_time || ((datum.annais >= yr - 5) & (datum.annais <= yr + 5))"
    )
    .transform_aggregate(
        M="sum(M)",
        F="sum(F)",
        groupby=["preusuel"]
    )
    .transform_calculate(
        ratio="max(datum.M, datum.F) / min(datum.M, datum.F)"
    )
    .transform_filter(
    "all_time ? (datum.M > 200 && datum.F > 200) : (datum.M > 20 && datum.F > 20)"
    )
    .add_params(year_select, all_time_select)
    .properties(title="Popularity of unisex names in France (1900–2020)")
    .interactive()
)

# --- Création de la diagonale ---
diag = pd.DataFrame({
    "x": [10, 1000000],
    "y": [10, 1000000]
})
ligne = alt.Chart(diag).mark_line().encode(
    x="x:Q",
    y="y:Q"
)

# --- Composition ---
chart = (points + ligne)
chart.save('prenoms_mixtes_france.html')

print("Export terminé : prenoms_mixtes_france.html")