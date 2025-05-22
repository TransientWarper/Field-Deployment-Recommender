# 🗺️ Field Deployment Zone Recommender

This Streamlit app allows users to upload a Digital Elevation Model (DEM) and interactively identify optimal deployment zones based on:

- 📏 Elevation range
- 📉 Slope flatness
- 🎯 Suitability score threshold

Users can visualize suitability as a color-coded heatmap, filter interactively, and download results.

If no DEM is uploaded, a synthetic terrain with varied topography will be used as a demo.

## 💻 How to Run Locally

Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
streamlit run field_deployment_app.py
```

## 📦 Built With

- [Streamlit](https://streamlit.io/) — for the interactive UI
- [NumPy](https://numpy.org/) — for slope and terrain analysis
- [Matplotlib](https://matplotlib.org/) — for color mapping
- [Rasterio](https://rasterio.readthedocs.io/) — for handling GeoTIFF files
- [Plotly](https://plotly.com/python/) — for zoomable, interactive heatmaps

## 🧠 Why This Exists

This tool provides a simple visual workflow for evaluating terrain suitability in remote field operations, logistics planning, or environmental monitoring. Filters help refine optimal regions according to site-specific constraints.

## 📫 Contact

Built by [Steven P. Boyer]  
Reach me at [stevenpboyer3@gmail.com]
