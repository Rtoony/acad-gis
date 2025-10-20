import streamlit as st
import pandas as pd
import ezdxf
from ezdxf import xref
import io
import tempfile
import os
from collections import defaultdict
from typing import Dict, Any
from utils.ai_query import AIQueryHelper

def show_scenario():
    st.header("📥 DXF Viewer & Inspector")
    
    # ============================================================================
    # TOP TOOLBAR - CAD STYLE
    # ============================================================================
    st.markdown("---")
    
    # Create top toolbar
    toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4 = st.columns([2, 1, 1, 1])
    
    with toolbar_col1:
        # File uploader in prominent position
        uploaded_file = st.file_uploader(
            "Upload DXF File",
            type=['dxf'],
            label_visibility="collapsed",
            key="dxf_upload"
        )
    
    with toolbar_col2:
        show_entities = st.checkbox("Show Entities", value=True)
    
    with toolbar_col3:
        show_stats = st.checkbox("Show Stats", value=True)
    
    with toolbar_col4:
        show_preview = st.checkbox("Show Preview", value=False)
    
    st.markdown("---")
    
    # ============================================================================
    # MAIN DISPLAY AREA
    # ============================================================================
    
    if uploaded_file is not None:
        try:
            # Write uploaded file to temporary file and read with ezdxf
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name
            
            try:
                doc = ezdxf.readfile(tmp_path)
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
            st.success(f"✅ Loaded: {uploaded_file.name}")
            
            # Get modelspace
            msp = doc.modelspace()
            
            # ============================================================================
            # AI QUERY SECTION
            # ============================================================================
            
            st.markdown("---")
            st.subheader("🤖 Ask AI About This DXF File")
            
            # Build comprehensive data summary for AI
            dxf_summary = {
                "filename": uploaded_file.name,
                "version": doc.acad_release,
                "total_layers": len(list(doc.layers)),
                "total_entities": len(list(msp)),
                "layer_details": []
            }
            
            # Collect detailed layer info for AI
            temp_layer_info = {}
            for entity in msp:
                layer_name = entity.dxf.layer if hasattr(entity.dxf, 'layer') else "0"
                entity_type = entity.dxftype()
                
                if layer_name not in temp_layer_info:
                    temp_layer_info[layer_name] = {"count": 0, "types": {}}
                
                temp_layer_info[layer_name]["count"] += 1
                
                if entity_type not in temp_layer_info[layer_name]["types"]:
                    temp_layer_info[layer_name]["types"][entity_type] = 0
                temp_layer_info[layer_name]["types"][entity_type] += 1
            
            # Add to summary
            for layer_name, info in temp_layer_info.items():
                dxf_summary["layer_details"].append({
                    "layer": layer_name,
                    "entity_count": info["count"],
                    "entity_types": list(info["types"].keys())
                })
            
            # AI Query Interface
            ai_helper = AIQueryHelper()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                query = st.text_input(
                    "Ask a question about this DXF file:",
                    placeholder="e.g., What layers contain survey data? How many line entities are there?",
                    key="dxf_ai_query"
                )
            
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                ask_button = st.button("🔍 Ask AI", type="primary", use_container_width=True)
            
            if ask_button and query:
                with st.spinner("🤖 AI analyzing DXF structure..."):
                    response = ai_helper.interpret_query(query, dxf_summary, "dxf_viewer")
                    if response and "error" not in response:
                        st.success("✅ AI Response:")
                        st.markdown(response.get("explanation", "No explanation provided."))
                    elif "error" in response:
                        st.error(f"❌ Error: {response['error']}")
                    else:
                        st.error("❌ Could not get AI response. Please check your OpenAI API key.")
            
            st.markdown("💡 **Example questions:** *What's the largest layer by entity count? Which layers have circles? Summarize this drawing's contents.*")
            
            # ============================================================================
            # ANALYZE DXF CONTENT
            # ============================================================================
            
            # Collect layer information
            layer_info: Dict[str, Dict[str, Any]] = {}
            
            for entity in msp:
                layer_name = entity.dxf.layer if hasattr(entity.dxf, 'layer') else "0"
                entity_type = entity.dxftype()
                
                if layer_name not in layer_info:
                    layer_info[layer_name] = {"count": 0, "types": {}, "entities": []}
                
                layer_info[layer_name]["count"] += 1
                
                if entity_type not in layer_info[layer_name]["types"]:
                    layer_info[layer_name]["types"][entity_type] = 0
                layer_info[layer_name]["types"][entity_type] += 1
                
                layer_info[layer_name]["entities"].append(entity)
            
            # Get layer definitions
            layer_definitions = {}
            for layer in doc.layers:
                layer_definitions[layer.dxf.name] = {
                    "color": layer.dxf.color if hasattr(layer.dxf, 'color') else 7,
                    "linetype": layer.dxf.linetype if hasattr(layer.dxf, 'linetype') else "CONTINUOUS",
                    "on": layer.is_on(),
                    "frozen": layer.is_frozen()
                }
            
            # ============================================================================
            # DISPLAY STATISTICS
            # ============================================================================
            
            if show_stats:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Layers", len(layer_info))
                
                with col2:
                    total_entities = sum(info["count"] for info in layer_info.values())
                    st.metric("Total Entities", f"{total_entities:,}")
                
                with col3:
                    all_types = set()
                    for info in layer_info.values():
                        all_types.update(info["types"].keys())
                    st.metric("Entity Types", len(all_types))
                
                with col4:
                    st.metric("DXF Version", doc.acad_release)
            
            st.markdown("---")
            
            # ============================================================================
            # LAYER FILTERING & EXPORT
            # ============================================================================
            
            st.subheader("🎨 Layer Selection & Export")
            
            # Create layer selection interface
            layer_df_data = []
            for layer_name, info in sorted(layer_info.items()):
                layer_def = layer_definitions.get(layer_name, {})
                layer_df_data.append({
                    "Layer": layer_name,
                    "Entities": info["count"],
                    "Color": layer_def.get("color", 7),
                    "Linetype": layer_def.get("linetype", "CONTINUOUS"),
                    "Status": "ON" if layer_def.get("on", True) else "OFF"
                })
            
            layer_df = pd.DataFrame(layer_df_data)
            
            # Layer multiselect
            selected_layers = st.multiselect(
                "Select layers to export:",
                options=layer_df["Layer"].tolist(),
                default=layer_df["Layer"].tolist()[:5] if len(layer_df) > 5 else layer_df["Layer"].tolist(),
                help="Choose which layers to include in the exported DXF"
            )
            
            # Export button
            if selected_layers:
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    if st.button("🚀 EXPORT SELECTED LAYERS TO DXF", type="primary"):
                        # Create new DXF document using xref.Loader for proper dependency copying
                        new_doc = ezdxf.new(dxfversion=doc.acad_release)
                        
                        # Use ezdxf.xref.Loader to copy entities with all dependencies
                        loader = xref.Loader(doc, new_doc, conflict_policy=xref.ConflictPolicy.KEEP)
                        
                        # Load selected layers (this will automatically load dependencies)
                        loader.load_layers(selected_layers)
                        
                        # Load entities from modelspace that are on selected layers
                        # Filter function to only include entities on selected layers
                        def layer_filter(entity):
                            return entity.dxf.layer in selected_layers if hasattr(entity.dxf, 'layer') else False
                        
                        loader.load_modelspace(
                            target_layout=new_doc.modelspace(),
                            filter_fn=layer_filter
                        )
                        
                        # Execute the loader to complete the copy with all dependencies
                        loader.execute()
                        
                        # Count entities in the new document
                        entities_copied = len(list(new_doc.modelspace()))
                        
                        # Save to bytes using temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_export_file:
                            tmp_export_path = tmp_export_file.name
                        
                        try:
                            new_doc.saveas(tmp_export_path)
                            with open(tmp_export_path, 'rb') as f:
                                dxf_bytes_out = f.read()
                        finally:
                            if os.path.exists(tmp_export_path):
                                os.unlink(tmp_export_path)
                        
                        st.success(f"✅ Exported {entities_copied:,} entities from {len(selected_layers)} layers")
                        
                        # Download button
                        st.download_button(
                            label="💾 DOWNLOAD FILTERED DXF",
                            data=dxf_bytes_out,
                            file_name=f"{uploaded_file.name.replace('.dxf', '')}_filtered.dxf",
                            mime="application/dxf",
                            type="primary"
                        )
            
            # ============================================================================
            # ENTITY BREAKDOWN
            # ============================================================================
            
            if show_entities:
                st.markdown("---")
                st.subheader("📊 Layer & Entity Breakdown")
                
                # Display layer table
                st.dataframe(
                    layer_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Layer": st.column_config.TextColumn("Layer Name", width="medium"),
                        "Entities": st.column_config.NumberColumn("Count", format="%d"),
                        "Color": st.column_config.NumberColumn("ACI Color", format="%d"),
                        "Linetype": st.column_config.TextColumn("Linetype", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
                
                # Detailed entity breakdown by type
                with st.expander("🔍 Detailed Entity Type Breakdown"):
                    for layer_name in sorted(layer_info.keys()):
                        if layer_name in selected_layers:
                            st.markdown(f"**{layer_name}** ({layer_info[layer_name]['count']} entities)")
                            type_breakdown = layer_info[layer_name]["types"]
                            type_df = pd.DataFrame([
                                {"Entity Type": etype, "Count": count}
                                for etype, count in sorted(type_breakdown.items(), key=lambda x: x[1], reverse=True)
                            ])
                            st.dataframe(type_df, hide_index=True, use_container_width=True)
                            st.markdown("")
            
            # ============================================================================
            # VISUAL PREVIEW (Optional - Basic for now)
            # ============================================================================
            
            if show_preview:
                st.markdown("---")
                st.subheader("👁️ Visual Preview (Simple)")
                
                # Basic matplotlib preview
                import matplotlib.pyplot as plt
                import matplotlib.patches as mpatches
                from matplotlib.collections import LineCollection
                
                fig, ax = plt.subplots(figsize=(12, 10))
                fig.patch.set_facecolor('#1e1e1e')
                ax.set_facecolor('#1e1e1e')
                
                # Color mapping (simplified)
                aci_colors = {
                    1: 'red', 2: 'yellow', 3: 'green', 4: 'cyan', 5: 'blue',
                    6: 'magenta', 7: 'white', 8: 'gray', 9: 'lightgray'
                }
                
                # Draw entities from selected layers
                for layer_name in selected_layers:
                    layer_def = layer_definitions.get(layer_name, {})
                    color_idx = layer_def.get("color", 7)
                    color = aci_colors.get(color_idx, 'white')
                    
                    for entity in layer_info[layer_name]["entities"][:100]:  # Limit for performance
                        try:
                            if entity.dxftype() == 'LINE':
                                start = entity.dxf.start
                                end = entity.dxf.end
                                ax.plot([start.x, end.x], [start.y, end.y], color=color, linewidth=0.5, alpha=0.7)
                            
                            elif entity.dxftype() == 'LWPOLYLINE' or entity.dxftype() == 'POLYLINE':
                                points = list(entity.get_points())
                                if points:
                                    xs = [p[0] for p in points]
                                    ys = [p[1] for p in points]
                                    ax.plot(xs, ys, color=color, linewidth=0.5, alpha=0.7)
                            
                            elif entity.dxftype() == 'CIRCLE':
                                center = entity.dxf.center
                                radius = entity.dxf.radius
                                circle = mpatches.Circle((center.x, center.y), radius, fill=False, 
                                                        edgecolor=color, linewidth=0.5, alpha=0.7)
                                ax.add_patch(circle)
                        except:
                            pass
                
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.2, color='gray')
                ax.tick_params(colors='white')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['left'].set_color('white')
                ax.spines['right'].set_color('white')
                
                st.pyplot(fig)
                
                st.info("ℹ️ Preview shows first 100 entities per layer for performance. Download the DXF for full detail.")
        
        except Exception as e:
            st.error(f"❌ Error loading DXF file: {str(e)}")
            st.exception(e)
    
    else:
        # Instructions when no file uploaded
        st.info("📂 Upload a DXF file to view its contents and export filtered versions")
        
        st.markdown("""
        ### What This Tool Does:
        
        1. **📥 Upload** - Load any DXF file from your civil engineering projects
        2. **🔍 Inspect** - View all layers, entity counts, and layer properties
        3. **🎨 Filter** - Select specific layers you want to keep
        4. **📤 Export** - Download a new DXF with only your selected layers
        
        ### Use Cases:
        
        - **Clean up drawings** - Remove unnecessary layers before sharing
        - **Extract specific data** - Pull only survey points or utilities
        - **Analyze file structure** - Understand what's in complex DXF files
        - **Prepare for import** - Filter data before bringing into other tools
        
        ### Supported Files:
        
        - Any DXF version (R12 through latest)
        - Files from AutoCAD, Civil 3D, BricsCAD, etc.
        - Large files are supported (may take longer to process)
        """)
