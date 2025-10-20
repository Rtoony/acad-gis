import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Dict, List

class CADVisualizer:
    """Visualize CAD entities using matplotlib"""
    
    def __init__(self):
        self.fig_size = (12, 8)
        
    def plot_subdivision(self, data: Dict):
        """Plot subdivision layout"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        corners = data.get("property_corners", [])
        
        if corners:
            # Plot property boundary
            x_coords = [pt['x'] for pt in corners] + [corners[0]['x']]
            y_coords = [pt['y'] for pt in corners] + [corners[0]['y']]
            
            ax.plot(x_coords, y_coords, 'r-', linewidth=2, label='Property Lines')
            
            # Plot corner points
            for corner in corners:
                ax.plot(corner['x'], corner['y'], 'ro', markersize=8)
                ax.annotate(corner['point_id'], 
                           (corner['x'], corner['y']), 
                           xytext=(5, 5), 
                           textcoords='offset points')
            
            # Add bearing/distance labels
            for i in range(len(corners)):
                pt1 = corners[i]
                pt2 = corners[(i+1) % len(corners)]
                
                mid_x = (pt1['x'] + pt2['x']) / 2
                mid_y = (pt1['y'] + pt2['y']) / 2
                
                # Calculate distance
                distance = np.sqrt((pt2['x'] - pt1['x'])**2 + (pt2['y'] - pt1['y'])**2)
                
                ax.annotate(f"{distance:.1f}'", 
                           (mid_x, mid_y), 
                           ha='center', 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate (ft)')
        ax.set_ylabel('Y Coordinate (ft)')
        ax.set_title('Subdivision Layout Preview')
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_utilities(self, data: Dict, utility_type: str):
        """Plot utility network"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        pipes = data.get("pipes", [])
        structures = data.get("structures", [])
        
        # Plot pipes
        for pipe in pipes:
            # Handle both naming conventions: start_x/end_x OR from_x/to_x
            start_x = pipe.get('start_x', pipe.get('from_x'))
            start_y = pipe.get('start_y', pipe.get('from_y'))
            end_x = pipe.get('end_x', pipe.get('to_x'))
            end_y = pipe.get('end_y', pipe.get('to_y'))
            
            if start_x is not None and end_x is not None:
                ax.plot([start_x, end_x], 
                       [start_y, end_y], 
                       'b-', linewidth=3, label='Pipes' if pipe == pipes[0] else "")
                
                # Label pipe at midpoint
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                size = pipe.get('size', '?')
                material = pipe.get('material', '?')
                ax.annotate(f"{size}\" {material}", 
                           (mid_x, mid_y), 
                           ha='center',
                           bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue", alpha=0.8))
        
        # Plot structures
        for struct in structures:
            # Handle both id and struct_id
            struct_id = struct.get('id', struct.get('struct_id', '?'))
            
            circle = patches.Circle((struct['x'], struct['y']), 3, 
                                  facecolor='red', alpha=0.7, 
                                  label='Structures' if struct == structures[0] else "")
            ax.add_patch(circle)
            
            ax.annotate(struct_id, 
                       (struct['x'], struct['y']), 
                       ha='center', va='center', 
                       color='white', fontweight='bold')
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate (ft)')
        ax.set_ylabel('Y Coordinate (ft)')
        ax.set_title(f'{utility_type} Network Preview')
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_survey_points(self, data: Dict):
        """Plot survey points and connections"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        points = data.get("points", [])
        
        if not points:
            ax.text(0.5, 0.5, 'No survey points to display', 
                   ha='center', va='center', transform=ax.transAxes)
            return fig
        
        # Group points by description for color coding
        descriptions = list(set([p.get('description', 'UNKNOWN') for p in points]))
        colors = plt.cm.Set1(np.linspace(0, 1, len(descriptions)))
        color_map = dict(zip(descriptions, colors))
        
        # Plot points grouped by description
        grouped_points = {}
        for point in points:
            desc = point.get('description', 'UNKNOWN')
            if desc not in grouped_points:
                grouped_points[desc] = []
            grouped_points[desc].append(point)
        
        # Draw connections and points
        for desc, point_group in grouped_points.items():
            color = color_map[desc]
            
            # Plot points
            x_coords = [p['x'] for p in point_group]
            y_coords = [p['y'] for p in point_group]
            
            ax.scatter(x_coords, y_coords, c=[color], s=100, 
                      label=desc, alpha=0.8, edgecolors='black')
            
            # Connect points if more than one
            if len(point_group) >= 2:
                # Sort for logical connection
                point_group.sort(key=lambda p: (p['x'], p['y']))
                x_line = [p['x'] for p in point_group]
                y_line = [p['y'] for p in point_group]
                ax.plot(x_line, y_line, color=color, linewidth=2, alpha=0.6)
            
            # Label points
            for point in point_group:
                ax.annotate(point['point_id'], 
                           (point['x'], point['y']), 
                           xytext=(5, 5), 
                           textcoords='offset points',
                           fontsize=8)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate (ft)')
        ax.set_ylabel('Y Coordinate (ft)')
        ax.set_title('Survey Point Connections Preview')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        return fig
    
    def plot_plan_sheets(self, data: Dict):
        """Plot plan sheet layout overview"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        coverage = data.get("coverage", {})
        start_station = coverage.get("start_station", 0)
        end_station = coverage.get("end_station", 1000)
        sheet_length = coverage.get("sheet_length", 200)
        
        # Calculate sheet boundaries
        num_sheets = max(1, int(np.ceil((end_station - start_station) / sheet_length)))
        
        # Draw project extents
        ax.axvline(start_station, color='green', linewidth=3, label='Project Start')
        ax.axvline(end_station, color='red', linewidth=3, label='Project End')
        
        # Draw sheet boundaries
        for i in range(num_sheets + 1):
            station = start_station + (i * sheet_length)
            if station <= end_station:
                ax.axvline(station, color='blue', linestyle='--', alpha=0.7)
                
                if i < num_sheets:
                    # Label sheet
                    sheet_center = station + (sheet_length / 2)
                    ax.text(sheet_center, 0.5, f'Sheet C-{i+1:02d}', 
                           ha='center', va='center', 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"),
                           rotation=90)
        
        # Add coverage area visualization
        bounds = coverage.get("bounds", {})
        project_width = bounds.get("max_y", 500) - bounds.get("min_y", 0)
        
        for i in range(num_sheets):
            sheet_start = start_station + (i * sheet_length)
            sheet_end = min(sheet_start + sheet_length, end_station)
            
            rect = patches.Rectangle((sheet_start, -project_width/4), 
                                   sheet_end - sheet_start, 
                                   project_width/2,
                                   linewidth=1, edgecolor='blue', 
                                   facecolor='lightblue', alpha=0.3)
            ax.add_patch(rect)
        
        ax.set_xlim(start_station - 50, end_station + 50)
        ax.set_ylim(-project_width/2, project_width/2)
        ax.set_xlabel('Station (ft)')
        ax.set_ylabel('Project Width')
        ax.set_title(f'Plan Sheet Layout - {num_sheets} Sheets')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_3d_grading(self, data: Dict, grading_type: str):
        """Plot 3D grading surfaces with cut/fill visualization"""
        from mpl_toolkits.mplot3d import Axes3D
        
        fig = plt.figure(figsize=(14, 10))
        
        # Get grid data
        x_grid = np.array(data.get("x_grid", []))
        y_grid = np.array(data.get("y_grid", []))
        z_existing = np.array(data.get("z_existing", []))
        z_proposed = np.array(data.get("z_proposed", []))
        
        if x_grid.size == 0:
            # Fallback if no grid data
            ax = fig.add_subplot(111, projection='3d')
            ax.text(0.5, 0.5, 0.5, 'No grading data to display', 
                   ha='center', va='center')
            return fig
        
        # Create subplots for different views
        # 1. Existing surface
        ax1 = fig.add_subplot(2, 2, 1, projection='3d')
        surf1 = ax1.plot_surface(x_grid, y_grid, z_existing, 
                                 cmap='terrain', alpha=0.8, edgecolor='none')
        ax1.set_title('Existing Ground Surface')
        ax1.set_xlabel('X (ft)')
        ax1.set_ylabel('Y (ft)')
        ax1.set_zlabel('Elevation (ft)')
        fig.colorbar(surf1, ax=ax1, shrink=0.5)
        
        # 2. Proposed surface
        ax2 = fig.add_subplot(2, 2, 2, projection='3d')
        surf2 = ax2.plot_surface(x_grid, y_grid, z_proposed, 
                                 cmap='viridis', alpha=0.8, edgecolor='none')
        ax2.set_title('Proposed Grading Surface')
        ax2.set_xlabel('X (ft)')
        ax2.set_ylabel('Y (ft)')
        ax2.set_zlabel('Elevation (ft)')
        fig.colorbar(surf2, ax=ax2, shrink=0.5)
        
        # 3. Cut/Fill visualization
        ax3 = fig.add_subplot(2, 2, 3, projection='3d')
        cut_fill = z_proposed - z_existing
        surf3 = ax3.plot_surface(x_grid, y_grid, cut_fill, 
                                 cmap='RdBu_r', alpha=0.8, edgecolor='none',
                                 vmin=-5, vmax=5)
        ax3.set_title('Cut/Fill Map (Red=Cut, Blue=Fill)')
        ax3.set_xlabel('X (ft)')
        ax3.set_ylabel('Y (ft)')
        ax3.set_zlabel('Cut/Fill (ft)')
        fig.colorbar(surf3, ax=ax3, shrink=0.5, label='Cut (-) / Fill (+)')
        
        # 4. Both surfaces overlaid
        ax4 = fig.add_subplot(2, 2, 4, projection='3d')
        ax4.plot_surface(x_grid, y_grid, z_existing, 
                        cmap='Greys', alpha=0.4, edgecolor='none', label='Existing')
        ax4.plot_surface(x_grid, y_grid, z_proposed, 
                        cmap='Greens', alpha=0.6, edgecolor='none', label='Proposed')
        ax4.set_title('Existing vs Proposed Overlay')
        ax4.set_xlabel('X (ft)')
        ax4.set_ylabel('Y (ft)')
        ax4.set_zlabel('Elevation (ft)')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def visualize_parking_lot(data: Dict):
        """Visualize parking lot layout"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Extract parameters
        lot_length = data.get('lot_length', 300)
        lot_width = data.get('lot_width', 200)
        stall_width = data.get('stall_width', 9)
        stall_length = data.get('stall_length', 18)
        aisle_width = data.get('aisle_width', 24)
        num_ada_spaces = data.get('num_ada_spaces', 4)
        compact_ratio = data.get('compact_ratio', 15)
        include_islands = data.get('include_islands', True)
        include_wheel_stops = data.get('include_wheel_stops', True)
        
        # Set dark background (CAD-like theme)
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#2d2d2d')
        
        # Draw lot boundary
        boundary = patches.Rectangle((0, 0), lot_length, lot_width, 
                                     linewidth=3, edgecolor='red', 
                                     facecolor='#2d2d2d', label='Lot Boundary')
        ax.add_patch(boundary)
        
        # Draw drive aisle
        aisle_y = lot_width / 2 - aisle_width / 2
        aisle = patches.Rectangle((0, aisle_y), lot_length, aisle_width,
                                  linewidth=2, edgecolor='green',
                                  facecolor='#3d3d3d', alpha=0.7, label='Drive Aisle')
        ax.add_patch(aisle)
        
        # Calculate layout - stalls along length, on both sides of aisle
        stalls_per_side = int(lot_length / stall_width)
        total_stalls = stalls_per_side * 2  # Both north and south sides
        compact_stalls = int(total_stalls * compact_ratio / 100)
        ada_stalls = num_ada_spaces
        
        # Draw parking stalls - use standard width for all to match calculations
        x = 0
        ada_placed = 0
        compact_placed = 0
        ada_label_added = False
        compact_label_added = False
        
        # North side - draw stalls_per_side stalls
        for i in range(stalls_per_side):
            # Determine stall type for north side
            if ada_placed < ada_stalls:
                color = 'cyan'
                label = 'ADA Spaces' if not ada_label_added else ""
                ada_label_added = True
                ada_placed += 1
            elif compact_placed < compact_stalls // 2:  # Split compact between sides
                color = 'magenta'
                label = 'Compact Spaces' if not compact_label_added else ""
                compact_label_added = True
                compact_placed += 1
            else:
                color = 'white'
                label = ""
            
            # North side stalls
            y1 = aisle_y + aisle_width
            y2 = lot_width
            
            ax.plot([x, x], [y1, y2], color=color, linewidth=1.5, label=label)
            ax.plot([x + stall_width, x + stall_width], [y1, y2], color=color, linewidth=1.5)
            
            # Wheel stops
            if include_wheel_stops:
                ax.plot([x + 0.5, x + stall_width - 0.5], [y2 - 2, y2 - 2], 
                       color='yellow', linewidth=2)
            
            x += stall_width
        
        # South side - draw stalls_per_side stalls
        x = 0
        for i in range(stalls_per_side):
            # Determine stall type for south side
            if compact_placed < compact_stalls:
                color = 'magenta'
                compact_placed += 1
            else:
                color = 'white'
            
            y1_south = 0
            y2_south = aisle_y
            
            ax.plot([x, x], [y1_south, y2_south], color=color, linewidth=1.5)
            ax.plot([x + stall_width, x + stall_width], [y1_south, y2_south], 
                   color=color, linewidth=1.5)
            
            if include_wheel_stops:
                ax.plot([x + 0.5, x + stall_width - 0.5], [2, 2], 
                       color='yellow', linewidth=2)
            
            x += stall_width
        
        # Add landscape island
        if include_islands:
            island_width = 10
            island_length = 20
            island_x = 20
            island_y = aisle_y + aisle_width / 2 - island_width / 2
            
            island = patches.Rectangle((island_x, island_y), island_length, island_width,
                                      linewidth=2, edgecolor='yellow',
                                      facecolor='green', alpha=0.5, label='Landscape Island')
            ax.add_patch(island)
            
            # Tree circle
            circle = patches.Circle((island_x + island_length/2, island_y + island_width/2), 
                                   3, facecolor='darkgreen', edgecolor='yellow')
            ax.add_patch(circle)
        
        # Add title and labels
        ax.set_title('Parking Lot Layout Preview', color='white', fontsize=16, pad=20)
        ax.set_xlabel('Length (ft)', color='white', fontsize=12)
        ax.set_ylabel('Width (ft)', color='white', fontsize=12)
        
        # Style adjustments
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, color='gray')
        ax.tick_params(colors='white')
        
        # Legend
        ax.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='white', 
                 labelcolor='white', fontsize=10)
        
        # Add statistics text
        stats_text = f'Total: {total_stalls} spaces | ADA: {ada_stalls} | Compact: {compact_stalls}'
        ax.text(lot_length / 2, -15, stats_text, 
               ha='center', color='white', fontsize=12,
               bbox=dict(boxstyle='round', facecolor='#1e1e1e', edgecolor='white', pad=0.5))
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def visualize_roadway_alignment(data: Dict):
        """Visualize roadway alignment"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Set dark background
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#2d2d2d')
        
        alignment_type = data.get('alignment_type', 'Horizontal Alignment')
        curve_radius = data.get('curve_radius', 1000)
        curve_length = data.get('curve_length', 500)
        lane_width = data.get('lane_width', 12)
        
        if "Horizontal" in alignment_type or "Combined" in alignment_type:
            # Calculate curve
            delta = curve_length / curve_radius
            
            # Draw tangent approach
            ax.plot([1000, 1500], [2000, 2000], 'r-', linewidth=3, label='Centerline')
            
            # Draw curve
            num_points = 50
            curve_x = []
            curve_y = []
            for i in range(num_points + 1):
                angle = delta * i / num_points
                x = 1500 + curve_radius * np.sin(angle)
                y = 2000 + curve_radius * (1 - np.cos(angle))
                curve_x.append(x)
                curve_y.append(y)
            
            ax.plot(curve_x, curve_y, 'r-', linewidth=3)
            
            # Draw tangent departure
            end_x, end_y = curve_x[-1], curve_y[-1]
            ax.plot([end_x, end_x + 500 * np.cos(delta)], 
                   [end_y, end_y + 500 * np.sin(delta)], 'r-', linewidth=3)
            
            # Edge of pavement
            half_width = lane_width / 2
            ax.plot([1000, 1500], [2000 + half_width, 2000 + half_width], 
                   'g--', linewidth=2, label='Edge of Pavement')
            ax.plot([1000, 1500], [2000 - half_width, 2000 - half_width], 
                   'g--', linewidth=2)
            
            # Labels
            ax.text(1600, 2050, f'R={curve_radius:.0f}\'', 
                   color='cyan', fontsize=12, bbox=dict(boxstyle='round', facecolor='#1e1e1e', edgecolor='cyan'))
        
        ax.set_title('Roadway Alignment Preview', color='white', fontsize=16, pad=20)
        ax.set_xlabel('Station (ft)', color='white', fontsize=12)
        ax.set_ylabel('Offset (ft)', color='white', fontsize=12)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, color='gray')
        ax.tick_params(colors='white')
        ax.legend(loc='upper right', facecolor='#2d2d2d', edgecolor='white', 
                 labelcolor='white', fontsize=10)
        
        plt.tight_layout()
        return fig
