"""
Streamlit viewer for pipe-network analytics.
Usage: streamlit run tools/pipe_network_viewer.py
"""

import json
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import pydeck as pdk
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (backend/.env preferred)
for env_path in (Path('backend/.env'), Path('.env')):
    if env_path.exists():
        load_dotenv(env_path)
        break

DB_PARAMS = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'sslmode': 'require'
}

@st.cache_resource(show_spinner=False)
def get_connection():
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)

@st.cache_data(show_spinner=False)
def fetch_networks():
    req = """
    CASE
        WHEN p.diameter_mm IS NULL THEN NULL
        WHEN (p.diameter_mm / 25.4) >= 24 THEN 0.15
        WHEN (p.diameter_mm / 25.4) >= 18 THEN 0.19
        WHEN (p.diameter_mm / 25.4) >= 15 THEN 0.25
        WHEN (p.diameter_mm / 25.4) >= 12 THEN 0.33
        WHEN (p.diameter_mm / 25.4) >= 10 THEN 0.28
        WHEN (p.diameter_mm / 25.4) >= 8 THEN 0.40
        WHEN (p.diameter_mm / 25.4) >= 6 THEN 0.40
        WHEN (p.diameter_mm / 25.4) >= 4 THEN 0.50
        ELSE 0.60
    END
    """
    sql = f"""
        SELECT
            pn.network_id,
            pn.name,
            pn.description,
            pn.project_id,
            proj.project_name,
            COUNT(p.pipe_id) AS pipe_count,
            SUM(CASE WHEN p.slope IS NOT NULL AND ({req}) IS NOT NULL AND p.slope < ({req}) THEN 1 ELSE 0 END) AS pipes_below_min,
            AVG(p.slope) AS avg_slope,
            MIN(p.slope - ({req})) AS worst_margin
        FROM pipe_networks pn
        LEFT JOIN projects proj ON pn.project_id = proj.project_id
        LEFT JOIN pipes p ON p.network_id = pn.network_id
        GROUP BY pn.network_id, pn.name, pn.description, pn.project_id, proj.project_name
        ORDER BY proj.project_name, pn.name
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    df = pd.DataFrame(rows)
    for col in ['avg_slope', 'worst_margin']:
        if col in df:
            df[col] = df[col].astype(float, errors='ignore')
    return df

@st.cache_data(show_spinner=False)
def fetch_pipes(network_id):
    req = """
    CASE
        WHEN p.diameter_mm IS NULL THEN NULL
        WHEN (p.diameter_mm / 25.4) >= 24 THEN 0.15
        WHEN (p.diameter_mm / 25.4) >= 18 THEN 0.19
        WHEN (p.diameter_mm / 25.4) >= 15 THEN 0.25
        WHEN (p.diameter_mm / 25.4) >= 12 THEN 0.33
        WHEN (p.diameter_mm / 25.4) >= 10 THEN 0.28
        WHEN (p.diameter_mm / 25.4) >= 8 THEN 0.40
        WHEN (p.diameter_mm / 25.4) >= 6 THEN 0.40
        WHEN (p.diameter_mm / 25.4) >= 4 THEN 0.50
        ELSE 0.60
    END
    """
    sql = f"""
        SELECT
            p.pipe_id,
            p.diameter_mm,
            p.material,
            p.slope,
            ({req}) AS required_slope,
            p.slope - ({req}) AS slope_margin,
            p.length_m,
            p.invert_up,
            p.invert_dn,
            p.status,
            ST_AsGeoJSON(p.geom) AS geom
        FROM pipes p
        WHERE p.network_id = %s
        ORDER BY p.pipe_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (network_id,))
        rows = cur.fetchall()
    df = pd.DataFrame(rows)
    numeric_cols = ['slope', 'required_slope', 'slope_margin', 'length_m', 'invert_up', 'invert_dn', 'diameter_mm']
    for col in numeric_cols:
        if col in df:
            df[col] = df[col].astype(float, errors='ignore')
    return df

@st.cache_data(show_spinner=False)
def fetch_structures(network_id):
    sql = """
        SELECT structure_id, type, rim_elev, sump_depth,
               ST_X(geom) AS lon, ST_Y(geom) AS lat,
               metadata
        FROM structures
        WHERE network_id = %s
        ORDER BY rim_elev DESC NULLS LAST
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (network_id,))
        rows = cur.fetchall()
    df = pd.DataFrame(rows)
    for col in ['rim_elev', 'sump_depth', 'lon', 'lat']:
        if col in df:
            df[col] = df[col].astype(float, errors='ignore')
    return df

st.set_page_config(page_title="Pipe Network Viewer", layout="wide")
st.title("Pipe Network Viewer")
st.write("Interactive read-only view of pipe networks, slopes, and supporting structures.")

try:
    networks_df = fetch_networks()
except Exception as exc:
    st.error(f"Failed to connect to database: {exc}")
    st.stop()

if networks_df.empty:
    st.info("No pipe networks found in the database.")
    st.stop()

network_labels = networks_df[['network_id', 'name', 'project_name']].apply(lambda row: f"{row['name']} ({row['project_name']})", axis=1)
selected_label = st.selectbox("Select a pipe network", network_labels.tolist())
selected_idx = network_labels[network_labels == selected_label].index[0]
selected_network = networks_df.loc[selected_idx]

cols = st.columns(4)
cols[0].metric("Total Pipes", int(selected_network.get('pipe_count', 0)))
cols[1].metric("Below Minimum", int(selected_network.get('pipes_below_min', 0)))
cols[2].metric("Average Slope", f"{selected_network.get('avg_slope', 0) * 100:.2f}%" if pd.notnull(selected_network.get('avg_slope')) else '-')
cols[3].metric("Worst Margin", f"{selected_network.get('worst_margin', 0) * 100:.2f}%" if pd.notnull(selected_network.get('worst_margin')) else '-')

pipes_df = fetch_pipes(selected_network.network_id)
structures_df = fetch_structures(selected_network.network_id)

if pipes_df.empty:
    st.warning("No pipes found for this network.")
else:
    st.subheader("Pipe Slopes")
    display_df = pipes_df.copy()
    display_df['Slope (%)'] = display_df['slope'].apply(lambda v: None if pd.isnull(v) else round(v * 100, 2))
    display_df['Required (%)'] = display_df['required_slope'].apply(lambda v: None if pd.isnull(v) else round(v * 100, 2))
    display_df['Margin (%)'] = display_df['slope_margin'].apply(lambda v: None if pd.isnull(v) else round(v * 100, 2))
    st.dataframe(
        display_df[['pipe_id', 'diameter_mm', 'material', 'Slope (%)', 'Required (%)', 'Margin (%)', 'length_m', 'status']]
        .rename(columns={'diameter_mm': 'Diameter (mm)', 'length_m': 'Length (m)', 'status': 'Status'}),
        hide_index=True
    )

    features = []
    for _, row in pipes_df.iterrows():
        geom = row.get('geom')
        if not geom:
            continue
        try:
            coords = json.loads(geom)['coordinates']
        except (TypeError, json.JSONDecodeError):
            continue
        color = [34, 197, 94]
        if row['slope_margin'] is not None and row['slope_margin'] < 0:
            color = [239, 68, 68]
        features.append({
            'path': coords,
            'color': color,
            'tooltip': f"Pipe {row['pipe_id']}"
        })

    if features:
        flat_coords = [coord for feature in features for coord in feature['path']]
        lons = [c[0] for c in flat_coords]
        lats = [c[1] for c in flat_coords]
        view_state = pdk.ViewState(
            longitude=sum(lons) / len(lons),
            latitude=sum(lats) / len(lats),
            zoom=15,
            pitch=35
        )
        layer = pdk.Layer(
            "PathLayer",
            data=features,
            get_path="path",
            get_color="color",
            width_scale=10,
            width_min_pixels=4,
            pickable=True
        )
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{tooltip}"}))

if not structures_df.empty:
    st.subheader("Structures")
    st.dataframe(
        structures_df.rename(columns={'rim_elev': 'Rim Elev.', 'sump_depth': 'Sump Depth', 'lon': 'Lon', 'lat': 'Lat'}),
        hide_index=True
    )

st.caption("Data sourced directly from the Supabase PostGIS database. Viewer is read-only.")
