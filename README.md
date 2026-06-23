# Baby Names Visualization — France (1900–2020)

Three interactive visualizations exploring French baby name data across time, geography, and gender, built with Python and Altair. Each script generates a standalone HTML file you can open in any browser.

## Visualizations

### 1. Popularity Over Time (`visu1.py`)
This visualization explores the popularity of French first names from 1900 to 2020, combining three linked views. The central streamgraph shows how the volume of births per name evolves over time, stacked to convey both individual trajectories and the overall total. The bottom strip acts as a period selector: brushing a range of years filters the main chart and recomputes the statistics shown elsewhere. The scatter plot on the right summarizes each name over the selected period, plotting its maximum yearly count against its minimum, with point size encoding the average. Selecting a rectangular region in the scatter filters the streamgraph to names matching that statistical profile. For instance, isolating names that were consistently present versus those with brief spikes. Clicking any band or point highlights that name across both views.

**Strengths**. The coordinated views let a reader move fluidly between the temporal shape of a name's popularity and its aggregate profile, and the period brush makes those statistics conditional on the window of interest rather than fixed over the whole century. The scatter's max/min/mean encoding surfaces structural differences between names, perennial staples, sudden fads, slow risers, that are hard to read off the streamgraph alone.
Weaknesses. With many names stacked, the streamgraph becomes dense and individual bands are hard to follow, and the categorical color palette repeats once the name pool grows large, so color alone doesn't uniquely identify a name. Because the minimum is computed over a zero-filled grid, most names sit near zero on the scatter's y-axis unless a short, recent window is selected, which can crowd points along the baseline. The view favors absolute birth counts, so long-dominant names occupy disproportionate vertical space regardless of their relative share in any given year.

### 2. Geographical Distribution (`visu2.py`)
Three synchronized panels exploring how names vary across French departments.
- **Map (left):** Choropleth of French departments colored by total births — click any department to filter the other panels
- **Pie chart (top-right):** Top 30 most common names in the selected department
- **Bar chart (bottom-right):** Top 15 names most over-represented in the selected department compared to the national average (shown as a ratio multiplier)

### 3. Unisex Names (`visu3.py`)
A scatter plot on logarithmic scales identifying truly unisex names (at least 200 births in each gender and a max/min gender ratio ≤ 50:1).
- X-axis: total male births (log scale)
- Y-axis: total female births (log scale)
- The diagonal reference line marks a perfect 1:1 gender split
- Hover over any point to see the name and exact counts

## Data

| File | Description |
|------|-------------|
| `dpt2020.csv` | Main dataset — births by name, year, department, and gender (1900–2020) |
| `departements-version-simplifiee.geojson` | Simplified French department boundaries (used by visu2.py) |
| `departements-avec-outre-mer.geojson` | Full boundaries including overseas territories |

## Requirements

- Python 3.12+
- pip

## Setup and Usage

```bash
# 1. Clone the repository
git clone <repo-url>
cd babynamesvizu

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# or use uv


# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the visualizations
python visu1.py   # chart_names_years.html
python visu2.py   # carte_prenoms_france.html
python visu3.py   # prenoms_mixtes_france.html
```

Then open any of the generated `.html` files in your browser, no server needed.
