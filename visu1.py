import altair as alt
import pandas as pd
import itertools

df = pd.read_csv("dpt2020.csv", sep=";")
d = df.copy()
d = d[d["annais"] != "XXXX"]
d = d[d["preusuel"] != "_PRENOMS_RARES"]
d["annais"] = d["annais"].astype(int)
d["nombre"] = d["nombre"].astype(int)

nat = d.groupby(["preusuel", "annais"], as_index=False)["nombre"].sum()

candidates = nat.groupby("preusuel")["nombre"].sum().nlargest(500).index.tolist()

p = nat[nat["preusuel"].isin(candidates)].copy()
years = range(int(nat["annais"].min()), int(nat["annais"].max()) + 1)
grid = pd.DataFrame(
    itertools.product(candidates, years), columns=["preusuel", "annais"]
)
p = grid.merge(p, on=["preusuel", "annais"], how="left").fillna({"nombre": 0})

brush = alt.selection_interval(encodings=["x"])
scatter_brush = alt.selection_interval()
legend_sel = alt.selection_point(fields=["preusuel"], on="click", empty=True)

base = alt.Chart(p)

detail = (
    alt.Chart(p).mark_area(interpolate="monotone")
    .transform_filter(brush)
    .transform_joinaggregate(
        max_par_an="max(nombre)",
        min_par_an="min(nombre)",
        groupby=["preusuel"],
    )
    .transform_filter(scatter_brush)
    .encode(
        x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
        y=alt.Y("nombre:Q", stack=True, title="Naissance",
                axis=alt.Axis(labels=True, ticks=True, format="~s")),
        color=alt.Color("preusuel:N", title="Prénom", scale=alt.Scale(scheme="category20")),
        opacity=alt.condition(legend_sel, alt.value(0.9), alt.value(0.12)),
        tooltip=["preusuel:N", "annais:Q", "nombre:Q"],
    )
    .add_params(legend_sel)
    .properties(width=800, height=380)
)

overview = (
    alt.Chart(p).mark_area(opacity=0.5)
    .encode(
        x=alt.X("annais:Q", title=None, axis=alt.Axis(format="d")),
        y=alt.Y("sum(nombre):Q", title=None, axis=None),
    )
    .add_params(brush)
    .properties(width=800, height=60)
)

scatter = (
    alt.Chart(p)
    .transform_filter(brush)
    .transform_aggregate(
        max_par_an="max(nombre)",
        min_par_an="min(nombre)",
        moyenne="mean(nombre)",
        groupby=["preusuel"],
    )
    .mark_circle()
    .encode(
        x=alt.X("max_par_an:Q", title="Max par année"),
        y=alt.Y("min_par_an:Q", title="Min par année"),
        size=alt.Size("moyenne:Q", legend=alt.Legend(orient="right", title="Moyenne / an")),
        color=alt.Color("preusuel:N", legend=None, scale=alt.Scale(scheme="category20")),
        opacity=alt.condition(scatter_brush & legend_sel, alt.value(0.9), alt.value(0.15)),
        tooltip=["preusuel:N", "max_par_an:Q", "min_par_an:Q", "moyenne:Q"],
    )
    .add_params(scatter_brush, legend_sel)
    .properties(width=300, height=380, title="Statistiques par prénom")
)

chart = alt.hconcat(alt.vconcat(detail, overview), scatter)
chart.save("chart_names_years.html")
