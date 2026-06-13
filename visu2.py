import altair as alt
import pandas as pd
import geopandas as gpd
import json

alt.data_transformers.disable_max_rows()

# --- Chargement des prénoms ---
names = pd.read_csv("dpt2020.csv", sep=";")
names.drop(names[names.preusuel == '_PRENOMS_RARES'].index, inplace=True)
names.drop(names[names.dpt == 'XX'].index, inplace=True)

# --- Chargement des données géographiques ---
depts = gpd.read_file('departements-version-simplifiee.geojson')
depts_geojson = json.loads(depts.to_json())

# --- Agrégation par département × prénom (TOUTES naissances) ---
grouped_names = names.groupby(['dpt', 'preusuel', 'sexe'], as_index=False)['nombre'].sum()

# --- Total naissances par département ---
total_par_dept = (
    grouped_names.groupby('dpt', as_index=False)['nombre'].sum()
    .rename(columns={'dpt': 'code', 'nombre': 'total_dept'})
)

# --- Proportion nationale et ratio multiplicatif ---
total_national = grouped_names['nombre'].sum()
prop_nationale = (
    grouped_names.groupby('preusuel', as_index=False)['nombre'].sum()
    .assign(prop_nationale=lambda df: df['nombre'] / total_national)
    [['preusuel', 'prop_nationale']]
)

total_par_dept_serie = grouped_names.groupby('dpt')['nombre'].sum().rename('total_dept')
gn = grouped_names.join(total_par_dept_serie, on='dpt')
gn['prop_dept'] = gn['nombre'] / gn['total_dept']
gn = gn.merge(prop_nationale, on='preusuel')
gn['ratio'] = gn['prop_dept'] / gn['prop_nationale']

# --- Top 30 par volume par département ---
top30 = (
    gn.sort_values('nombre', ascending=False)
    .groupby('dpt').head(30)
    .reset_index(drop=True)
)

# --- Top 15 par ratio par département ---
seuil_national = 0.0001
top15 = (
    gn[gn['prop_nationale'] >= seuil_national]
    .sort_values('ratio', ascending=False)
    .groupby('dpt').head(15)
    .reset_index(drop=True)
    .assign(base=1.0)
)

# --- Sélection sur 'dept_code' créé par transform_calculate sur la carte ---
dept_selection = alt.selection_point(
    name='dept_sel',
    fields=['dept_code'],
    on='click',
    clear='dblclick',
    empty='none'
)

# --- Carte ---
map_chart = (
    alt.Chart(
        alt.InlineData(values=depts_geojson, format=alt.DataFormat(property='features', type='json'))
    )
    .mark_geoshape(stroke='white')
    .transform_calculate(dept_code='datum.properties.code')
    .transform_lookup(
        lookup='dept_code',
        from_=alt.LookupData(data=total_par_dept, key='code', fields=['total_dept'])
    )
    .encode(
        tooltip=[
            alt.Tooltip('properties.nom:N', title='Département'),
            alt.Tooltip('dept_code:N', title='Code'),
            alt.Tooltip('total_dept:Q', title='Naissances', format=','),
        ],
        color=alt.Color('total_dept:Q', title='Naissances', scale=alt.Scale(scheme='blues')),
        opacity=alt.condition(dept_selection, alt.value(1), alt.value(0.35)),
    )
    .add_params(dept_selection)
    .project('mercator')
    .properties(width=450, height=600, title='Cliquez un département')
)

# --- Pie chart : top 30 par volume, filtré par sélection ---
# top30 a une colonne 'dpt' qui doit matcher dept_code sélectionné
# On renomme dpt → dept_code pour que transform_filter(dept_selection) fonctionne
pie_chart = (
    alt.Chart(top30.rename(columns={'dpt': 'dept_code'}))
    .mark_arc()
    .transform_filter(dept_selection)
    .encode(
        theta=alt.Theta('nombre:Q', stack=True),
        color=alt.Color('preusuel:N', legend=None,
                         sort=alt.EncodingSortField(field='nombre', order='descending')),
        order=alt.Order('nombre:Q', sort='descending'),
        tooltip=[
            alt.Tooltip('preusuel:N', title='Prénom'),
            alt.Tooltip('nombre:Q', title='Naissances', format=','),
            alt.Tooltip('prop_dept:Q', title='% dept', format='.2%'),
            alt.Tooltip('prop_nationale:Q', title='% national', format='.2%'),
        ],
    )
    .properties(width=320, height=320, title='Top 30 du département')
)

# --- Bar chart : top 15 par ratio, filtré par sélection ---
bar_chart = (
    alt.Chart(top15.rename(columns={'dpt': 'dept_code'}))
    .mark_bar()
    .transform_filter(dept_selection)
    .encode(
        x=alt.X('base:Q', title='× la moyenne nationale', scale=alt.Scale(domainMin=1, zero=False)),
        x2=alt.X2('ratio:Q'),
        y=alt.Y('preusuel:N', title='Prénom',
                 sort=alt.EncodingSortField(field='ratio', order='descending')),
        color=alt.Color('ratio:Q', scale=alt.Scale(scheme='orangered', domainMin=1), legend=None),
        tooltip=[
            alt.Tooltip('preusuel:N', title='Prénom'),
            alt.Tooltip('ratio:Q', title='× la moyenne nationale', format='.2f'),
            alt.Tooltip('prop_dept:Q', title='% dept', format='.3%'),
            alt.Tooltip('prop_nationale:Q', title='% national', format='.3%'),
            alt.Tooltip('nombre:Q', title='Naissances dept', format=','),
        ],
    )
    .properties(width=320, height=380, title='Top 15 sur-représentés vs France')
)

# --- Composition ---
chart = (map_chart | (pie_chart & bar_chart)).resolve_scale(color='independent')
chart.save('carte_prenoms_france.html', inline=True)

print("Export terminé : carte_prenoms_france.html")