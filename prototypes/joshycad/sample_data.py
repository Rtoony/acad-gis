"""Sample data for CAD generation demonstrations"""

def get_subdivision_data():
    """Get sample subdivision property corner data"""
    return {
        "property_corners": [
            {"x": 0.0, "y": 0.0, "point_id": "P1"},
            {"x": 150.0, "y": 0.0, "point_id": "P2"},
            {"x": 150.0, "y": 100.0, "point_id": "P3"},
            {"x": 120.0, "y": 120.0, "point_id": "P4"},
            {"x": 80.0, "y": 120.0, "point_id": "P5"},
            {"x": 0.0, "y": 80.0, "point_id": "P6"}
        ],
        "buildings": [
            {"x": 50.0, "y": 30.0, "width": 40.0, "height": 25.0, "type": "residence"},
            {"x": 80.0, "y": 70.0, "width": 30.0, "height": 20.0, "type": "garage"}
        ]
    }

def get_utility_data(utility_type="water_system"):
    """Get sample utility network data"""
    
    if utility_type == "water_system":
        return {
            "pipes": [
                {"start_x": 0, "start_y": 50, "end_x": 100, "end_y": 50, "size": "8", "material": "DI", "length": 100},
                {"start_x": 100, "start_y": 50, "end_x": 200, "end_y": 50, "size": "6", "material": "DI", "length": 100},
                {"start_x": 200, "start_y": 50, "end_x": 250, "end_y": 75, "size": "6", "material": "DI", "length": 59},
                {"start_x": 100, "start_y": 50, "end_x": 100, "end_y": 150, "size": "4", "material": "DI", "length": 100}
            ],
            "structures": [
                {"x": 0, "y": 50, "id": "MH-1", "type": "connection", "size": "8\"", "rim_elev": 150.5, "invert_elev": 145.2},
                {"x": 100, "y": 50, "id": "MH-2", "type": "tee", "size": "8x6x4", "rim_elev": 151.2, "invert_elev": 145.8},
                {"x": 200, "y": 50, "id": "MH-3", "type": "bend", "size": "6\"", "rim_elev": 152.0, "invert_elev": 146.5},
                {"x": 250, "y": 75, "id": "V-1", "type": "valve", "size": "6\"", "rim_elev": 152.8, "invert_elev": 147.2},
                {"x": 100, "y": 150, "id": "HYD-1", "type": "hydrant", "size": "4\"", "rim_elev": 153.5, "invert_elev": 148.0}
            ]
        }
    
    elif utility_type == "sewer_system":
        return {
            "pipes": [
                {"start_x": 25, "start_y": 25, "end_x": 75, "end_y": 40, "size": "8", "material": "PVC", "length": 56},
                {"start_x": 75, "start_y": 40, "end_x": 125, "end_y": 55, "size": "8", "material": "PVC", "length": 56},
                {"start_x": 125, "start_y": 55, "end_x": 175, "end_y": 70, "size": "10", "material": "PVC", "length": 56},
                {"start_x": 175, "start_y": 70, "end_x": 225, "end_y": 85, "size": "12", "material": "PVC", "length": 56}
            ],
            "structures": [
                {"x": 25, "y": 25, "id": "MH-A", "type": "manhole", "size": "4'", "rim_elev": 148.5, "invert_elev": 142.3},
                {"x": 75, "y": 40, "id": "MH-B", "type": "manhole", "size": "4'", "rim_elev": 149.2, "invert_elev": 142.8},
                {"x": 125, "y": 55, "id": "MH-C", "type": "manhole", "size": "5'", "rim_elev": 150.0, "invert_elev": 143.2},
                {"x": 175, "y": 70, "id": "MH-D", "type": "manhole", "size": "5'", "rim_elev": 150.8, "invert_elev": 143.5},
                {"x": 225, "y": 85, "id": "MH-E", "type": "manhole", "size": "6'", "rim_elev": 151.5, "invert_elev": 143.8}
            ]
        }
    
    elif utility_type == "storm_drain":
        return {
            "pipes": [
                {"start_x": 50, "start_y": 200, "end_x": 100, "end_y": 150, "size": "18", "material": "RCP", "length": 71},
                {"start_x": 100, "start_y": 150, "end_x": 150, "end_y": 100, "size": "24", "material": "RCP", "length": 71},
                {"start_x": 150, "start_y": 100, "end_x": 200, "end_y": 50, "size": "30", "material": "RCP", "length": 71},
                {"start_x": 80, "start_y": 180, "end_x": 100, "end_y": 150, "size": "12", "material": "RCP", "length": 36}
            ],
            "structures": [
                {"x": 50, "y": 200, "id": "CB-1", "type": "catch_basin", "size": "Type D", "rim_elev": 155.0, "invert_elev": 148.5},
                {"x": 80, "y": 180, "id": "CB-2", "type": "catch_basin", "size": "Type D", "rim_elev": 154.5, "invert_elev": 148.2},
                {"x": 100, "y": 150, "id": "MH-1", "type": "junction", "size": "6'", "rim_elev": 154.0, "invert_elev": 147.8},
                {"x": 150, "y": 100, "id": "MH-2", "type": "manhole", "size": "6'", "rim_elev": 153.2, "invert_elev": 147.0},
                {"x": 200, "y": 50, "id": "OUT-1", "type": "outfall", "size": "30\"", "rim_elev": 152.5, "invert_elev": 146.2}
            ]
        }
    
    else:  # gas_lines
        return {
            "pipes": [
                {"start_x": 0, "start_y": 25, "end_x": 50, "end_y": 25, "size": "4", "material": "PE", "length": 50},
                {"start_x": 50, "start_y": 25, "end_x": 100, "end_y": 25, "size": "4", "material": "PE", "length": 50},
                {"start_x": 100, "start_y": 25, "end_x": 150, "end_y": 25, "size": "2", "material": "PE", "length": 50},
                {"start_x": 50, "start_y": 25, "end_x": 50, "end_y": 75, "size": "2", "material": "PE", "length": 50}
            ],
            "structures": [
                {"x": 0, "y": 25, "id": "REG-1", "type": "regulator", "size": "4\"", "rim_elev": 149.5, "invert_elev": 146.0},
                {"x": 50, "y": 25, "id": "TEE-1", "type": "tee", "size": "4x2", "rim_elev": 150.0, "invert_elev": 146.5},
                {"x": 100, "y": 25, "id": "VAL-1", "type": "valve", "size": "4\"", "rim_elev": 150.5, "invert_elev": 147.0},
                {"x": 150, "y": 25, "id": "CAP-1", "type": "cap", "size": "2\"", "rim_elev": 151.0, "invert_elev": 147.5},
                {"x": 50, "y": 75, "id": "MTR-1", "type": "meter", "size": "2\"", "rim_elev": 151.5, "invert_elev": 148.0}
            ]
        }

def get_survey_data():
    """Get sample survey point data"""
    return {
        "points": [
            {"x": 0.0, "y": 50.0, "point_id": "101", "description": "TOP_CURB", "elevation": 100.25},
            {"x": 25.0, "y": 52.0, "point_id": "102", "description": "TOP_CURB", "elevation": 100.45},
            {"x": 50.0, "y": 54.0, "point_id": "103", "description": "TOP_CURB", "elevation": 100.65},
            {"x": 75.0, "y": 56.0, "point_id": "104", "description": "TOP_CURB", "elevation": 100.85},
            {"x": 100.0, "y": 58.0, "point_id": "105", "description": "TOP_CURB", "elevation": 101.05},
            
            {"x": 0.0, "y": 45.0, "point_id": "201", "description": "BACK_CURB", "elevation": 100.75},
            {"x": 25.0, "y": 47.0, "point_id": "202", "description": "BACK_CURB", "elevation": 100.95},
            {"x": 50.0, "y": 49.0, "point_id": "203", "description": "BACK_CURB", "elevation": 101.15},
            {"x": 75.0, "y": 51.0, "point_id": "204", "description": "BACK_CURB", "elevation": 101.35},
            {"x": 100.0, "y": 53.0, "point_id": "205", "description": "BACK_CURB", "elevation": 101.55},
            
            {"x": 0.0, "y": 40.0, "point_id": "301", "description": "SIDEWALK", "elevation": 101.00},
            {"x": 25.0, "y": 42.0, "point_id": "302", "description": "SIDEWALK", "elevation": 101.20},
            {"x": 50.0, "y": 44.0, "point_id": "303", "description": "SIDEWALK", "elevation": 101.40},
            {"x": 75.0, "y": 46.0, "point_id": "304", "description": "SIDEWALK", "elevation": 101.60},
            {"x": 100.0, "y": 48.0, "point_id": "305", "description": "SIDEWALK", "elevation": 101.80},
            
            {"x": 0.0, "y": 60.0, "point_id": "401", "description": "EDGE_PAVEMENT", "elevation": 100.00},
            {"x": 25.0, "y": 62.0, "point_id": "402", "description": "EDGE_PAVEMENT", "elevation": 100.20},
            {"x": 50.0, "y": 64.0, "point_id": "403", "description": "EDGE_PAVEMENT", "elevation": 100.40},
            {"x": 75.0, "y": 66.0, "point_id": "404", "description": "EDGE_PAVEMENT", "elevation": 100.60},
            {"x": 100.0, "y": 68.0, "point_id": "405", "description": "EDGE_PAVEMENT", "elevation": 100.80}
        ]
    }

def get_plan_sheet_data():
    """Get sample plan sheet project data"""
    return {
        "project_name": "Main Street Reconstruction",
        "project_number": "2024-CS-001",
        "engineer": "Sarah Johnson, PE",
        "sheet_size": "D (24x36)",
        "scale": "1\"=20'",
        "coverage": {
            "start_station": 0,
            "end_station": 1200,
            "sheet_length": 200,
            "bounds": {
                "min_x": 0,
                "max_x": 1200,
                "min_y": 0,
                "max_y": 400
            }
        }
    }

def get_grading_data(grading_type="building_pad"):
    """Get sample 3D grading data"""
    import numpy as np
    
    if grading_type == "building_pad":
        # Create a grid of points for a building pad
        x = np.linspace(0, 100, 11)
        y = np.linspace(0, 80, 9)
        X, Y = np.meshgrid(x, y)
        
        # Existing ground with slope
        Z_existing = 95 + 0.05 * X + 0.03 * Y + np.random.randn(*X.shape) * 0.3
        
        # Proposed pad at elevation 100
        Z_proposed = np.full_like(Z_existing, 100.0)
        
        grid_points = []
        for i in range(len(x)):
            for j in range(len(y)):
                grid_points.append({
                    "x": X[j, i],
                    "y": Y[j, i],
                    "existing_z": Z_existing[j, i],
                    "proposed_z": Z_proposed[j, i],
                    "point_id": f"G{i}{j}"
                })
        
        return {
            "grid_points": grid_points,
            "cell_area": 100,  # 10ft x 10ft grid
            "x_grid": X.tolist(),
            "y_grid": Y.tolist(),
            "z_existing": Z_existing.tolist(),
            "z_proposed": Z_proposed.tolist()
        }
    
    elif grading_type == "road_grading":
        # Create road profile with crown
        x = np.linspace(0, 500, 51)  # Station length
        y = np.linspace(-40, 40, 17)  # Cross-section width
        X, Y = np.meshgrid(x, y)
        
        # Existing ground
        Z_existing = 100 + 0.02 * X + np.random.randn(*X.shape) * 0.2
        
        # Proposed road with crown
        Z_proposed = 100 + 0.02 * X - 0.02 * np.abs(Y)
        
        grid_points = []
        for i in range(len(x)):
            for j in range(len(y)):
                grid_points.append({
                    "x": X[j, i],
                    "y": Y[j, i],
                    "existing_z": Z_existing[j, i],
                    "proposed_z": Z_proposed[j, i],
                    "point_id": f"R{i}{j}"
                })
        
        return {
            "grid_points": grid_points,
            "cell_area": 50,  # 10ft x 5ft grid
            "x_grid": X.tolist(),
            "y_grid": Y.tolist(),
            "z_existing": Z_existing.tolist(),
            "z_proposed": Z_proposed.tolist()
        }
    
    elif grading_type == "site_grading":
        # General site grading
        x = np.linspace(0, 200, 21)
        y = np.linspace(0, 150, 16)
        X, Y = np.meshgrid(x, y)
        
        # Existing ground with undulations
        Z_existing = 98 + 0.04 * X + 0.02 * Y + 2 * np.sin(X/20) * np.cos(Y/25)
        
        # Proposed grading to smooth surface
        Z_proposed = 98 + 0.04 * X + 0.02 * Y
        
        grid_points = []
        for i in range(len(x)):
            for j in range(len(y)):
                grid_points.append({
                    "x": X[j, i],
                    "y": Y[j, i],
                    "existing_z": Z_existing[j, i],
                    "proposed_z": Z_proposed[j, i],
                    "point_id": f"S{i}{j}"
                })
        
        return {
            "grid_points": grid_points,
            "cell_area": 100,
            "x_grid": X.tolist(),
            "y_grid": Y.tolist(),
            "z_existing": Z_existing.tolist(),
            "z_proposed": Z_proposed.tolist()
        }
    
    else:  # detention_basin
        # Create a detention basin
        x = np.linspace(0, 120, 13)
        y = np.linspace(0, 80, 9)
        X, Y = np.meshgrid(x, y)
        
        # Existing ground
        Z_existing = 105 + 0.01 * X + 0.01 * Y
        
        # Proposed basin (bowl shape)
        center_x, center_y = 60, 40
        Z_proposed = 100 + 0.005 * ((X - center_x)**2 + (Y - center_y)**2) / 100
        
        grid_points = []
        for i in range(len(x)):
            for j in range(len(y)):
                grid_points.append({
                    "x": X[j, i],
                    "y": Y[j, i],
                    "existing_z": Z_existing[j, i],
                    "proposed_z": Z_proposed[j, i],
                    "point_id": f"B{i}{j}"
                })
        
        return {
            "grid_points": grid_points,
            "cell_area": 100,
            "x_grid": X.tolist(),
            "y_grid": Y.tolist(),
            "z_existing": Z_existing.tolist(),
            "z_proposed": Z_proposed.tolist()
        }
