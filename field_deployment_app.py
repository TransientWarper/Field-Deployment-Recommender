import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from tempfile import NamedTemporaryFile
import rasterio
from rasterio.transform import from_origin
import os
import plotly.express as px

st.set_page_config(page_title="Field Deployment Zone Recommender", layout="wide")
st.title("📍 Field Deployment Zone Recommender")

# === Upload DEM file ===
uploaded_file = st.file_uploader("🗂️ Upload a DEM (.tif) file", type=["tif"])
if uploaded_file is not None:
    with rasterio.open(uploaded_file) as src:
        dem = src.read(1).astype(float)
        profile = src.profile
else:
    # === Sample DEM with four peaks ===
    width, height = 200, 200
    x = np.linspace(-3, 3, width)
    y = np.linspace(-3, 3, height)
    xgrid, ygrid = np.meshgrid(x, y)
    dem = (
        np.exp(-((xgrid - 1.5)**2 + (ygrid - 1.5)**2)) +
        np.exp(-((xgrid + 1.5)**2 + (ygrid - 1.5)**2)) +
        np.exp(-((xgrid - 1.5)**2 + (ygrid + 1.5)**2)) +
        np.exp(-((xgrid + 1.5)**2 + (ygrid + 1.5)**2))
    ) * 100
    transform = from_origin(0, 0, 1, 1)  # dummy transform
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "nodata": None,
        "width": width,
        "height": height,
        "count": 1,
        "crs": "EPSG:4326",
        "transform": transform
    }

# === Weighting ===
flatness_weight = 1.0

# === Calculate slope (flatness proxy) ===
dy, dx = np.gradient(dem)
slope = np.hypot(dx, dy)

# === Normalize slope to flatness score (lower slope = higher score) ===
slope_norm = (slope - slope.min()) / (slope.max() - slope.min())
flatness_score = 1 - slope_norm
weighted_score = flatness_score * flatness_weight

# === Layout with columns ===
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🏔️ Elevation Range Filter")
    rounded_min_elev = int(dem.min())
    rounded_max_elev = int(dem.max())
    elev_range = st.slider(
        "Select elevation range (m):",
        min_value=rounded_min_elev,
        max_value=rounded_max_elev,
        value=(rounded_min_elev, rounded_max_elev),
        step=5
    )
    elevation_mask = ((dem >= elev_range[0]) & (dem <= elev_range[1])).astype(float)
    weighted_score *= elevation_mask

    st.markdown("### 📉 Slope Range Filter")
    rounded_min_slope = float(round(slope.min(), 2))
    rounded_max_slope = float(round(slope.max(), 2))
    slope_range = st.slider(
        "Select slope range:",
        min_value=rounded_min_slope,
        max_value=rounded_max_slope,
        value=(rounded_min_slope, rounded_max_slope),
        step=0.05
    )
    slope_mask = ((slope >= slope_range[0]) & (slope <= slope_range[1])).astype(float)
    weighted_score *= slope_mask

    st.markdown("### 🎯 Suitability Threshold Filter")
    threshold = st.slider(
        "Minimum suitability score to display (0 = show all, 1 = show only perfect)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05
    )
    threshold_mask = (weighted_score >= threshold).astype(float)
    final_score = weighted_score * threshold_mask

    # === Statistics Panel ===
    st.markdown("---")
    st.markdown("### 📊 Suitability Stats")
    percent_suitable = 100 * np.sum(final_score > 0) / final_score.size
    selected_elev = dem[final_score > 0]
    selected_slope = slope[final_score > 0]
    st.write(f"**Percent Suitable:** {percent_suitable:.2f}%")
    if selected_elev.size > 0:
        st.write(f"**Mean Elevation:** {np.mean(selected_elev):.2f} m")
        st.write(f"**Mean Slope:** {np.mean(selected_slope):.2f}")
    else:
        st.write("No areas meet criteria.")

    # === Export Button ===
    st.markdown("---")
    st.markdown("### 💾 Export Heatmap")
    if st.button("Download PNG"):
        fig, ax = plt.subplots()
        ax.imshow(final_score, cmap="winter", vmin=0, vmax=1)
        ax.axis('off')
        with NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.savefig(tmpfile.name, bbox_inches='tight', pad_inches=0)
            st.download_button("📥 Click to Download", tmpfile.read(), file_name="suitability_map.png")

with col2:
    st.markdown("### 🗺️ Deployment Suitability Map (Zoomable)")
    fig = px.imshow(final_score, color_continuous_scale="blues", origin="lower")
    fig.update_layout(
        coloraxis_colorbar=dict(title="Suitability Score"),
        margin=dict(l=10, r=10, t=10, b=10),
        dragmode="pan"
    )
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)