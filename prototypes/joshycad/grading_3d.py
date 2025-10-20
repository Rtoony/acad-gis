import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from utils.cad_generator import Grading3DGenerator
from utils.visualizer import CADVisualizer
from data.sample_data import get_grading_data

def show_scenario():
    st.header("🏔️ 3D Grading & Earthwork Visualization")
    st.markdown("""
    Generate 3D grading surfaces and calculate earthwork volumes. This demonstrates how to create
    3D terrain models, proposed grading surfaces, and visualize cut/fill areas.
    """)
    
    # Advanced 3D Display Options
    with st.expander("⚙️ 3D Display & Analysis Options", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Surface Display:**")
            surface_resolution = st.selectbox("Grid Resolution:", ["Coarse (10ft)", "Medium (5ft)", "Fine (2ft)"], index=1)
            show_contours = st.checkbox("Show Contours", value=True)
            contour_interval = st.number_input("Contour Interval (ft):", 1.0, 10.0, 2.0, 0.5)
        
        with col2:
            st.markdown("**Cut/Fill Analysis:**")
            show_cutfill = st.checkbox("Show Cut/Fill Colors", value=True)
            volume_method = st.selectbox("Volume Method:", ["Grid Method", "Average End Area", "Prismoidal"])
        
        with col3:
            st.markdown("**Visualization:**")
            vertical_exaggeration = st.slider("Vertical Exaggeration:", 1.0, 5.0, 1.5, 0.5)
            view_angle = st.selectbox("View Angle:", ["Isometric", "Top", "Side", "Custom"])
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Grading Configuration")
        
        # Grading type selection
        grading_type = st.selectbox(
            "Select grading type:",
            ["Building Pad", "Road Grading", "Site Grading", "Detention Basin"]
        )
        
        # Data source
        data_source = st.radio(
            "Data source:",
            ["Sample Grading Data", "Upload Survey Points"]
        )
        
        if data_source == "Sample Grading Data":
            grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
        else:
            st.info("📋 CSV Format: Upload a file with columns: x, y, existing_z, proposed_z (and optional point_id)")
            st.warning("⚠️ Data must form a regular grid with uniform spacing (e.g., every 10ft × 10ft)")
            
            uploaded_file = st.file_uploader("Upload grading points CSV", type=['csv'])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Validate required columns
                    required_cols = ['x', 'y', 'existing_z', 'proposed_z']
                    if not all(col in df.columns for col in required_cols):
                        st.error(f"❌ CSV must contain columns: {', '.join(required_cols)}")
                        grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                        st.info("Using sample data instead")
                    else:
                        # Convert DataFrame to grid format
                        x_vals = sorted(df['x'].unique())
                        y_vals = sorted(df['y'].unique())
                        
                        # Validate uniform grid spacing
                        def check_uniform(vals, name):
                            if len(vals) < 2:
                                return True, 0
                            diffs = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
                            avg_diff = np.mean(diffs)
                            if any(abs(d - avg_diff) > avg_diff * 0.1 for d in diffs):  # 10% tolerance
                                return False, 0
                            return True, avg_diff
                        
                        x_uniform, dx = check_uniform(x_vals, 'x')
                        y_uniform, dy = check_uniform(y_vals, 'y')
                        
                        if not x_uniform or not y_uniform:
                            st.error("❌ Grid spacing is not uniform. Data must be on a regular grid.")
                            st.info("Example: points at (0,0), (10,0), (20,0), (0,10), (10,10), (20,10) etc.")
                            grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                            st.info("Using sample data instead")
                        else:
                            # Check for complete grid
                            expected_points = len(x_vals) * len(y_vals)
                            if len(df) < expected_points:
                                st.error(f"❌ Incomplete grid: expected {expected_points} points but got {len(df)}")
                                st.info("Every X/Y combination must have a data point")
                                grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                                st.info("Using sample data instead")
                            else:
                                # Create meshgrid
                                X, Y = np.meshgrid(x_vals, y_vals)
                                
                                # Build Z matrices - validate no missing data
                                Z_existing = np.full_like(X, np.nan, dtype=float)
                                Z_proposed = np.full_like(X, np.nan, dtype=float)
                                
                                for _, row in df.iterrows():
                                    try:
                                        i = list(x_vals).index(row['x'])
                                        j = list(y_vals).index(row['y'])
                                        Z_existing[j, i] = row['existing_z']
                                        Z_proposed[j, i] = row['proposed_z']
                                    except (ValueError, IndexError):
                                        continue
                                
                                # Check for missing data
                                if np.any(np.isnan(Z_existing)) or np.any(np.isnan(Z_proposed)):
                                    st.error("❌ Missing elevation data for some grid points")
                                    grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                                    st.info("Using sample data instead")
                                else:
                                    # Build grid_points
                                    grid_points = []
                                    for i, x in enumerate(x_vals):
                                        for j, y in enumerate(y_vals):
                                            # Handle optional point_id column
                                            if 'point_id' in df.columns:
                                                point_id_vals = df[((df['x'] == x) & (df['y'] == y))]['point_id'].values
                                                pid = point_id_vals[0] if len(point_id_vals) > 0 else f"P{i}{j}"
                                            else:
                                                pid = f"P{i}{j}"
                                            
                                            grid_points.append({
                                                "x": x,
                                                "y": y,
                                                "existing_z": Z_existing[j, i],
                                                "proposed_z": Z_proposed[j, i],
                                                "point_id": pid
                                            })
                                    
                                    # Calculate cell area from actual spacing
                                    cell_area = dx * dy if dx > 0 and dy > 0 else 100
                                    
                                    grading_data = {
                                        "grid_points": grid_points,
                                        "cell_area": cell_area,
                                        "x_grid": X.tolist(),
                                        "y_grid": Y.tolist(),
                                        "z_existing": Z_existing.tolist(),
                                        "z_proposed": Z_proposed.tolist()
                                    }
                                    
                                    st.success(f"✅ Loaded {len(grid_points)} grid points ({len(x_vals)} × {len(y_vals)}) with {cell_area:.1f} sq ft cells")
                        
                except Exception as e:
                    st.error(f"❌ Error processing CSV: {str(e)}")
                    grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                    st.info("Using sample data instead")
            else:
                grading_data = get_grading_data(grading_type.lower().replace(" ", "_"))
                st.info("Using sample data")
        
        # Grading parameters
        st.subheader("⚙️ Grading Parameters")
        
        if grading_type == "Building Pad":
            target_elevation = st.number_input("Target Pad Elevation (ft):", value=100.0, step=0.5)
            side_slope = st.selectbox("Side Slope Ratio:", ["2:1", "3:1", "4:1"], index=1)
            grading_data["target_elevation"] = target_elevation
            grading_data["side_slope"] = side_slope
        
        elif grading_type == "Road Grading":
            crown_height = st.number_input("Crown Height (ft):", value=0.2, step=0.05)
            cross_slope = st.number_input("Cross Slope (%):", value=2.0, step=0.5)
            grading_data["crown_height"] = crown_height
            grading_data["cross_slope"] = cross_slope
        
        # Display grid info
        if grading_data and "grid_points" in grading_data:
            st.subheader("📋 Grid Information")
            grid_points = grading_data["grid_points"]
            st.metric("Grid Points", len(grid_points))
            
            elevations = [pt["existing_z"] for pt in grid_points]
            st.metric("Elevation Range", f"{min(elevations):.1f} - {max(elevations):.1f} ft")
    
    with col2:
        with st.expander("🐍 Show Python Code", expanded=False):
            st.subheader("🐍 Generated Python Code")
            
            generator = Grading3DGenerator()
            code = generator.generate_code(grading_data, grading_type)
            
            st.code(code, language="python")
        
        # Generate DXF with 3D data
        if st.button("🔧 Generate 3D Grading DXF", type="primary"):
            with st.spinner("Generating 3D grading model..."):
                dxf_content, filename = generator.generate_dxf(grading_data, grading_type)
                
                st.download_button(
                    label="📥 Download 3D Grading DXF",
                    data=dxf_content,
                    file_name=filename,
                    mime="application/dxf"
                )
                
                st.success(f"✅ Generated {filename}")
    
    # 3D Visualization
    st.subheader("👁️ 3D Surface Visualization")
    
    if grading_data:
        visualizer = CADVisualizer()
        fig = visualizer.plot_3d_grading(grading_data, grading_type)
        st.pyplot(fig)
        
        # Earthwork calculations
        st.subheader("📊 Earthwork Quantities")
        
        if "grid_points" in grading_data:
            grid_points = grading_data["grid_points"]
            
            # Calculate cut/fill volumes properly by computing average height per cell
            # Get unique x and y coordinates to determine grid
            x_coords = sorted(set(pt['x'] for pt in grid_points))
            y_coords = sorted(set(pt['y'] for pt in grid_points))
            
            cell_area = grading_data.get("cell_area", 100)  # sq ft
            total_cut_volume = 0
            total_fill_volume = 0
            
            # Calculate volume for each grid cell
            for i in range(len(x_coords) - 1):
                for j in range(len(y_coords) - 1):
                    # Get four corner points for this cell
                    pts_in_cell = [
                        pt for pt in grid_points
                        if x_coords[i] <= pt['x'] <= x_coords[i+1] 
                        and y_coords[j] <= pt['y'] <= y_coords[j+1]
                    ]
                    
                    if len(pts_in_cell) >= 4:
                        # Average height difference for this cell
                        avg_diff = sum(pt.get("proposed_z", pt["existing_z"]) - pt["existing_z"] 
                                     for pt in pts_in_cell) / len(pts_in_cell)
                        
                        # Volume for this cell
                        cell_volume = abs(avg_diff) * cell_area / 27  # cubic yards
                        
                        if avg_diff < 0:
                            total_cut_volume += cell_volume
                        else:
                            total_fill_volume += cell_volume
            
            cut_volume = total_cut_volume
            fill_volume = total_fill_volume
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Cut Volume", f"{cut_volume:.0f} CY", delta=f"-{cut_volume:.0f}")
            
            with col2:
                st.metric("Fill Volume", f"{fill_volume:.0f} CY", delta=f"+{fill_volume:.0f}")
            
            with col3:
                net_volume = fill_volume - cut_volume
                st.metric("Net Volume", f"{abs(net_volume):.0f} CY", 
                         delta="Import" if net_volume > 0 else "Export")
        
        # Technical details
        with st.expander("🔍 3D Grading Implementation Details"):
            st.markdown(f"""
            **{grading_type} Generation:**
            
            1. **3D Point Cloud**: Creates 3D points with X, Y, Z coordinates
            2. **Surface Meshing**: Generates triangulated irregular network (TIN) 
            3. **Existing vs Proposed**: Shows both existing ground and proposed surfaces
            4. **Cut/Fill Visualization**: Color-codes areas by cut (red) and fill (blue)
            5. **Contour Lines**: Generates elevation contours at specified intervals
            6. **Volume Calculations**: Computes earthwork quantities using grid method
            
            **3D ezdxf Features:**
            - `add_3dface()` - Create 3D triangular faces for terrain
            - `add_point()` - Add 3D survey points with elevation
            - `add_polyline()` - Create 3D contour lines
            - `dxfattribs={{'elevation': z}}` - Set Z-elevation for entities
            - Layer separation for existing vs proposed surfaces
            
            **Visualization Techniques:**
            - matplotlib 3D surface plots with colormap
            - Contour projections on base plane
            - Wireframe overlay for grid structure
            - Cut/fill color coding (red=cut, blue=fill)
            """)
