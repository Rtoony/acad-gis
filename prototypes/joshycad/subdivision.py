import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from utils.cad_generator import SubdivisionGenerator
from utils.visualizer import CADVisualizer
from data.sample_data import get_subdivision_data

def get_sample_subdivision_lots():
    """Sample lot data for editable subdivision"""
    return [
        {"lot_number": "1", "address": "101 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 1800, "setback_front": 25.0, "setback_rear": 10.0},
        {"lot_number": "2", "address": "102 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 2100, "setback_front": 25.0, "setback_rear": 10.0},
        {"lot_number": "3", "address": "103 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 2400, "setback_front": 25.0, "setback_rear": 10.0},
        {"lot_number": "4", "address": "104 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 1950, "setback_front": 25.0, "setback_rear": 10.0},
        {"lot_number": "5", "address": "105 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 2200, "setback_front": 25.0, "setback_rear": 10.0},
        {"lot_number": "6", "address": "106 MAIN ST", "width": 60.0, "depth": 100.0, "building_sf": 1850, "setback_front": 25.0, "setback_rear": 10.0},
    ]

def show_scenario():
    st.header("Subdivision Layout")
    
    st.info("""
    Create automated subdivision layouts with residential lots, buildings, streets, sidewalks, driveways, 
    trees, and utility easements organized across professional CAD layers.
    """)
    
    st.markdown("---")
    
    # Data source selection
    data_source = st.radio(
        "**Select Data Source:**",
        ["📝 Sample Subdivision (Edit Lots & Export)", "📁 Upload Lot Data CSV"],
        horizontal=True
    )
    
    lot_data = []
    
    if data_source == "📝 Sample Subdivision (Edit Lots & Export)":
        st.info("✨ **Pro Tip:** Edit lot parameters below, adjust building sizes and setbacks, then export complete subdivision plan!")
        
        # Advanced Layout Options (Collapsible)
        with st.expander("⚙️ Advanced Layout Configuration", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Lot Grid Layout:**")
                num_rows = st.number_input("Number of Rows:", value=2, min_value=1, max_value=5, help="How many rows of lots")
                num_cols = st.number_input("Number of Columns:", value=3, min_value=1, max_value=6, help="How many lots per row")
                
            with col2:
                st.markdown("**Default Lot Dimensions:**")
                default_lot_width = st.number_input("Default Lot Width (ft):", value=60.0, min_value=40.0, max_value=100.0)
                default_lot_depth = st.number_input("Default Lot Depth (ft):", value=100.0, min_value=80.0, max_value=150.0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                show_buildings = st.checkbox("Show Buildings", value=True, help="Include building footprints on lots")
            with col2:
                show_dimensions = st.checkbox("Show Dimensions", value=True, help="Add dimension annotations")
            with col3:
                compact_layout = st.checkbox("Compact Layout", value=False, help="Tighter spacing between elements")
        
        st.markdown("---")
        
        # Subdivision settings
        col1, col2, col3 = st.columns(3)
        
        with col1:
            street_name = st.text_input("Street Name:", value="MAIN STREET")
        
        with col2:
            street_width = st.number_input("Street Width (ft):", value=30.0, min_value=20.0, max_value=50.0)
        
        with col3:
            sidewalk_width = st.number_input("Sidewalk Width (ft):", value=5.0, min_value=4.0, max_value=8.0)
        
        st.markdown("---")
        
        # Get sample data
        sample_lots = get_sample_subdivision_lots()
        df = pd.DataFrame(sample_lots)
        
        # Editable lot table
        st.subheader("📋 Edit Lot Parameters")
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "lot_number": st.column_config.TextColumn("Lot #", required=True),
                "address": st.column_config.TextColumn("Address", required=True),
                "width": st.column_config.NumberColumn("Width (ft)", required=True, format="%.1f"),
                "depth": st.column_config.NumberColumn("Depth (ft)", required=True, format="%.1f"),
                "building_sf": st.column_config.NumberColumn("Building SF", required=True, format="%d"),
                "setback_front": st.column_config.NumberColumn("Front Setback", required=True, format="%.1f"),
                "setback_rear": st.column_config.NumberColumn("Rear Setback", required=True, format="%.1f"),
            },
            key="subdivision_lots_editor"
        )
        
        lot_data = edited_df.to_dict('records')
        
        # Additional features checkboxes
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            include_driveways = st.checkbox("🚗 Add Driveways", value=True)
        with col2:
            include_trees = st.checkbox("🌳 Add Trees", value=True)
        with col3:
            include_easements = st.checkbox("⚡ Utility Easements", value=True)
        with col4:
            include_sidewalks = st.checkbox("🚶 Sidewalks", value=True)
        
        # Build subdivision data structure
        subdivision_data = {
            "lots": lot_data,
            "street_name": street_name,
            "street_width": street_width,
            "sidewalk_width": sidewalk_width,
            "include_driveways": include_driveways,
            "include_trees": include_trees,
            "include_easements": include_easements,
            "include_sidewalks": include_sidewalks,
            "show_buildings": show_buildings,
            "show_dimensions": show_dimensions,
            "compact_layout": compact_layout,
            "num_rows": num_rows,
            "num_cols": num_cols,
            "default_lot_width": default_lot_width,
            "default_lot_depth": default_lot_depth
        }
        
    else:  # Upload CSV
        uploaded_file = st.file_uploader(
            "📁 Upload Lot Data CSV (lot_number,address,width,depth,building_sf,setback_front,setback_rear)", 
            type=['csv'],
            help="CSV format: lot_number,address,width,depth,building_sf,setback_front,setback_rear"
        )
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded: {uploaded_file.name}")
            
            required_cols = ["lot_number", "address", "width", "depth", "building_sf", "setback_front", "setback_rear"]
            if all(col in df.columns for col in required_cols):
                lot_data = df.to_dict('records')
                st.dataframe(df, use_container_width=True)
                
                subdivision_data = {
                    "lots": lot_data,
                    "street_name": "MAIN STREET",
                    "street_width": 30.0,
                    "sidewalk_width": 5.0,
                    "include_driveways": True,
                    "include_trees": True,
                    "include_easements": True,
                    "include_sidewalks": True
                }
            else:
                st.error(f"⚠️ CSV must have columns: {', '.join(required_cols)}")
                return
        else:
            st.info("👆 Upload a lot data CSV file to begin")
            return
    
    if not lot_data:
        return
    
    st.markdown("---")
    
    # Subdivision metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Total Lots", len(lot_data))
    
    with col2:
        total_sf = sum(lot['building_sf'] for lot in lot_data)
        st.metric("🏗️ Total Building SF", f"{total_sf:,}")
    
    with col3:
        total_acreage = sum(lot['width'] * lot['depth'] for lot in lot_data) / 43560
        st.metric("📏 Total Acreage", f"{total_acreage:.2f}")
    
    with col4:
        avg_lot_size = sum(lot['width'] * lot['depth'] for lot in lot_data) / len(lot_data)
        st.metric("📊 Avg Lot Size", f"{avg_lot_size:,.0f} SF")
    
    st.markdown("---")
    
    # Layer summary
    st.subheader("🗂️ Professional Layer Structure (15 Layers!)")
    
    layers_info = [
        {"Layer": "PROP-BOUNDARY", "Description": "Property boundary", "Color": "Red"},
        {"Layer": "LOTS", "Description": "Individual lot lines", "Color": "Cyan"},
        {"Layer": "LOT-LABELS", "Description": "Lot numbers & addresses", "Color": "Yellow"},
        {"Layer": "STREET-CL", "Description": "Street centerline", "Color": "White"},
        {"Layer": "STREET-EDGE", "Description": "Street edges", "Color": "Magenta"},
        {"Layer": "STREET-LABELS", "Description": "Street names", "Color": "Yellow"},
        {"Layer": "BUILDINGS", "Description": "Building footprints", "Color": "Green"},
        {"Layer": "BLDG-LABELS", "Description": "Building SF labels", "Color": "White"},
        {"Layer": "SIDEWALK", "Description": "Sidewalk edges", "Color": "Gray"},
        {"Layer": "DRIVEWAYS", "Description": "Driveway access", "Color": "Blue"},
        {"Layer": "LANDSCAPE", "Description": "Trees & plantings", "Color": "Dark Green"},
        {"Layer": "EASEMENTS", "Description": "Utility easements", "Color": "Orange"},
        {"Layer": "TITLE-BLOCK", "Description": "Title block frame", "Color": "White"},
        {"Layer": "TITLE-TEXT", "Description": "Project information", "Color": "Yellow"},
        {"Layer": "DIMENSIONS", "Description": "Lot dimensions", "Color": "Cyan"},
    ]
    
    layers_df = pd.DataFrame(layers_info)
    st.dataframe(layers_df, use_container_width=True)
    
    st.markdown("---")
    
    # EXPORT BUTTON
    if st.button("Generate Subdivision DXF", type="primary", use_container_width=True):
        with st.spinner("Generating subdivision layout..."):
            generator = SubdivisionGenerator()
            dxf_content, filename = generator.generate_dxf(subdivision_data)
            
            st.success(f"Subdivision generated successfully with {len(lot_data)} lots, buildings, streets, and utilities.")
            
            st.download_button(
                label="Download Subdivision DXF",
                data=dxf_content,
                file_name=filename,
                mime="application/dxf",
                type="primary",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Visualization
    st.subheader("Subdivision Visualization")
    
    if subdivision_data:
        visualizer = CADVisualizer()
        fig = visualizer.plot_subdivision(subdivision_data)
        st.pyplot(fig)
    
    with st.expander("Technical Details"):
        st.markdown("""
        **Complete Residential Subdivision Generation:**
        
        This tool generates professional subdivision plans with comprehensive layer organization.
        
        **What Gets Generated:**
        
        1. **Property & Lots** (3 layers)
           - Overall property boundary with bearing/distance labels
           - Individual lot lines (60' × 100' typical)
           - Lot numbers and street addresses
        
        2. **Street Network** (3 layers)
           - Street centerlines with station markers
           - Street edge lines (pavement limits)
           - Street name labels (ROMANS font)
        
        3. **Buildings** (2 layers)
           - Building footprints based on lot size and setbacks
           - Square footage labels for each building
           - Automatic placement within setback zones
        
        4. **Infrastructure** (4 layers)
           - Sidewalks along street frontage
           - Driveway access from street to building
           - Landscape elements (trees, plantings)
           - Utility easements (10' typical along rear lot lines)
        
        5. **Title Block** (3 layers)
           - Professional title block with project info
           - Total acreage calculation
           - Layer legend and scale information
        
        **Smart Calculations:**
        - **Lot Acreage**: (Width × Depth) / 43,560
        - **Building Placement**: Respects front/rear/side setbacks
        - **Utility Easements**: Automatic 10' along rear property lines
        - **Street Geometry**: Centerline offsets, edge delineation
        
        **Generic CAD Standards (Not Tied to AutoCAD!):**
        - Universal layer naming (LOTS, BUILDINGS, STREET-CL, etc.)
        - Standard AutoCAD colors (1-255) for compatibility
        - Pure DXF entities (no proprietary Civil 3D objects)
        - Works with BricsCAD, DraftSight, FreeCAD, any DXF viewer
        
        **Benefits of Python Automation:**
        - **Speed**: Generate complete subdivisions quickly
        - **Automation**: Create multiple subdivision layouts easily
        - **Flexibility**: Customize lot sizes, setbacks, and streets instantly
        - **Intelligence**: Automatic calculations for acreage, building placement, and easements
        - **Scalability**: Batch process multiple projects programmatically
        """)
