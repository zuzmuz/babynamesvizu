import pandas as pd
import altair as alt

# --- Lecture du fichier ---
names = pd.read_csv("dpt2020.csv", sep=";")
names.drop(names[names.preusuel == '_PRENOMS_RARES'].index, inplace=True)

# --- Somme des effectifs par prénom et par sexe ---
names = (
    names.groupby(["preusuel", "sexe"])["nombre"]
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

# --- Remettre le prénom comme colonne ---
names = names.reset_index()

# --- Création des points ---
points = alt.Chart(names).mark_circle(size=40).encode(
    x=alt.X(
        "M:Q",
        scale=alt.Scale(type="log"),
        title="Total of boys"
    ),
    y=alt.Y(
        "F:Q",
        scale=alt.Scale(type="log"),
        title="Total of girls"
    ),
    tooltip=[
        alt.Tooltip("preusuel:N", title="Prénom"),
        alt.Tooltip("M:Q", format=","),
        alt.Tooltip("F:Q", format=",")
    ]
).properties(
    title="Popularity of unisex names in France (1900–2020)"
).interactive()

# --- Création de la diagonale ---
diag = pd.DataFrame({
    "x": [100, 1000000],
    "y": [100, 1000000]
})
ligne = alt.Chart(diag).mark_line().encode(
    x="x:Q",
    y="y:Q"
)

# --- Composition ---
chart = (points + ligne)
chart.save('prenoms_mixtes_france.html', inline=True)

print("Export terminé : prenoms_mixtes_france.html")