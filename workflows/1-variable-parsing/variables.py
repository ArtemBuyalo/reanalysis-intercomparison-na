import pandas as pd
import xscen as xs
from xscen.config import CONFIG

xs.load_config("paths.yml", verbose=False, reset=True)

# Sources/datasets of interest
sources_of_interest = ["ERA5-Land", "EMDNA", "CaSR", "PCICBlend"]

# Load all data catalog paths from config
dc_paths = CONFIG["extract"]["reconstruction"]["search_data_catalogs"]["data_catalogs"]

# Helper list to collect (source, variable, frequency) triplets across all catalogs
all_source_variable_freq = []

def extract_source_variable_freq(dc_path, valid_sources):
    """Extract (source, variable, frequency) from a data catalog, filtered by source."""
    catalog = xs.DataCatalog(dc_path)
    df = catalog.df[["source", "variable", "frequency"]]
    return df[df["source"].isin(valid_sources)]

# Extract and combine
for dc_path in dc_paths:
    df_subset = extract_source_variable_freq(dc_path, sources_of_interest)
    all_source_variable_freq.append(df_subset)

combined_df = pd.concat(all_source_variable_freq).drop_duplicates()

# Clean variable formatting (e.g. remove "(pr,)")
combined_df["variable"] = combined_df["variable"].astype(str).str.extract(r"\(?\s*([a-zA-Z0-9_]+)\s*,?\)?")[0]

# Create a unique multi-index from (variable, frequency)
combined_df = combined_df.assign(present="Yes")
presence_matrix = (
    combined_df
    .pivot_table(index=["variable", "frequency"], columns="source", values="present", aggfunc="first", fill_value="No")
    .sort_index()
    .sort_index(axis=1)
)

print(presence_matrix)

# ----------------------------------------
# Format and style the matrix as HTML
# ----------------------------------------

def color_yes_no(val):
    return {
        "Yes": "background-color: #c6f6d5;",  # light green
        "No": "background-color: #fed7d7;"   # light red
    }.get(val, "")

styled = presence_matrix.style.map(color_yes_no)

styled.set_table_styles([
    {"selector": "table", "props": [
        ("font-family", "Segoe UI, Arial, sans-serif"),
        ("border-collapse", "collapse"),
        ("width", "100%"),
        ("table-layout", "fixed")
    ]},
    {"selector": "th, td", "props": [
        ("text-align", "center"),
        ("padding", "8px"),
        ("border", "1px solid #ccc"),
        ("white-space", "nowrap"),
        ("overflow", "hidden"),
        ("text-overflow", "ellipsis")
    ]}
], overwrite=False)

# Export to HTML
styled.to_html("variables_by_source.html", escape=False)