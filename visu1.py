import altair as alt
import pandas as pd
import itertools

df = pd.read_csv("dpt2020.csv", sep=";")
d = df.copy()
d = d[d["annais"] != "XXXX"]  # drop unknown-year rows
d = d[d["preusuel"] != "_PRENOMS_RARES"]  # drop the rare-name bucket
d["annais"] = d["annais"].astype(int)
d["nombre"] = d["nombre"].astype(int)


nat = d.groupby(["preusuel", "annais"], as_index=False)["nombre"].sum()

candidates = nat.groupby("preusuel")["nombre"].sum().nlargest(500).index.tolist()

# --- chart ---
sel = alt.selection_point(fields=["preusuel"], bind="legend")

p = nat[nat["preusuel"].isin(candidates)]
p = nat.copy()
years = range(int(p["annais"].min()), int(p["annais"].max()) + 1)
grid = pd.DataFrame(
    itertools.product(candidates, years), columns=["preusuel", "annais"]
)
p = grid.merge(p, on=["preusuel", "annais"], how="left").fillna({"nombre": 0})

brush = alt.selection_interval(encodings=["x"])
scatter_brush = alt.selection_interval()
legend_sel = alt.selection_point(fields=["preusuel"], on="click", empty=True)

base = alt.Chart(p)

# click a band to isolate it; click empty space to reset
# click = alt.selection_point(fields=['preusuel'], on='click', empty=True)

detail = (
    base.mark_area(interpolate="monotone")
    .encode(
        x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
        y=alt.Y("nombre:Q", stack="center", title=None, axis=None),
        color=alt.Color(
            "preusuel:N", title="Prénom", scale=alt.Scale(scheme="category20")
        ),
        opacity=alt.condition(legend_sel, alt.value(0.9), alt.value(0.12)),
        tooltip=["preusuel:N", "annais:Q", "nombre:Q"],
    )
    .transform_filter(brush)  # zoom to brushed period
    .transform_filter(scatter_brush)
    .add_params(legend_sel)
    .properties(width=800, height=380)
)

overview = (
    base.mark_area(opacity=0.5)
    .encode(
        x=alt.X("annais:Q", title=None, axis=alt.Axis(format="d")),
        y=alt.Y("sum(nombre):Q", title=None, axis=None),
    )
    .add_params(brush)
    .properties(width=800, height=60)
)

# --- scatter data: per-name stats over the years the name actually appears ---
stats = (
    nat[nat["preusuel"].isin(candidates)]
    .groupby("preusuel")["nombre"]
    .agg(max_par_an="max", min_par_an="min", moyenne="mean")
    .reset_index()
)

scatter = (
    alt.Chart(stats)
    .mark_circle()
    .encode(
        x=alt.X("max_par_an:Q", title="Max par année", scale=alt.Scale(type="log")),
        y=alt.Y("min_par_an:Q", title="Min par année", scale=alt.Scale(type="log")),
        size=alt.Size("moyenne:Q", title="Moyenne / an"),
        color=alt.Color(
            "preusuel:N", legend=None, scale=alt.Scale(scheme="category20")
        ),
        opacity=alt.condition(legend_sel, alt.value(0.9), alt.value(0.12)),
        tooltip=["preusuel:N", "max_par_an:Q", "min_par_an:Q", "moyenne:Q"],
    )
    .add_params(legend_sel)
    .add_params(scatter_brush)
    .properties(width=300, height=380, title="Statistiques par prénom")
)

(scatter | (detail & overview)).save("chart_names_years.html")
