import ezdxf
import numpy as np
import math
import io
from typing import Dict, List, Any

class CADGenerator:
    """Base class for CAD generation utilities"""
    
    def __init__(self):
        self.doc = None
        self.msp = None
    
    def create_document(self):
        """Create a new DXF document"""
        self.doc = ezdxf.new('R2010')
        self.msp = self.doc.modelspace()
        return self.doc, self.msp
    
    def create_layers(self, layer_specs: List[Dict]):
        """Create CAD layers with specified properties"""
        for spec in layer_specs:
            if not spec.get('name'):
                continue
            try:
                self.doc.layers.new(
                    name=spec['name'],
                    dxfattribs={
                        'color': spec.get('color', 7),
                        'linetype': spec.get('linetype', 'CONTINUOUS')
                    }
                )
            except Exception:
                pass
    
    def validate_coordinate(self, value: Any, default: float = 0.0) -> float:
        """Validate and convert coordinate value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def validate_point(self, point_dict: Dict, required_keys: List[str] = ['x', 'y']) -> bool:
        """Validate that a point dictionary has required coordinates"""
        if not point_dict or not isinstance(point_dict, dict):
            return False
        for key in required_keys:
            if key not in point_dict:
                return False
            if point_dict[key] is None:
                return False
            try:
                float(point_dict[key])
            except (ValueError, TypeError):
                return False
        return True
    
    def safe_get_coords(self, point_dict: Dict) -> tuple:
        """Safely extract x, y coordinates with validation"""
        x = self.validate_coordinate(point_dict.get('x', 0), 0.0)
        y = self.validate_coordinate(point_dict.get('y', 0), 0.0)
        return (x, y)
    
    def safe_get_coords_3d(self, point_dict: Dict) -> tuple:
        """Safely extract x, y, z coordinates with validation"""
        x = self.validate_coordinate(point_dict.get('x', 0), 0.0)
        y = self.validate_coordinate(point_dict.get('y', 0), 0.0)
        z = self.validate_coordinate(point_dict.get('z', 0), 0.0)
        return (x, y, z)
    
    def safe_get_field(self, obj: Dict, field: str, default: str = "") -> str:
        """Safely extract a text field from a dictionary"""
        try:
            value = obj.get(field, default)
            return str(value) if value is not None else default
        except:
            return default
    
    def validate_property_corner(self, corner: Dict) -> bool:
        """Validate a property corner has required fields"""
        if not isinstance(corner, dict):
            return False
        return self.validate_point(corner)
    
    def validate_structure(self, structure: Dict) -> bool:
        """Validate a structure dictionary has required fields"""
        if not isinstance(structure, dict):
            return False
        # Must have valid coordinates
        if not self.validate_point(structure):
            return False
        # Must have structure_id
        if 'structure_id' not in structure or not structure['structure_id']:
            return False
        return True
    
    def calculate_bearing_distance(self, pt1: tuple, pt2: tuple) -> tuple:
        """Calculate bearing and distance between two points"""
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate bearing in degrees
        angle_rad = math.atan2(dx, dy)
        bearing_deg = math.degrees(angle_rad)
        
        # Convert to surveyor's bearing format
        if bearing_deg < 0:
            bearing_deg += 360
            
        # Convert to quadrant bearing
        if 0 <= bearing_deg < 90:
            bearing = f"N {bearing_deg:.0f}° E"
        elif 90 <= bearing_deg < 180:
            bearing = f"S {180-bearing_deg:.0f}° E"
        elif 180 <= bearing_deg < 270:
            bearing = f"S {bearing_deg-180:.0f}° W"
        else:
            bearing = f"N {360-bearing_deg:.0f}° W"
            
        return bearing, distance
    
    def save_to_bytes(self) -> bytes:
        """Save DXF document to bytes"""
        stream = io.StringIO()
        self.doc.write(stream)
        return stream.getvalue().encode('utf-8')

class SubdivisionGenerator(CADGenerator):
    """Generate subdivision layouts with property lines and labels"""
    
    def generate_code(self, data: Dict) -> str:
        """Generate the Python code that creates the subdivision"""
        corners = data.get("property_corners", [])
        
        code = f'''import ezdxf
import math

# Create new DXF document
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Create layers
doc.layers.new('PROP', dxfattribs={{'color': 1}})  # Red for property lines
doc.layers.new('TEXT', dxfattribs={{'color': 3}})  # Green for text
doc.layers.new('BLDG', dxfattribs={{'color': 5}})  # Magenta for buildings

# Property corner coordinates
corners = {corners}

# Create property boundary
if len(corners) >= 3:
    # Create closed polyline for property boundary
    points = [(pt['x'], pt['y']) for pt in corners]
    points.append(points[0])  # Close the polygon
    
    msp.add_lwpolyline(
        points, 
        dxfattribs={{'layer': 'PROP'}}
    )
    
    # Add bearing and distance labels for each segment
    for i in range(len(corners)):
        pt1 = (corners[i]['x'], corners[i]['y'])
        pt2 = (corners[(i+1) % len(corners)]['x'], corners[(i+1) % len(corners)]['y'])
        
        # Calculate bearing and distance
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        angle_rad = math.atan2(dx, dy)
        bearing_deg = math.degrees(angle_rad)
        if bearing_deg < 0:
            bearing_deg += 360
            
        # Convert to quadrant bearing
        if 0 <= bearing_deg < 90:
            bearing = f"N {{bearing_deg:.0f}}° E"
        elif 90 <= bearing_deg < 180:
            bearing = f"S {{180-bearing_deg:.0f}}° E"
        elif 180 <= bearing_deg < 270:
            bearing = f"S {{bearing_deg-180:.0f}}° W"
        else:
            bearing = f"N {{360-bearing_deg:.0f}}° W"
        
        # Place label at midpoint of line
        mid_x = (pt1[0] + pt2[0]) / 2
        mid_y = (pt1[1] + pt2[1]) / 2
        
        label = f"{{bearing}}\\n{{distance:.1f}}'"
        
        msp.add_text(
            label,
            dxfattribs={{
                'layer': 'TEXT',
                'height': 2.0,
                'style': 'Standard'
            }}
        ).set_placement((mid_x, mid_y + 3))

# Add property corner markers
for corner in corners:
    msp.add_circle(
        (corner['x'], corner['y']), 
        1.0, 
        dxfattribs={{'layer': 'PROP'}}
    )
    
    # Label the corner
    msp.add_text(
        corner['point_id'],
        dxfattribs={{
            'layer': 'TEXT',
            'height': 1.5
        }}
    ).set_placement((corner['x'] + 2, corner['y'] + 2))

# Save the DXF file
doc.saveas('subdivision_layout.dxf')
print("Subdivision layout generated successfully!")'''
        
        return code
    
    def generate_dxf(self, data: Dict) -> tuple:
        """Generate actual DXF file content with enhanced professional details"""
        self.create_document()
        
        # Create comprehensive layer system
        layers = [
            {'name': 'PROP-LINE', 'color': 1},      # Red - Property lines
            {'name': 'PROP-TEXT', 'color': 41},     # Orange - Property labels
            {'name': 'LOT-LINE', 'color': 30},      # Orange - Lot lines
            {'name': 'LOT-TEXT', 'color': 30},      # Orange - Lot labels
            {'name': 'STREET-CL', 'color': 6},      # Cyan - Street centerlines
            {'name': 'STREET-ROW', 'color': 8},     # Gray - Right of way
            {'name': 'STREET-TEXT', 'color': 6},    # Cyan - Street names
            {'name': 'BLDG', 'color': 5},           # Magenta - Buildings
            {'name': 'BLDG-TEXT', 'color': 5},      # Magenta - Building labels
            {'name': 'SIDEWALK', 'color': 252},     # Light gray - Sidewalks
            {'name': 'DRIVEWAY', 'color': 9},       # Gray - Driveways
            {'name': 'EASEMENT', 'color': 4},       # Cyan - Easements
            {'name': 'LANDSCAPE', 'color': 92},     # Green - Trees/landscape
            {'name': 'DIMENSIONS', 'color': 7},     # White - Dimension lines
            {'name': 'MARKERS', 'color': 1}         # Red - Corner markers
        ]
        self.create_layers(layers)
        
        # Create ROMANS text style
        try:
            self.doc.styles.add('ROMANS', font='romans.shx')
        except:
            pass
        
        corners = data.get("property_corners", [])
        
        # Validate corners data
        if not corners or not isinstance(corners, list):
            corners = []
        
        # Filter out invalid corners
        valid_corners = [c for c in corners if self.validate_point(c)]
        
        if len(valid_corners) >= 3:
            # Use valid corners
            corners = valid_corners
            
            # === PROPERTY BOUNDARY ===
            points = [self.safe_get_coords(pt) for pt in corners]
            points.append(points[0])
            
            try:
                self.msp.add_lwpolyline(
                    points,
                    dxfattribs={'layer': 'PROP-LINE', 'lineweight': 35}
                )
            except Exception:
                pass
        
            # Add bearing/distance labels with better formatting
            for i in range(len(corners)):
                try:
                    pt1 = self.safe_get_coords(corners[i])
                    pt2 = self.safe_get_coords(corners[(i+1) % len(corners)])
            
                    bearing, distance = self.calculate_bearing_distance(pt1, pt2)
                
                    mid_x = (pt1[0] + pt2[0]) / 2
                    mid_y = (pt1[1] + pt2[1]) / 2
                    
                    # Distance label
                    self.msp.add_text(
                        f"{distance:.2f}'",
                        dxfattribs={'layer': 'PROP-TEXT', 'height': 3.0, 'style': 'ROMANS'}
                    ).set_placement((mid_x, mid_y + 5))
                    
                    # Bearing label
                    self.msp.add_text(
                        bearing,
                        dxfattribs={'layer': 'PROP-TEXT', 'height': 2.5, 'style': 'ROMANS'}
                    ).set_placement((mid_x, mid_y + 1))
                except Exception:
                    pass
            
            # Property corner markers with professional symbols
            for corner in corners:
                try:
                    x, y = self.safe_get_coords(corner)
                    point_id = self.safe_get_field(corner, 'point_id', 'PT')
                    
                    # X marker
                    self.msp.add_line(
                        (x - 1.5, y - 1.5),
                        (x + 1.5, y + 1.5),
                        dxfattribs={'layer': 'MARKERS', 'lineweight': 25}
                    )
                    self.msp.add_line(
                        (x - 1.5, y + 1.5),
                        (x + 1.5, y - 1.5),
                        dxfattribs={'layer': 'MARKERS', 'lineweight': 25}
                    )
                    # Circle around marker
                    self.msp.add_circle(
                        (x, y),
                        2.0,
                        dxfattribs={'layer': 'MARKERS'}
                    )
                    # Point ID
                    self.msp.add_text(
                        point_id,
                        dxfattribs={'layer': 'PROP-TEXT', 'height': 2.5, 'style': 'ROMANS'}
                    ).set_placement((x + 3, y + 3))
                except Exception:
                    pass
            
            # === CREATE SUBDIVISION LOTS ===
            # Calculate center for lot layout
            try:
                center_x = sum(self.safe_get_coords(pt)[0] for pt in corners) / len(corners)
                center_y = sum(self.safe_get_coords(pt)[1] for pt in corners) / len(corners)
            except (ZeroDivisionError, Exception):
                center_x, center_y = 0.0, 0.0
            
            # Create 6 lots in 2 rows of 3
            lot_width = 60
            lot_depth = 100
            lots = []
            
            for row in range(2):
                for col in range(3):
                    lot_x = center_x - lot_width*1.5 + col*lot_width
                    lot_y = center_y - lot_depth + row*lot_depth
                    lot_num = row*3 + col + 1
                    
                    # Lot boundary
                    lot_corners = [
                        (lot_x, lot_y),
                        (lot_x + lot_width, lot_y),
                        (lot_x + lot_width, lot_y + lot_depth),
                        (lot_x, lot_y + lot_depth),
                        (lot_x, lot_y)
                    ]
                    self.msp.add_lwpolyline(
                        lot_corners,
                        dxfattribs={'layer': 'LOT-LINE'}
                    )
                    
                    # Lot number label
                    self.msp.add_text(
                        f"LOT {lot_num}",
                        dxfattribs={'layer': 'LOT-TEXT', 'height': 5.0, 'style': 'ROMANS'}
                    ).set_placement((lot_x + lot_width/2, lot_y + lot_depth/2))
                    
                    # Lot dimensions
                    self.msp.add_text(
                        f"{lot_width}' x {lot_depth}'",
                        dxfattribs={'layer': 'LOT-TEXT', 'height': 3.0, 'style': 'ROMANS'}
                    ).set_placement((lot_x + lot_width/2, lot_y + lot_depth/2 - 6))
                    
                    # Address
                    address_num = 1000 + lot_num*10
                    self.msp.add_text(
                        f"{address_num} MAIN ST",
                        dxfattribs={'layer': 'LOT-TEXT', 'height': 2.5, 'style': 'ROMANS'}
                    ).set_placement((lot_x + lot_width/2, lot_y + 5))
                    
                    # === BUILDING FOOTPRINT ===
                    bldg_margin = 15
                    bldg_x = lot_x + bldg_margin
                    bldg_y = lot_y + 40
                    bldg_width = lot_width - 2*bldg_margin
                    bldg_depth = 40
                    
                    bldg_corners = [
                        (bldg_x, bldg_y),
                        (bldg_x + bldg_width, bldg_y),
                        (bldg_x + bldg_width, bldg_y + bldg_depth),
                        (bldg_x, bldg_y + bldg_depth),
                        (bldg_x, bldg_y)
                    ]
                    self.msp.add_lwpolyline(
                        bldg_corners,
                        dxfattribs={'layer': 'BLDG', 'lineweight': 25}
                    )
                    
                    # Building label
                    self.msp.add_text(
                        f"SF {1800 + lot_num*100} SF",
                        dxfattribs={'layer': 'BLDG-TEXT', 'height': 2.0, 'style': 'ROMANS'}
                    ).set_placement((bldg_x + bldg_width/2, bldg_y + bldg_depth/2))
                    
                    # === DRIVEWAY ===
                    driveway_width = 12
                    driveway_x = lot_x + lot_width/2 - driveway_width/2
                    driveway_corners = [
                        (driveway_x, lot_y),
                        (driveway_x + driveway_width, lot_y),
                        (driveway_x + driveway_width, lot_y + 25),
                        (driveway_x, lot_y + 25),
                        (driveway_x, lot_y)
                    ]
                    self.msp.add_lwpolyline(
                        driveway_corners,
                        dxfattribs={'layer': 'DRIVEWAY'}
                    )
                    
                    # === TREES (landscaping) ===
                    # Front yard trees
                    for tree_offset in [-15, 15]:
                        tree_x = lot_x + lot_width/2 + tree_offset
                        tree_y = lot_y + 60
                        self.msp.add_circle(
                            (tree_x, tree_y),
                            3.0,
                            dxfattribs={'layer': 'LANDSCAPE'}
                        )
            
            # === STREET NETWORK ===
            # Main Street (horizontal)
            street_y = center_y - lot_depth
            street_width = 40
            
            # Street centerline
            self.msp.add_line(
                (center_x - 200, street_y),
                (center_x + 200, street_y),
                dxfattribs={'layer': 'STREET-CL', 'linetype': 'CENTER', 'lineweight': 25}
            )
            
            # Street edges
            self.msp.add_line(
                (center_x - 200, street_y - street_width/2),
                (center_x + 200, street_y - street_width/2),
                dxfattribs={'layer': 'STREET-ROW'}
            )
            self.msp.add_line(
                (center_x - 200, street_y + street_width/2),
                (center_x + 200, street_y + street_width/2),
                dxfattribs={'layer': 'STREET-ROW'}
            )
            
            # Street name
            self.msp.add_text(
                "MAIN STREET",
                dxfattribs={'layer': 'STREET-TEXT', 'height': 8.0, 'style': 'ROMANS'}
            ).set_placement((center_x, street_y - 30))
            
            # === SIDEWALKS ===
            sidewalk_width = 5
            # North sidewalk
            self.msp.add_lwpolyline([
                (center_x - 200, street_y + street_width/2 + 3),
                (center_x + 200, street_y + street_width/2 + 3),
                (center_x + 200, street_y + street_width/2 + 3 + sidewalk_width),
                (center_x - 200, street_y + street_width/2 + 3 + sidewalk_width),
                (center_x - 200, street_y + street_width/2 + 3)
            ], dxfattribs={'layer': 'SIDEWALK'})
            
            # === UTILITY EASEMENT ===
            # 10' utility easement along rear lot lines
            easement_width = 10
            easement_y = center_y + lot_depth
            self.msp.add_lwpolyline([
                (center_x - lot_width*1.5, easement_y),
                (center_x + lot_width*1.5, easement_y),
                (center_x + lot_width*1.5, easement_y - easement_width),
                (center_x - lot_width*1.5, easement_y - easement_width),
                (center_x - lot_width*1.5, easement_y)
            ], dxfattribs={'layer': 'EASEMENT', 'linetype': 'DASHED'})
            
            # Easement label
            self.msp.add_text(
                "10' UTILITY EASEMENT",
                dxfattribs={'layer': 'EASEMENT', 'height': 3.0, 'style': 'ROMANS'}
            ).set_placement((center_x, easement_y - 5))
            
            # === TITLE BLOCK / LEGEND ===
            title_x = center_x - 180
            title_y = center_y + 140
            
            self.msp.add_text(
                "SUNSET HILLS SUBDIVISION",
                dxfattribs={'layer': 'PROP-TEXT', 'height': 10.0, 'style': 'ROMANS'}
            ).set_placement((title_x, title_y))
            
            self.msp.add_text(
                f"6 Residential Lots - Total Area: {lot_width*lot_depth*6/43560:.2f} Acres",
                dxfattribs={'layer': 'PROP-TEXT', 'height': 4.0, 'style': 'ROMANS'}
            ).set_placement((title_x, title_y - 12))
        
        filename = "subdivision_layout_enhanced.dxf"
        return self.save_to_bytes(), filename

class UtilityGenerator(CADGenerator):
    """Generate utility networks with pipes and structures"""
    
    def generate_code(self, data: Dict, utility_type: str) -> str:
        """Generate Python code for utility network"""
        pipes = data.get("pipes", [])
        structures = data.get("structures", [])
        
        code = f'''import ezdxf

# Create new DXF document for {utility_type}
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Create utility layers
doc.layers.new('UTIL-PIPE', dxfattribs={{'color': 4, 'linetype': 'CONTINUOUS'}})
doc.layers.new('UTIL-STRUCT', dxfattribs={{'color': 2}})
doc.layers.new('UTIL-TEXT', dxfattribs={{'color': 3}})

# Define utility structure blocks
block = doc.blocks.new(name='MANHOLE')
block.add_circle((0, 0), 2.0)
block.add_line((-1.5, 0), (1.5, 0))
block.add_line((0, -1.5), (0, 1.5))

# Pipe data
pipes = {pipes}

# Structure data  
structures = {structures}

# Draw pipes
for pipe in pipes:
    start_point = (pipe['start_x'], pipe['start_y'])
    end_point = (pipe['end_x'], pipe['end_y'])
    
    # Draw pipe as line
    msp.add_line(
        start_point, 
        end_point,
        dxfattribs={{'layer': 'UTIL-PIPE'}}
    )
    
    # Add pipe label at midpoint
    mid_x = (start_point[0] + end_point[0]) / 2
    mid_y = (start_point[1] + end_point[1]) / 2
    
    label = f"{{pipe['size']}}\" {{pipe['material']}}"
    
    msp.add_text(
        label,
        dxfattribs={{
            'layer': 'UTIL-TEXT',
            'height': 1.5
        }}
    ).set_placement((mid_x, mid_y + 2))

# Insert structure blocks
for struct in structures:
    msp.add_blockref(
        'MANHOLE',
        (struct['x'], struct['y']),
        dxfattribs={{'layer': 'UTIL-STRUCT'}}
    )
    
    # Label structure with RIM and INVERT elevations
    rim_elev = struct.get('rim_elev', 'N/A')
    invert_elev = struct.get('invert_elev', 'N/A')
    label = f"{{struct['id']}}\\nRIM: {{rim_elev}}\\nINV: {{invert_elev}}"
    
    msp.add_text(
        label,
        dxfattribs={{
            'layer': 'UTIL-TEXT',
            'height': 2.0
        }}
    ).set_placement((struct['x'] + 3, struct['y'] + 3))

# Save the utility network
doc.saveas('{utility_type.lower().replace(" ", "_")}_network.dxf')
print("{utility_type} network generated!")'''
        
        return code
    
    def generate_dxf(self, data: Dict, utility_type: str) -> tuple:
        """Generate comprehensive utility network DXF with multiple systems"""
        self.create_document()
        
        # Create comprehensive layer system for all utilities
        layers = [
            {'name': 'WATER-PIPE', 'color': 4},      # Blue - Water pipes
            {'name': 'WATER-STRUCT', 'color': 4},    # Blue - Water structures
            {'name': 'WATER-TEXT', 'color': 4},      # Blue - Water labels
            {'name': 'SEWER-PIPE', 'color': 1},      # Red - Sewer pipes
            {'name': 'SEWER-STRUCT', 'color': 1},    # Red - Sewer structures
            {'name': 'SEWER-TEXT', 'color': 1},      # Red - Sewer labels
            {'name': 'STORM-PIPE', 'color': 6},      # Cyan - Storm pipes
            {'name': 'STORM-STRUCT', 'color': 6},    # Cyan - Storm structures
            {'name': 'STORM-TEXT', 'color': 6},      # Cyan - Storm labels
            {'name': 'GAS-PIPE', 'color': 30},       # Orange - Gas pipes
            {'name': 'GAS-STRUCT', 'color': 30},     # Orange - Gas structures
            {'name': 'GAS-TEXT', 'color': 30}        # Orange - Gas labels
        ]
        self.create_layers(layers)
        
        # Create ROMANS text style
        self.doc.styles.add('ROMANS', font='romans.shx')
        
        # Import block library for utility symbols
        from utils.block_library import CivilBlockLibrary
        CivilBlockLibrary.create_model_space_blocks(self.doc)
        
        # === WATER NETWORK ===
        water_structures = [
            {'x': 50, 'y': 0, 'id': 'WV-1', 'rim': 145.5},
            {'x': 150, 'y': 0, 'id': 'WM-1', 'rim': 145.2},
            {'x': 250, 'y': 0, 'id': 'FH-1', 'rim': 145.8}
        ]
        
        # Water main line
        self.msp.add_line((0, 0), (300, 0), dxfattribs={'layer': 'WATER-PIPE', 'lineweight': 35})
        self.msp.add_text('12" DIP WATER MAIN', dxfattribs={'layer': 'WATER-TEXT', 'height': 3.0, 'style': 'ROMANS'}).set_placement((150, 8))
        
        for struct in water_structures:
            try:
                x, y = self.safe_get_coords(struct)
                struct_id = self.safe_get_field(struct, 'id', 'UNKNOWN')
                rim = self.safe_get_field(struct, 'rim', '0.0')
                
                if 'WV' in struct_id:
                    CivilBlockLibrary.insert_block(self.msp, 'VALVE_WATER', (x, y), scale=1.5)
                elif 'WM' in struct_id:
                    CivilBlockLibrary.insert_block(self.msp, 'WATER_METER', (x, y), scale=1.5)
                elif 'FH' in struct_id:
                    CivilBlockLibrary.insert_block(self.msp, 'HYDRANT', (x, y), scale=1.5)
                
                # Labels with elevation
                self.msp.add_text(f"{struct_id}\nRIM: {rim}", 
                    dxfattribs={'layer': 'WATER-TEXT', 'height': 2.0, 'style': 'ROMANS'}
                ).set_placement((x, y + 10))
            except Exception:
                pass
        
        # === SEWER NETWORK ===
        sewer_structures = [
            {'x': 0, 'y': -50, 'id': 'MH-1', 'rim': 144.5, 'inv_in': 139.8, 'inv_out': 139.6},
            {'x': 100, 'y': -50, 'id': 'MH-2', 'rim': 143.2, 'inv_in': 138.5, 'inv_out': 138.3},
            {'x': 200, 'y': -50, 'id': 'MH-3', 'rim': 142.0, 'inv_in': 137.2, 'inv_out': 137.0},
            {'x': 300, 'y': -50, 'id': 'MH-4', 'rim': 140.8, 'inv_in': 136.0, 'inv_out': 135.8}
        ]
        
        # Sewer pipes with flow arrows
        for i in range(len(sewer_structures) - 1):
            try:
                start = self.safe_get_coords(sewer_structures[i])
                end = self.safe_get_coords(sewer_structures[i+1])
                self.msp.add_line(start, end, dxfattribs={'layer': 'SEWER-PIPE', 'lineweight': 35})
                
                # Flow arrow
                mid_x = (start[0] + end[0]) / 2
                mid_y = (start[1] + end[1]) / 2
                self.msp.add_line((mid_x - 5, mid_y), (mid_x + 5, mid_y), dxfattribs={'layer': 'SEWER-PIPE', 'lineweight': 25})
                self.msp.add_line((mid_x + 5, mid_y), (mid_x + 2, mid_y + 2), dxfattribs={'layer': 'SEWER-PIPE', 'lineweight': 25})
                self.msp.add_line((mid_x + 5, mid_y), (mid_x + 2, mid_y - 2), dxfattribs={'layer': 'SEWER-PIPE', 'lineweight': 25})
                
                # Pipe label
                self.msp.add_text('8" VCP', dxfattribs={'layer': 'SEWER-TEXT', 'height': 2.5, 'style': 'ROMANS'}).set_placement((mid_x, mid_y + 5))
            except Exception:
                pass
        
        for struct in sewer_structures:
            try:
                x, y = self.safe_get_coords(struct)
                struct_id = self.safe_get_field(struct, 'id', 'UNKNOWN')
                rim = self.safe_get_field(struct, 'rim', '0.0')
                inv_in = self.safe_get_field(struct, 'inv_in', '0.0')
                inv_out = self.safe_get_field(struct, 'inv_out', '0.0')
                
                CivilBlockLibrary.insert_block(self.msp, 'MH_SANITARY', (x, y), scale=1.5)
                self.msp.add_text(
                    f"{struct_id}\nRIM: {rim}\nINV IN: {inv_in}\nINV OUT: {inv_out}",
                    dxfattribs={'layer': 'SEWER-TEXT', 'height': 2.0, 'style': 'ROMANS'}
                ).set_placement((x + 8, y))
            except Exception:
                pass
        
        # === STORM DRAIN NETWORK ===
        storm_structures = [
            {'x': 50, 'y': -100, 'id': 'CB-1', 'rim': 145.0, 'inv': 140.5},
            {'x': 150, 'y': -100, 'id': 'SD-1', 'rim': 144.5, 'inv': 140.0},
            {'x': 250, 'y': -100, 'id': 'CB-2', 'rim': 144.0, 'inv': 139.5}
        ]
        
        # Storm pipes
        for i in range(len(storm_structures) - 1):
            try:
                start = self.safe_get_coords(storm_structures[i])
                end = self.safe_get_coords(storm_structures[i+1])
                self.msp.add_line(start, end, dxfattribs={'layer': 'STORM-PIPE', 'lineweight': 35})
            except Exception:
                pass
        
        self.msp.add_text('15" RCP STORM DRAIN', dxfattribs={'layer': 'STORM-TEXT', 'height': 3.0, 'style': 'ROMANS'}).set_placement((150, -90))
        
        for struct in storm_structures:
            try:
                x, y = self.safe_get_coords(struct)
                struct_id = self.safe_get_field(struct, 'id', 'UNKNOWN')
                rim = self.safe_get_field(struct, 'rim', '0.0')
                inv = self.safe_get_field(struct, 'inv', '0.0')
                
                if 'CB' in struct_id:
                    CivilBlockLibrary.insert_block(self.msp, 'CATCH_BASIN', (x, y), scale=1.5)
                else:
                    CivilBlockLibrary.insert_block(self.msp, 'INLET_STORM', (x, y), scale=1.5)
                
                self.msp.add_text(
                    f"{struct_id}\nRIM: {rim}\nINV: {inv}",
                    dxfattribs={'layer': 'STORM-TEXT', 'height': 2.0, 'style': 'ROMANS'}
                ).set_placement((x, y - 15))
            except Exception:
                pass
        
        # === GAS NETWORK ===
        gas_structures = [
            {'x': 0, 'y': 50, 'id': 'GV-1'},
            {'x': 150, 'y': 50, 'id': 'GV-2'},
            {'x': 300, 'y': 50, 'id': 'GV-3'}
        ]
        
        self.msp.add_line((0, 50), (300, 50), dxfattribs={'layer': 'GAS-PIPE', 'lineweight': 25, 'linetype': 'DASHED'})
        self.msp.add_text('4" HDPE GAS MAIN', dxfattribs={'layer': 'GAS-TEXT', 'height': 3.0, 'style': 'ROMANS'}).set_placement((150, 58))
        
        for struct in gas_structures:
            try:
                x, y = self.safe_get_coords(struct)
                struct_id = self.safe_get_field(struct, 'id', 'UNKNOWN')
                
                CivilBlockLibrary.insert_block(self.msp, 'VALVE_GAS', (x, y), scale=1.5)
                self.msp.add_text(struct_id, dxfattribs={'layer': 'GAS-TEXT', 'height': 2.5, 'style': 'ROMANS'}).set_placement((x, y + 8))
            except Exception:
                pass
        
        # === TITLE BLOCK ===
        self.msp.add_text(
            'COMPREHENSIVE UTILITY PLAN',
            dxfattribs={'layer': 'WATER-TEXT', 'height': 8.0, 'style': 'ROMANS'}
        ).set_placement((-20, 80))
        
        self.msp.add_text(
            'WATER (BLUE) | SEWER (RED) | STORM (CYAN) | GAS (ORANGE)',
            dxfattribs={'layer': 'WATER-TEXT', 'height': 3.5, 'style': 'ROMANS'}
        ).set_placement((-20, 70))
        
        filename = "comprehensive_utility_network.dxf"
        return self.save_to_bytes(), filename

class SurveyGenerator(CADGenerator):
    """Generate CAD drawings from survey points"""
    
    def generate_code(self, data: Dict) -> str:
        """Generate code for survey point connections"""
        points = data.get("points", [])
        
        code = f'''import ezdxf
import math

# Create DXF document for survey data
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Create survey layers
doc.layers.new('SURVEY-POINTS', dxfattribs={{'color': 1}})
doc.layers.new('SURVEY-LINE', dxfattribs={{'color': 2}})
doc.layers.new('SURVEY-TEXT', dxfattribs={{'color': 3}})

# Survey point data
points = {points}

# Group points by description
grouped_points = {{}}
for point in points:
    desc = point.get('description', 'UNKNOWN')
    if desc not in grouped_points:
        grouped_points[desc] = []
    grouped_points[desc].append(point)

# Connect points within each group
for description, point_group in grouped_points.items():
    if len(point_group) >= 2:
        # Sort points to create logical connections
        point_group.sort(key=lambda p: (p['x'], p['y']))
        
        # Create polyline connecting points
        point_coords = [(p['x'], p['y']) for p in point_group]
        
        msp.add_lwpolyline(
            point_coords,
            dxfattribs={{'layer': 'SURVEY-LINE'}}
        )
        
        # Label the line with description
        mid_idx = len(point_coords) // 2
        mid_point = point_coords[mid_idx]
        
        msp.add_text(
            description,
            dxfattribs={{
                'layer': 'SURVEY-TEXT',
                'height': 2.0
            }}
        ).set_placement((mid_point[0], mid_point[1] + 3))

# Add individual point markers
for point in points:
    # Draw point marker
    msp.add_circle(
        (point['x'], point['y']),
        0.5,
        dxfattribs={{'layer': 'SURVEY-POINTS'}}
    )
    
    # Add point ID label
    msp.add_text(
        point['point_id'],
        dxfattribs={{
            'layer': 'SURVEY-TEXT',
            'height': 1.0
        }}
    ).set_placement((point['x'] + 1, point['y'] + 1))

# Save survey drawing
doc.saveas('survey_connections.dxf')
print("Survey point connections generated!")'''
        
        return code
    
    def generate_dxf(self, data: Dict) -> tuple:
        """Generate survey connections DXF"""
        self.create_document()
        
        # Create layers
        layers = [
            {'name': 'SURVEY-POINTS', 'color': 1},
            {'name': 'SURVEY-LINE', 'color': 2},
            {'name': 'SURVEY-TEXT', 'color': 3}
        ]
        self.create_layers(layers)
        
        points = data.get("points", [])
        
        # Validate and filter points
        valid_points = [p for p in points if self.validate_point(p)]
        
        # Group points by description
        grouped_points = {}
        for point in valid_points:
            desc = point.get('description', 'UNKNOWN')
            if desc not in grouped_points:
                grouped_points[desc] = []
            grouped_points[desc].append(point)
        
        # Connect points within groups
        for description, point_group in grouped_points.items():
            if len(point_group) >= 2:
                try:
                    # Sort using safe coordinate extraction
                    point_group.sort(key=lambda p: self.safe_get_coords(p))
                    
                    # Build coordinate list with safe extraction
                    point_coords = [self.safe_get_coords(p) for p in point_group]
                    
                    self.msp.add_lwpolyline(
                        point_coords,
                        dxfattribs={'layer': 'SURVEY-LINE'}
                    )
                    
                    # Label line
                    mid_idx = len(point_coords) // 2
                    mid_point = point_coords[mid_idx]
                    
                    self.msp.add_text(
                        description,
                        dxfattribs={
                            'layer': 'SURVEY-TEXT',
                            'height': 2.0
                        }
                    ).set_placement((mid_point[0], mid_point[1] + 3))
                except Exception:
                    pass
        
        # Add point markers
        for point in valid_points:
            try:
                x, y = self.safe_get_coords(point)
                point_id = self.safe_get_field(point, 'point_id', 'PT')
                
                self.msp.add_circle(
                    (x, y),
                    0.5,
                    dxfattribs={'layer': 'SURVEY-POINTS'}
                )
                
                self.msp.add_text(
                    point_id,
                    dxfattribs={
                        'layer': 'SURVEY-TEXT',
                        'height': 1.0
                    }
                ).set_placement((x + 1, y + 1))
            except Exception:
                pass
        
        filename = "survey_connections.dxf"
        return self.save_to_bytes(), filename

class PlanSheetGenerator(CADGenerator):
    """Generate automated plan sheets with title blocks"""
    
    def generate_code(self, data: Dict) -> str:
        """Generate code for plan sheets"""
        project_name = data.get("project_name", "")
        project_number = data.get("project_number", "")
        engineer = data.get("engineer", "")
        sheet_size = data.get("sheet_size", "D (24x36)")
        scale = data.get("scale", '1"=20\'')
        num_sheets = self._calculate_sheet_count(data)
        
        code = f'''import ezdxf

# Create DXF document for plan sheets
doc = ezdxf.new('R2010')

# Project information
project_name = "{project_name}"
project_number = "{project_number}"
engineer = "{engineer}"

# Sheet configuration
sheet_size = "{sheet_size}"
scale = "{scale}"

# Create plan sheet layouts
for sheet_num in range(1, {num_sheets + 1}):
    # Create new layout for each sheet
    layout = doc.layouts.new(f"C-{{sheet_num:02d}}")
    
    # Create title block
    title_block_x = 0
    title_block_y = 0
    title_block_width = 36  # For D-size sheet
    title_block_height = 24
    
    # Draw title block border
    layout.add_lwpolyline([
        (title_block_x, title_block_y),
        (title_block_x + title_block_width, title_block_y),
        (title_block_x + title_block_width, title_block_y + title_block_height),
        (title_block_x, title_block_y + title_block_height),
        (title_block_x, title_block_y)
    ])
    
    # Add title block information
    layout.add_text(
        project_name,
        dxfattribs={{'height': 0.25}}
    ).set_placement((title_block_width - 8, 1))
    
    layout.add_text(
        f"Sheet {{sheet_num}} of {num_sheets}",
        dxfattribs={{'height': 0.125}}
    ).set_placement((title_block_width - 8, 0.5))
    
    layout.add_text(
        f"Project: {{project_number}}",
        dxfattribs={{'height': 0.125}}
    ).set_placement((title_block_width - 8, 0.25))
    
    # Create viewport for drawing content
    viewport = layout.add_viewport(
        center=(title_block_width/2, title_block_height/2),
        size=(title_block_width - 2, title_block_height - 4),
        view_center_point=(sheet_num * 200, 250),  # Shift view for each sheet
        view_height=400
    )

# Save the plan sheets
doc.saveas('plan_sheets.dxf')
print(f"Generated {{num_sheets}} plan sheets!")'''
        
        return code
    
    def _calculate_sheet_count(self, data: Dict) -> int:
        """Calculate number of sheets needed"""
        coverage = data.get("coverage", {})
        total_length = coverage.get("end_station", 1000) - coverage.get("start_station", 0)
        sheet_length = coverage.get("sheet_length", 200)
        return max(1, int(np.ceil(total_length / sheet_length)))
    
    def generate_dxf(self, data: Dict) -> tuple:
        """Generate plan sheets DXF"""
        self.create_document()
        
        project_name = data.get("project_name", "Project")
        project_number = data.get("project_number", "")
        engineer = data.get("engineer", "")
        num_sheets = self._calculate_sheet_count(data)
        
        # Create plan sheet layouts
        for sheet_num in range(1, num_sheets + 1):
            layout = self.doc.layouts.new(f"C-{sheet_num:02d}")
            
            # Title block dimensions (D-size)
            title_block_width = 36
            title_block_height = 24
            
            # Draw title block border
            layout.add_lwpolyline([
                (0, 0),
                (title_block_width, 0),
                (title_block_width, title_block_height),
                (0, title_block_height),
                (0, 0)
            ])
            
            # Add title block text
            layout.add_text(
                project_name,
                dxfattribs={'height': 0.25}
            ).set_placement((title_block_width - 8, 1))
            
            layout.add_text(
                f"Sheet {sheet_num} of {num_sheets}",
                dxfattribs={'height': 0.125}
            ).set_placement((title_block_width - 8, 0.5))
            
            layout.add_text(
                f"Project: {project_number}",
                dxfattribs={'height': 0.125}
            ).set_placement((title_block_width - 8, 0.25))
            
            layout.add_text(
                f"Engineer: {engineer}",
                dxfattribs={'height': 0.125}
            ).set_placement((1, 0.25))
            
            # Create viewport
            layout.add_viewport(
                center=(title_block_width/2, title_block_height/2),
                size=(title_block_width - 2, title_block_height - 4),
                view_center_point=(sheet_num * 200, 250),
                view_height=400
            )
        
        filename = f"{project_name.replace(' ', '_')}_plan_sheets.dxf"
        return self.save_to_bytes(), filename

class Grading3DGenerator(CADGenerator):
    """Generate 3D grading surfaces with earthwork calculations"""
    
    def generate_code(self, data: Dict, grading_type: str) -> str:
        """Generate Python code for 3D grading"""
        code = f'''import ezdxf
import numpy as np

# Create DXF document for 3D grading
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Create 3D grading layers
doc.layers.new('EXISTING', dxfattribs={{'color': 8}})  # Gray
doc.layers.new('PROPOSED', dxfattribs={{'color': 3}})  # Green
doc.layers.new('CUT', dxfattribs={{'color': 1}})       # Red
doc.layers.new('FILL', dxfattribs={{'color': 5}})      # Blue
doc.layers.new('CONTOURS', dxfattribs={{'color': 7}})  # White/Black

# Grid points with X, Y, Z coordinates
# Each point has existing_z and proposed_z elevations
grid_points = {data.get("grid_points", [])[:20]}... # Truncated for display

# Create 3D faces for terrain
for i in range(len(x_grid) - 1):
    for j in range(len(y_grid) - 1):
        # Get four corner points
        p1 = grid_points[i * len(y_grid) + j]
        p2 = grid_points[(i+1) * len(y_grid) + j]
        p3 = grid_points[(i+1) * len(y_grid) + (j+1)]
        p4 = grid_points[i * len(y_grid) + (j+1)]
        
        # Create existing surface face
        msp.add_3dface([
            (p1['x'], p1['y'], p1['existing_z']),
            (p2['x'], p2['y'], p2['existing_z']),
            (p3['x'], p3['y'], p3['existing_z']),
            (p4['x'], p4['y'], p4['existing_z'])
        ], dxfattribs={{'layer': 'EXISTING'}})
        
        # Create proposed surface face
        msp.add_3dface([
            (p1['x'], p1['y'], p1['proposed_z']),
            (p2['x'], p2['y'], p2['proposed_z']),
            (p3['x'], p3['y'], p3['proposed_z']),
            (p4['x'], p4['y'], p4['proposed_z'])
        ], dxfattribs={{'layer': 'PROPOSED'}})
        
        # Add cut/fill visualization
        avg_diff = (p1['proposed_z'] - p1['existing_z'] + 
                   p2['proposed_z'] - p2['existing_z'] +
                   p3['proposed_z'] - p3['existing_z'] +
                   p4['proposed_z'] - p4['existing_z']) / 4
        
        layer = 'FILL' if avg_diff > 0 else 'CUT'
        
        # Add colored face at proposed elevation
        msp.add_3dface([
            (p1['x'], p1['y'], p1['proposed_z']),
            (p2['x'], p2['y'], p2['proposed_z']),
            (p3['x'], p3['y'], p3['proposed_z']),
            (p4['x'], p4['y'], p4['proposed_z'])
        ], dxfattribs={{'layer': layer}})

# Add 3D point markers
for pt in grid_points:
    # Existing ground point
    msp.add_point(
        (pt['x'], pt['y'], pt['existing_z']),
        dxfattribs={{'layer': 'EXISTING'}}
    )
    
    # Proposed elevation point
    msp.add_point(
        (pt['x'], pt['y'], pt['proposed_z']),
        dxfattribs={{'layer': 'PROPOSED'}}
    )

# Save 3D grading model
doc.saveas('{grading_type.lower().replace(" ", "_")}_grading.dxf')
print("3D grading model generated!")'''
        
        return code
    
    def generate_dxf(self, data: Dict, grading_type: str) -> tuple:
        """Generate 3D grading DXF"""
        self.create_document()
        
        # Create layers
        layers = [
            {'name': 'EXISTING', 'color': 8},  # Gray
            {'name': 'PROPOSED', 'color': 3},  # Green
            {'name': 'CUT', 'color': 1},       # Red
            {'name': 'FILL', 'color': 5},      # Blue
            {'name': 'CONTOURS', 'color': 7}   # White/Black
        ]
        self.create_layers(layers)
        
        grid_points = data.get("grid_points", [])
        
        if not grid_points:
            # Return empty DXF
            filename = f"{grading_type.lower().replace(' ', '_')}_grading.dxf"
            return self.save_to_bytes(), filename
        
        # Determine grid dimensions
        x_coords = sorted(set(pt['x'] for pt in grid_points))
        y_coords = sorted(set(pt['y'] for pt in grid_points))
        
        # Create point lookup
        point_dict = {}
        for pt in grid_points:
            key = (pt['x'], pt['y'])
            point_dict[key] = pt
        
        # Create 3D faces
        for i in range(len(x_coords) - 1):
            for j in range(len(y_coords) - 1):
                x1, x2 = x_coords[i], x_coords[i+1]
                y1, y2 = y_coords[j], y_coords[j+1]
                
                # Get four corner points
                p1 = point_dict.get((x1, y1))
                p2 = point_dict.get((x2, y1))
                p3 = point_dict.get((x2, y2))
                p4 = point_dict.get((x1, y2))
                
                if not all([p1, p2, p3, p4]):
                    continue
                
                # Existing surface
                self.msp.add_3dface([
                    (p1['x'], p1['y'], p1['existing_z']),
                    (p2['x'], p2['y'], p2['existing_z']),
                    (p3['x'], p3['y'], p3['existing_z']),
                    (p4['x'], p4['y'], p4['existing_z'])
                ], dxfattribs={'layer': 'EXISTING'})
                
                # Proposed surface
                self.msp.add_3dface([
                    (p1['x'], p1['y'], p1['proposed_z']),
                    (p2['x'], p2['y'], p2['proposed_z']),
                    (p3['x'], p3['y'], p3['proposed_z']),
                    (p4['x'], p4['y'], p4['proposed_z'])
                ], dxfattribs={'layer': 'PROPOSED'})
                
                # Cut/fill layer
                avg_diff = ((p1['proposed_z'] - p1['existing_z']) +
                           (p2['proposed_z'] - p2['existing_z']) +
                           (p3['proposed_z'] - p3['existing_z']) +
                           (p4['proposed_z'] - p4['existing_z'])) / 4
                
                layer = 'FILL' if avg_diff > 0 else 'CUT'
                
                self.msp.add_3dface([
                    (p1['x'], p1['y'], p1['proposed_z']),
                    (p2['x'], p2['y'], p2['proposed_z']),
                    (p3['x'], p3['y'], p3['proposed_z']),
                    (p4['x'], p4['y'], p4['proposed_z'])
                ], dxfattribs={'layer': layer})
        
        # Add 3D points
        for pt in grid_points:
            self.msp.add_point(
                (pt['x'], pt['y'], pt['existing_z']),
                dxfattribs={'layer': 'EXISTING'}
            )
            
            self.msp.add_point(
                (pt['x'], pt['y'], pt['proposed_z']),
                dxfattribs={'layer': 'PROPOSED'}
            )
        
        filename = f"{grading_type.lower().replace(' ', '_')}_grading.dxf"
        return self.save_to_bytes(), filename

class ProfileGenerator(CADGenerator):
    """Generate Civil 3D-style profile views from alignment and surface data"""
    
    def __init__(self):
        super().__init__()
        self.alignment_points = []
        self.surface_triangles = []
    
    def parse_alignment_dxf(self, dxf_content: bytes) -> List[tuple]:
        """Extract alignment points from DXF LINE entities"""
        import tempfile
        import os
        
        # Write DXF to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf', mode='wb') as f:
            f.write(dxf_content)
            temp_path = f.name
        
        try:
            doc = ezdxf.readfile(temp_path)
            msp = doc.modelspace()
            
            points = []
            for entity in msp.query('LINE'):
                start = entity.dxf.start
                end = entity.dxf.end
                points.append((start.x, start.y))
                points.append((end.x, end.y))
            
            # Remove duplicates and sort by distance along path
            if points:
                unique_points = []
                for pt in points:
                    if pt not in unique_points:
                        unique_points.append(pt)
                return unique_points
            return []
        finally:
            os.unlink(temp_path)
    
    def parse_surface_dxf(self, dxf_content: bytes) -> List[Dict]:
        """Extract surface triangles from DXF 3DFACE entities"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf', mode='wb') as f:
            f.write(dxf_content)
            temp_path = f.name
        
        try:
            doc = ezdxf.readfile(temp_path)
            msp = doc.modelspace()
            
            triangles = []
            for entity in msp.query('3DFACE'):
                # Get the 4 vertices (3DFACE is actually a quad, but we treat as 2 triangles)
                p1 = entity.dxf.vtx0
                p2 = entity.dxf.vtx1
                p3 = entity.dxf.vtx2
                p4 = entity.dxf.vtx3 if hasattr(entity.dxf, 'vtx3') else p3
                
                triangles.append({
                    'p1': (p1.x, p1.y, p1.z),
                    'p2': (p2.x, p2.y, p2.z),
                    'p3': (p3.x, p3.y, p3.z),
                    'p4': (p4.x, p4.y, p4.z)
                })
            
            return triangles
        finally:
            os.unlink(temp_path)
    
    def sample_elevation_at_point(self, x: float, y: float, triangles: List[Dict]) -> float:
        """Sample elevation at a point using nearest triangle interpolation"""
        if not triangles:
            return 0.0
        
        # Find nearest triangle and interpolate elevation
        min_dist = float('inf')
        elevation = 0.0
        
        for tri in triangles:
            # Calculate centroid of triangle
            cx = (tri['p1'][0] + tri['p2'][0] + tri['p3'][0]) / 3
            cy = (tri['p1'][1] + tri['p2'][1] + tri['p3'][1]) / 3
            
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            
            if dist < min_dist:
                min_dist = dist
                # Use average elevation of triangle vertices
                elevation = (tri['p1'][2] + tri['p2'][2] + tri['p3'][2]) / 3
        
        return elevation
    
    def generate_profile_dxf(self, alignment_points: List[tuple], surface_triangles: List[Dict], 
                            h_scale: float = 1.0, v_scale: float = 1.0, v_exag: float = 10.0) -> tuple:
        """Generate profile view DXF with grid and ground line"""
        self.create_document()
        
        # Create layers
        layers = [
            {'name': 'PROFILE-GRID', 'color': 8},      # Gray - Grid
            {'name': 'PROFILE-MAJOR', 'color': 7},     # White - Major grid
            {'name': 'PROFILE-GROUND', 'color': 3},    # Green - Ground line
            {'name': 'PROFILE-TEXT', 'color': 7},      # White - Labels
            {'name': 'PROFILE-TITLE', 'color': 6}      # Cyan - Title
        ]
        self.create_layers(layers)
        
        # Create ROMANS text style
        self.doc.styles.add('ROMANS', font='romans.shx')
        
        # Calculate stations and elevations along alignment
        stations = []
        elevations = []
        cumulative_dist = 0.0
        
        for i in range(len(alignment_points)):
            x, y = alignment_points[i]
            
            # Sample elevation from surface
            elev = self.sample_elevation_at_point(x, y, surface_triangles)
            
            stations.append(cumulative_dist)
            elevations.append(elev)
            
            # Calculate distance to next point
            if i < len(alignment_points) - 1:
                next_x, next_y = alignment_points[i + 1]
                dist = math.sqrt((next_x - x)**2 + (next_y - y)**2)
                cumulative_dist += dist
        
        if not stations:
            stations = [0, 100, 200, 300]
            elevations = [100, 105, 103, 108]
        
        # Determine grid extents
        min_station = min(stations)
        max_station = max(stations)
        min_elev = min(elevations) - 5
        max_elev = max(elevations) + 5
        
        # Round to nice numbers
        min_elev = math.floor(min_elev / 5) * 5
        max_elev = math.ceil(max_elev / 5) * 5
        
        # Profile grid origin and size
        origin_x = 50
        origin_y = 50
        grid_width = (max_station - min_station) * h_scale
        grid_height = (max_elev - min_elev) * v_scale * v_exag
        
        # === DRAW PROFILE GRID ===
        # Outer border
        self.msp.add_lwpolyline([
            (origin_x, origin_y),
            (origin_x + grid_width, origin_y),
            (origin_x + grid_width, origin_y + grid_height),
            (origin_x, origin_y + grid_height),
            (origin_x, origin_y)
        ], dxfattribs={'layer': 'PROFILE-MAJOR', 'lineweight': 35})
        
        # Horizontal grid lines (elevations)
        elev_interval = 5
        for elev in range(int(min_elev), int(max_elev) + 1, elev_interval):
            y_pos = origin_y + (elev - min_elev) * v_scale * v_exag
            
            # Determine if major or minor grid
            is_major = (elev % 10 == 0)
            layer = 'PROFILE-MAJOR' if is_major else 'PROFILE-GRID'
            
            self.msp.add_line(
                (origin_x, y_pos),
                (origin_x + grid_width, y_pos),
                dxfattribs={'layer': layer}
            )
            
            # Elevation label
            self.msp.add_text(
                f"{elev:.0f}",
                dxfattribs={'layer': 'PROFILE-TEXT', 'height': 3.0, 'style': 'ROMANS'}
            ).set_placement((origin_x - 15, y_pos - 1))
        
        # Vertical grid lines (stations)
        station_interval = 50
        for sta in range(int(min_station), int(max_station) + 1, station_interval):
            x_pos = origin_x + (sta - min_station) * h_scale
            
            is_major = (sta % 100 == 0)
            layer = 'PROFILE-MAJOR' if is_major else 'PROFILE-GRID'
            
            self.msp.add_line(
                (x_pos, origin_y),
                (x_pos, origin_y + grid_height),
                dxfattribs={'layer': layer}
            )
            
            # Station label
            self.msp.add_text(
                f"{sta:.0f}",
                dxfattribs={'layer': 'PROFILE-TEXT', 'height': 3.0, 'style': 'ROMANS', 'rotation': 90}
            ).set_placement((x_pos - 1, origin_y - 8))
        
        # === DRAW GROUND LINE ===
        profile_points = []
        for sta, elev in zip(stations, elevations):
            x_pos = origin_x + (sta - min_station) * h_scale
            y_pos = origin_y + (elev - min_elev) * v_scale * v_exag
            profile_points.append((x_pos, y_pos))
        
        # Draw ground line as polyline
        if len(profile_points) >= 2:
            self.msp.add_lwpolyline(
                profile_points,
                dxfattribs={'layer': 'PROFILE-GROUND', 'lineweight': 35}
            )
        
        # Add elevation labels on ground line
        for i in range(0, len(profile_points), max(1, len(profile_points) // 5)):
            x, y = profile_points[i]
            elev = elevations[i]
            self.msp.add_text(
                f"{elev:.2f}",
                dxfattribs={'layer': 'PROFILE-TEXT', 'height': 2.5, 'style': 'ROMANS'}
            ).set_placement((x, y + 5))
        
        # === TITLE BLOCK ===
        title_y = origin_y + grid_height + 20
        
        self.msp.add_text(
            'PROFILE VIEW - GROUND LINE',
            dxfattribs={'layer': 'PROFILE-TITLE', 'height': 8.0, 'style': 'ROMANS'}
        ).set_placement((origin_x, title_y))
        
        self.msp.add_text(
            f'Horizontal Scale: 1:{int(1/h_scale)} | Vertical Scale: 1:{int(1/(v_scale*v_exag))} | V.E. = {v_exag}x',
            dxfattribs={'layer': 'PROFILE-TEXT', 'height': 4.0, 'style': 'ROMANS'}
        ).set_placement((origin_x, title_y - 10))
        
        # Axis labels
        self.msp.add_text(
            'STATION (ft)',
            dxfattribs={'layer': 'PROFILE-TEXT', 'height': 4.0, 'style': 'ROMANS'}
        ).set_placement((origin_x + grid_width/2 - 30, origin_y - 25))
        
        self.msp.add_text(
            'ELEVATION (ft)',
            dxfattribs={'layer': 'PROFILE-TEXT', 'height': 4.0, 'style': 'ROMANS', 'rotation': 90}
        ).set_placement((origin_x - 35, origin_y + grid_height/2 - 30))
        
        filename = "profile_view.dxf"
        return self.save_to_bytes(), filename

class ParkingLotGenerator(CADGenerator):
    """Generate parking lot layouts with striping, ADA spaces, and drainage"""
    
    def generate_dxf(self, data: Dict) -> tuple:
        """Generate parking lot DXF with striping and ADA compliance"""
        self.create_document()
        
        # Create layers
        layers = [
            {'name': 'LOT-BOUNDARY', 'color': 1},  # Red
            {'name': 'STRIPING', 'color': 7},      # White
            {'name': 'ADA-SPACES', 'color': 4},    # Cyan
            {'name': 'COMPACT-SPACES', 'color': 6}, # Magenta
            {'name': 'AISLES', 'color': 3},        # Green
            {'name': 'ISLANDS', 'color': 2},       # Yellow
            {'name': 'DRAINAGE', 'color': 5},      # Blue
            {'name': 'TEXT', 'color': 7},          # White
            {'name': 'DIMENSIONS', 'color': 8},    # Dark Gray
        ]
        self.create_layers(layers)
        
        # Extract parameters
        lot_length = data.get('lot_length', 300)
        lot_width = data.get('lot_width', 200)
        stall_width = data.get('stall_width', 9)
        stall_length = data.get('stall_length', 18)
        aisle_width = data.get('aisle_width', 24)
        parking_angle = data.get('parking_angle', 90)
        num_ada_spaces = data.get('num_ada_spaces', 4)
        compact_ratio = data.get('compact_ratio', 15)
        include_van_accessible = data.get('include_van_accessible', True)
        include_islands = data.get('include_islands', True)
        include_wheel_stops = data.get('include_wheel_stops', True)
        show_drainage = data.get('show_drainage', True)
        show_dimensions = data.get('show_dimensions', True)
        slope_percent = data.get('slope_percent', 1.5)
        
        # Draw lot boundary
        boundary = [
            (0, 0),
            (lot_length, 0),
            (lot_length, lot_width),
            (0, lot_width),
            (0, 0)
        ]
        self.msp.add_lwpolyline(boundary, dxfattribs={'layer': 'LOT-BOUNDARY'})
        
        # Calculate layout - stalls along length, on both sides of aisle
        stalls_per_side = int(lot_length / stall_width)
        total_stalls = stalls_per_side * 2  # Both north and south sides
        compact_stalls = int(total_stalls * compact_ratio / 100)
        ada_stalls = num_ada_spaces
        regular_stalls = max(0, total_stalls - compact_stalls - ada_stalls)
        
        # Draw drive aisle
        aisle_y = lot_width / 2 - aisle_width / 2
        self.msp.add_lwpolyline(
            [(0, aisle_y), (lot_length, aisle_y), (lot_length, aisle_y + aisle_width), (0, aisle_y + aisle_width), (0, aisle_y)],
            dxfattribs={'layer': 'AISLES'}
        )
        
        # Draw parking stalls - use standard width for all to match calculations
        x = 0
        ada_placed = 0
        compact_placed = 0
        
        # North side - draw stalls_per_side stalls
        for i in range(stalls_per_side):
            # Determine stall type for north side
            if ada_placed < ada_stalls:
                layer = 'ADA-SPACES'
                ada_placed += 1
            elif compact_placed < compact_stalls // 2:  # Split compact between sides
                layer = 'COMPACT-SPACES'
                compact_placed += 1
            else:
                layer = 'STRIPING'
            
            # North side stalls
            y1 = aisle_y + aisle_width
            y2 = lot_width
            
            self.msp.add_line((x, y1), (x, y2), dxfattribs={'layer': layer})
            self.msp.add_line((x + stall_width, y1), (x + stall_width, y2), dxfattribs={'layer': layer})
            
            # Add ADA symbol
            if layer == 'ADA-SPACES':
                text_x = x + stall_width / 2
                text_y = y1 + (y2 - y1) / 2
                self.msp.add_text(
                    '♿',
                    dxfattribs={'layer': 'ADA-SPACES', 'height': 4}
                ).set_placement((text_x - 2, text_y))
            
            # Add wheel stops
            if include_wheel_stops:
                self.msp.add_line(
                    (x + 0.5, y2 - 2), 
                    (x + stall_width - 0.5, y2 - 2),
                    dxfattribs={'layer': 'STRIPING'}
                )
            
            x += stall_width
        
        # South side - draw stalls_per_side stalls
        x = 0
        for i in range(stalls_per_side):
            # Determine stall type for south side
            if compact_placed < compact_stalls:
                layer = 'COMPACT-SPACES'
                compact_placed += 1
            else:
                layer = 'STRIPING'
            
            y1_south = 0
            y2_south = aisle_y
            
            self.msp.add_line((x, y1_south), (x, y2_south), dxfattribs={'layer': layer})
            self.msp.add_line((x + stall_width, y1_south), (x + stall_width, y2_south), dxfattribs={'layer': layer})
            
            if include_wheel_stops:
                self.msp.add_line(
                    (x + 0.5, 2), 
                    (x + stall_width - 0.5, 2),
                    dxfattribs={'layer': 'STRIPING'}
                )
            
            x += stall_width
        
        # Add landscape islands
        if include_islands:
            island_width = 10
            island_length = 20
            
            # Island at entrance
            island_x = 20
            island_y = aisle_y + aisle_width / 2 - island_width / 2
            
            self.msp.add_lwpolyline(
                [
                    (island_x, island_y),
                    (island_x + island_length, island_y),
                    (island_x + island_length, island_y + island_width),
                    (island_x, island_y + island_width),
                    (island_x, island_y)
                ],
                dxfattribs={'layer': 'ISLANDS'}
            )
            
            # Tree symbol
            center_x = island_x + island_length / 2
            center_y = island_y + island_width / 2
            self.msp.add_circle((center_x, center_y), 3, dxfattribs={'layer': 'ISLANDS'})
        
        # Add drainage arrows
        if show_drainage:
            arrow_spacing = 30
            for i in range(int(lot_length / arrow_spacing)):
                arrow_x = i * arrow_spacing + 15
                arrow_y = lot_width / 2
                
                # Simple arrow pointing to drainage
                self.msp.add_line(
                    (arrow_x, arrow_y - 5),
                    (arrow_x, arrow_y + 5),
                    dxfattribs={'layer': 'DRAINAGE'}
                )
                self.msp.add_line(
                    (arrow_x, arrow_y + 5),
                    (arrow_x - 2, arrow_y + 3),
                    dxfattribs={'layer': 'DRAINAGE'}
                )
                self.msp.add_line(
                    (arrow_x, arrow_y + 5),
                    (arrow_x + 2, arrow_y + 3),
                    dxfattribs={'layer': 'DRAINAGE'}
                )
            
            # Slope annotation
            self.msp.add_text(
                f'SLOPE: {slope_percent}%',
                dxfattribs={'layer': 'DRAINAGE', 'height': 3}
            ).set_placement((lot_length / 2 - 20, lot_width + 5))
        
        # Add dimensions
        if show_dimensions:
            # Lot dimensions
            self.msp.add_text(
                f"{lot_length:.0f}'",
                dxfattribs={'layer': 'DIMENSIONS', 'height': 3}
            ).set_placement((lot_length / 2 - 10, -10))
            
            self.msp.add_text(
                f"{lot_width:.0f}'",
                dxfattribs={'layer': 'DIMENSIONS', 'height': 3, 'rotation': 90}
            ).set_placement((-10, lot_width / 2 - 10))
            
            # Aisle width
            self.msp.add_text(
                f"AISLE: {aisle_width:.0f}'",
                dxfattribs={'layer': 'DIMENSIONS', 'height': 2.5}
            ).set_placement((10, aisle_y + aisle_width / 2 - 1))
        
        # Add title block
        self.msp.add_text(
            'PARKING LOT LAYOUT',
            dxfattribs={'layer': 'TEXT', 'height': 6}
        ).set_placement((lot_length / 2 - 40, lot_width + 15))
        
        self.msp.add_text(
            f'Total Spaces: {total_stalls} | ADA: {ada_stalls} | Regular: {regular_stalls} | Compact: {compact_stalls}',
            dxfattribs={'layer': 'TEXT', 'height': 3}
        ).set_placement((10, lot_width + 25))
        
        filename = "parking_lot_layout.dxf"
        return self.save_to_bytes(), filename

class RoadwayAlignmentGenerator(CADGenerator):
    """Generate roadway alignments with horizontal/vertical curves"""
    
    def generate_dxf(self, data: Dict) -> tuple:
        """Generate roadway alignment DXF"""
        self.create_document()
        
        # Create layers
        layers = [
            {'name': 'CENTERLINE', 'color': 1},  # Red
            {'name': 'EDGE-PAVEMENT', 'color': 3},  # Green
            {'name': 'STATIONING', 'color': 7},  # White
            {'name': 'LABELS', 'color': 4},  # Cyan
            {'name': 'DIMENSIONS', 'color': 8},  # Dark Gray
        ]
        self.create_layers(layers)
        
        alignment_type = data.get('alignment_type', 'Horizontal Alignment')
        curve_radius = data.get('curve_radius', 1000)
        curve_length = data.get('curve_length', 500)
        lane_width = data.get('lane_width', 12)
        show_stationing = data.get('show_stationing', True)
        station_interval = data.get('station_interval', 100)
        show_centerline = data.get('show_centerline', True)
        show_edge_lines = data.get('show_edge_lines', True)
        
        # Draw horizontal alignment
        if "Horizontal" in alignment_type or "Combined" in alignment_type:
            # Calculate curve parameters
            delta = curve_length / curve_radius  # in radians
            
            # Draw tangent approach
            tangent_length = 500
            self.msp.add_line((1000, 2000), (1500, 2000), dxfattribs={'layer': 'CENTERLINE'})
            
            # Draw circular curve
            num_points = 50
            curve_points = []
            for i in range(num_points + 1):
                angle = delta * i / num_points
                x = 1500 + curve_radius * np.sin(angle)
                y = 2000 + curve_radius * (1 - np.cos(angle))
                curve_points.append((x, y))
            
            self.msp.add_lwpolyline(curve_points, dxfattribs={'layer': 'CENTERLINE'})
            
            # Draw tangent departure
            end_x, end_y = curve_points[-1]
            end_angle = delta
            self.msp.add_line(
                (end_x, end_y),
                (end_x + 500 * np.cos(end_angle), end_y + 500 * np.sin(end_angle)),
                dxfattribs={'layer': 'CENTERLINE'}
            )
            
            # Add edge of pavement lines
            if show_edge_lines:
                half_width = lane_width / 2
                # Simplified edge lines parallel to centerline
                self.msp.add_line((1000, 2000 + half_width), (1500, 2000 + half_width), 
                                 dxfattribs={'layer': 'EDGE-PAVEMENT'})
                self.msp.add_line((1000, 2000 - half_width), (1500, 2000 - half_width), 
                                 dxfattribs={'layer': 'EDGE-PAVEMENT'})
            
            # Add stationing
            if show_stationing:
                for station in range(1000, 2500, int(station_interval)):
                    x = station
                    y = 2000 if station < 1500 else 2000  # Simplified
                    self.msp.add_text(
                        f"{station}+00",
                        dxfattribs={'layer': 'STATIONING', 'height': 5}
                    ).set_placement((x, y - 20))
            
            # Add labels
            self.msp.add_text(
                f'R={curve_radius:.0f}\'',
                dxfattribs={'layer': 'LABELS', 'height': 8}
            ).set_placement((1600, 2050))
            
            self.msp.add_text(
                f'L={curve_length:.0f}\'',
                dxfattribs={'layer': 'LABELS', 'height': 8}
            ).set_placement((1600, 2030))
        
        # Add title block
        self.msp.add_text(
            'ROADWAY HORIZONTAL ALIGNMENT',
            dxfattribs={'layer': 'LABELS', 'height': 10}
        ).set_placement((1200, 2150))
        
        filename = "roadway_alignment.dxf"
        return self.save_to_bytes(), filename
