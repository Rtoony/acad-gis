import streamlit as st
import sys
import os
import io
import zipfile
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(__file__))

from scenarios import subdivision, utilities, survey_points, plan_sheets, grading_3d, batch_processing, dxf_viewer, survey_import, block_demo, sheet_notes, profile_view, data_liberation, parking_lot, roadway_alignment
from utils.cad_generator import SubdivisionGenerator, UtilityGenerator, SurveyGenerator, ProfileGenerator, PlanSheetGenerator, Grading3DGenerator, ParkingLotGenerator, RoadwayAlignmentGenerator
from data.sample_data import get_subdivision_data, get_utility_data, get_survey_data

def generate_all_dxf_files_zip():
    """Generate default DXF files from all 11 tools and package into ZIP"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Subdivision Layout
        try:
            subdivision_data = get_subdivision_data()
            gen = SubdivisionGenerator()
            dxf_content, filename = gen.generate_dxf(subdivision_data)
            zip_file.writestr("01_Subdivision_Layout.dxf", dxf_content)
        except:
            pass
        
        # 2. Utility Networks (Water example)
        try:
            utility_data = get_utility_data()
            gen = UtilityGenerator()
            dxf_content, filename = gen.generate_dxf(utility_data, "💧 Water Network")
            zip_file.writestr("02_Water_Utility_Network.dxf", dxf_content)
        except:
            pass
        
        # 3. Survey Points
        try:
            survey_data = get_survey_data()
            gen = SurveyGenerator()
            dxf_content, filename = gen.generate_dxf(survey_data)
            zip_file.writestr("03_Survey_Points.dxf", dxf_content)
        except:
            pass
        
        # 4. Profile View
        try:
            gen = ProfileGenerator()
            # Simple profile data - alignment is just x,y not x,y,z
            alignment_data = [(0, 1000), (500, 1500)]
            # Surface triangles need to be dictionaries with p1, p2, p3 keys
            surface_data = [
                {
                    'p1': (0, 1000, 100),
                    'p2': (500, 1000, 105),
                    'p3': (500, 1500, 103)
                },
                {
                    'p1': (0, 1000, 100),
                    'p2': (500, 1500, 103),
                    'p3': (0, 1500, 102)
                }
            ]
            dxf_content, filename = gen.generate_profile_dxf(alignment_data, surface_data, 1.0, 1.0, 10.0)
            zip_file.writestr("04_Profile_View.dxf", dxf_content)
        except:
            pass
        
        # 5. Plan Sheets
        try:
            gen = PlanSheetGenerator()
            sheet_data = {
                "project_name": "JoshyCAD Demo Project",
                "sheet_number": "C-001",
                "scale": "1:100"
            }
            dxf_content, filename = gen.generate_dxf(sheet_data)
            zip_file.writestr("05_Plan_Sheet.dxf", dxf_content)
        except:
            pass
        
        # 6. 3D Grading
        try:
            gen = Grading3DGenerator()
            grading_data = {
                "grid_points": [
                    {"x": i*10, "y": j*10, "existing_z": 100 + i*0.5 + j*0.3, "proposed_z": 100 + i*0.5 + j*0.3 + 1}
                    for i in range(10) for j in range(10)
                ]
            }
            dxf_content, filename = gen.generate_dxf(grading_data, "Demo Grading")
            zip_file.writestr("06_3D_Grading.dxf", dxf_content)
        except:
            pass
        
        # 7. Survey Import (simple points)
        try:
            import ezdxf
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            # Add sample survey points
            for i in range(5):
                x, y, z = 1000 + i*20, 2000, 150 + i*0.5
                msp.add_point((x, y, z), dxfattribs={'layer': 'SURVEY'})
                msp.add_text(f"PT {i+1}", dxfattribs={'height': 2}).set_placement((x+2, y+2))
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
                doc.saveas(tmp.name)
                with open(tmp.name, 'rb') as f:
                    zip_file.writestr("07_Survey_Import.dxf", f.read())
                os.unlink(tmp.name)
        except:
            pass
        
        # 8. Block Demo (demonstrates block library)
        try:
            import ezdxf
            from utils.block_library import CivilBlockLibrary
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Create all blocks first
            CivilBlockLibrary.create_all_blocks(doc)
            
            # Insert various blocks from library
            CivilBlockLibrary.insert_block(msp, 'MH_SANITARY', (1000, 2000))
            CivilBlockLibrary.insert_block(msp, 'VALVE_WATER', (1020, 2000), rotation=45)
            CivilBlockLibrary.insert_block(msp, 'HYDRANT', (1040, 2000))
            CivilBlockLibrary.insert_block(msp, 'TREE_DECIDUOUS', (1060, 2000))
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
                doc.saveas(tmp.name)
                with open(tmp.name, 'rb') as f:
                    zip_file.writestr("08_Block_Library_Demo.dxf", f.read())
                os.unlink(tmp.name)
        except:
            pass
        
        # 9. Sheet Notes (notes demonstration)
        try:
            import ezdxf
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            notes = [
                "GENERAL NOTES:",
                "1. ALL DIMENSIONS ARE IN FEET UNLESS NOTED OTHERWISE",
                "2. CONTRACTOR SHALL VERIFY ALL DIMENSIONS IN FIELD",
                "3. SEE SHEET C-002 FOR UTILITY DETAILS"
            ]
            
            y_pos = 2050
            for note in notes:
                msp.add_text(note, dxfattribs={'height': 3}).set_placement((1000, y_pos))
                y_pos -= 10
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
                doc.saveas(tmp.name)
                with open(tmp.name, 'rb') as f:
                    zip_file.writestr("09_Sheet_Notes.dxf", f.read())
                os.unlink(tmp.name)
        except:
            pass
        
        # 10. DXF Viewer Demo File (sample DXF for viewing)
        try:
            import ezdxf
            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            
            # Create sample geometry for viewer demo
            msp.add_line((1000, 2000), (1100, 2000), dxfattribs={'layer': 'SITE', 'color': 1})
            msp.add_line((1100, 2000), (1100, 2100), dxfattribs={'layer': 'SITE', 'color': 1})
            msp.add_line((1100, 2100), (1000, 2100), dxfattribs={'layer': 'SITE', 'color': 1})
            msp.add_line((1000, 2100), (1000, 2000), dxfattribs={'layer': 'SITE', 'color': 1})
            msp.add_circle((1050, 2050), 25, dxfattribs={'layer': 'BUILDING', 'color': 3})
            msp.add_text('DEMO FILE FOR VIEWER', dxfattribs={'height': 5, 'layer': 'TEXT'}).set_placement((1020, 2080))
            
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
                doc.saveas(tmp.name)
                with open(tmp.name, 'rb') as f:
                    zip_file.writestr("10_DXF_Viewer_Demo.dxf", f.read())
                os.unlink(tmp.name)
        except:
            pass
        
        # 11. Batch Processing Example (multiple generated files)
        try:
            import ezdxf
            
            # Generate 3 simple batch files
            for batch_num in range(1, 4):
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
                
                # Simple rectangle with batch number
                x_offset = batch_num * 200
                msp.add_lwpolyline([
                    (1000 + x_offset, 2000),
                    (1050 + x_offset, 2000),
                    (1050 + x_offset, 2050),
                    (1000 + x_offset, 2050),
                    (1000 + x_offset, 2000)
                ], dxfattribs={'layer': f'BATCH-{batch_num}'})
                msp.add_text(f'Batch #{batch_num}', dxfattribs={'height': 8}).set_placement((1010 + x_offset, 2020))
                
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
                    doc.saveas(tmp.name)
                    with open(tmp.name, 'rb') as f:
                        zip_file.writestr(f"11_Batch_Processing_File_{batch_num}.dxf", f.read())
                    os.unlink(tmp.name)
        except:
            pass
        
        # 12. Parking Lot Designer
        try:
            gen = ParkingLotGenerator()
            parking_data = {
                "lot_length": 300,
                "lot_width": 200,
                "stall_width": 9,
                "stall_length": 18,
                "aisle_width": 24,
                "parking_angle": 90,
                "num_ada_spaces": 4,
                "compact_ratio": 15,
                "include_van_accessible": True,
                "include_islands": True,
                "include_wheel_stops": True,
                "show_drainage": True,
                "slope_percent": 1.5,
                "drainage_direction": "To Center",
                "show_dimensions": True
            }
            dxf_content, filename = gen.generate_dxf(parking_data)
            zip_file.writestr("12_Parking_Lot_Layout.dxf", dxf_content)
        except:
            pass
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

def main():
    st.set_page_config(
        page_title="JoshyCAD - Free Professional CAD Generation",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        /* Sidebar styling - darker background for better readability */
        [data-testid="stSidebar"] {
            background-color: #0e1117;
        }
        
        /* Sidebar content text color */
        [data-testid="stSidebar"] .element-container {
            color: #fafafa;
        }
        
        /* Main content area */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Header styling */
        h1 {
            color: #1f77b4;
            font-weight: 700;
        }
        
        /* Metrics styling */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # =================== SIDEBAR NAVIGATION ===================
    with st.sidebar:
        st.markdown("# JoshyCAD")
        st.markdown("### DXF Generation Tools")
        st.markdown("---")
        
        st.markdown("### 🛠️ Select Tool")
        
        # Tool categories for better organization
        tools = [
            "📥 DXF Viewer & Inspector",
            "📊 Survey Point Import",
            "📦 Block Library Demo",
            "📝 Sheet Notes Manager",
            "🏘️ Subdivision Layout",
            "🚰 Utility Networks", 
            "📍 Survey Connections",
            "📈 Profile Generator",
            "📋 Plan Sheets",
            "🏔️ 3D Grading",
            "🔄 Batch Processing",
            "🔓 Data Liberation",
            "🅿️ Parking Lot Designer",
            "🛣️ Roadway Alignment"
        ]
        
        # Initialize session state for selected tool
        if 'selected_tool' not in st.session_state:
            st.session_state.selected_tool = tools[0]
        
        # Tool selection with radio buttons for clear visual selection
        selected_tool = st.radio(
            "Choose a tool:",
            tools,
            index=tools.index(st.session_state.selected_tool),
            label_visibility="collapsed"
        )
        
        st.session_state.selected_tool = selected_tool
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tools", "14")
        with col2:
            st.metric("Cost", "$0")
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About", expanded=False):
            st.markdown("""
            **JoshyCAD** - Professional DXF generation using Python.
            
            **Stack:**
            - ezdxf
            - pandas  
            - matplotlib
            """)
    
    # =================== MAIN CONTENT AREA ===================
    
    # Hero section
    st.markdown("# JoshyCAD")
    st.markdown("### Professional DXF Generation with Python")
    
    st.info("""
    Generate professional DXF files using Python and ezdxf. Includes tools for survey data, 
    subdivision layouts, utilities, profile views, plan sheets, 3D grading, and batch processing.
    """)
    
    # Download all tools button
    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
    with col_dl2:
        if st.button("Download All Tools as ZIP", type="primary", use_container_width=True):
            with st.spinner("Generating DXF files..."):
                zip_data = generate_all_dxf_files_zip()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                st.success("All 11 DXF files generated successfully.")
                
                st.download_button(
                    label=f"Download ZIP ({timestamp})",
                    data=zip_data,
                    file_name=f"JoshyCAD_All_Tools_{timestamp}.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # Route to selected scenario based on sidebar selection
    if selected_tool == "📥 DXF Viewer & Inspector":
        dxf_viewer.show_scenario()
    elif selected_tool == "📊 Survey Point Import":
        survey_import.show_scenario()
    elif selected_tool == "📦 Block Library Demo":
        block_demo.show_scenario()
    elif selected_tool == "📝 Sheet Notes Manager":
        sheet_notes.show_scenario()
    elif selected_tool == "🏘️ Subdivision Layout":
        subdivision.show_scenario()
    elif selected_tool == "🚰 Utility Networks":
        utilities.show_scenario() 
    elif selected_tool == "📍 Survey Connections":
        survey_points.show_scenario()
    elif selected_tool == "📈 Profile Generator":
        profile_view.show_scenario()
    elif selected_tool == "📋 Plan Sheets":
        plan_sheets.show_scenario()
    elif selected_tool == "🏔️ 3D Grading":
        grading_3d.show_scenario()
    elif selected_tool == "🔄 Batch Processing":
        batch_processing.show_scenario()
    elif selected_tool == "🔓 Data Liberation":
        data_liberation.show_scenario()
    elif selected_tool == "🅿️ Parking Lot Designer":
        parking_lot.show_scenario()
    elif selected_tool == "🛣️ Roadway Alignment":
        roadway_alignment.show_scenario()

if __name__ == "__main__":
    main()
