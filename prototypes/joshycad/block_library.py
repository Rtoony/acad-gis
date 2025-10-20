import ezdxf
from ezdxf.enums import TextEntityAlignment

class CivilBlockLibrary:
    """
    Library of standard civil engineering CAD blocks.
    Includes both model space symbols and paper space annotation elements.
    """
    
    @staticmethod
    def create_all_blocks(doc):
        """Create all civil engineering blocks in the DXF document"""
        CivilBlockLibrary.create_model_space_blocks(doc)
        CivilBlockLibrary.create_paper_space_blocks(doc)
    
    @staticmethod
    def create_model_space_blocks(doc):
        """Create model space utility and survey symbols"""
        
        # 1. SANITARY MANHOLE
        block = doc.blocks.new(name='MH_SANITARY')
        block.add_circle(center=(0, 0), radius=2.0, dxfattribs={'color': 1})
        block.add_circle(center=(0, 0), radius=1.5, dxfattribs={'color': 1})
        block.add_text('MH', dxfattribs={'height': 0.8, 'color': 1}).set_placement((0, -0.3), align=TextEntityAlignment.CENTER)
        
        # 2. STORM DRAIN INLET
        block = doc.blocks.new(name='INLET_STORM')
        block.add_lwpolyline([(0, -2), (2, 0), (0, 2), (-2, 0)], close=True, dxfattribs={'color': 6})
        block.add_text('SD', dxfattribs={'height': 0.8, 'color': 6}).set_placement((0, -0.3), align=TextEntityAlignment.CENTER)
        
        # 3. WATER VALVE
        block = doc.blocks.new(name='VALVE_WATER')
        block.add_circle(center=(0, 0), radius=1.5, dxfattribs={'color': 4})
        block.add_line((-1.5, 0), (1.5, 0), dxfattribs={'color': 4})
        block.add_line((0, -1.5), (0, 1.5), dxfattribs={'color': 4})
        block.add_text('WV', dxfattribs={'height': 0.6, 'color': 4}).set_placement((0, 2), align=TextEntityAlignment.CENTER)
        
        # 4. FIRE HYDRANT
        block = doc.blocks.new(name='HYDRANT')
        block.add_circle(center=(0, 0), radius=1.2, dxfattribs={'color': 1})
        block.add_lwpolyline([(-0.8, -0.8), (-0.8, 0.8), (0.8, 0.8), (0.8, -0.8)], close=True, dxfattribs={'color': 1})
        block.add_text('FH', dxfattribs={'height': 0.6, 'color': 1}).set_placement((0, -0.2), align=TextEntityAlignment.CENTER)
        
        # 5. WATER METER
        block = doc.blocks.new(name='WATER_METER')
        block.add_lwpolyline([(-1.5, -1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, 1.5)], close=True, dxfattribs={'color': 4})
        block.add_circle(center=(0, 0), radius=1.0, dxfattribs={'color': 4})
        block.add_text('WM', dxfattribs={'height': 0.6, 'color': 4}).set_placement((0, -0.2), align=TextEntityAlignment.CENTER)
        
        # 6. GAS VALVE
        block = doc.blocks.new(name='VALVE_GAS')
        block.add_circle(center=(0, 0), radius=1.3, dxfattribs={'color': 30})
        block.add_lwpolyline([(-1, 0), (0, 0.8), (1, 0), (0, -0.8)], close=True, dxfattribs={'color': 30})
        block.add_text('GV', dxfattribs={'height': 0.5, 'color': 30}).set_placement((0, 1.8), align=TextEntityAlignment.CENTER)
        
        # 7. CATCH BASIN
        block = doc.blocks.new(name='CATCH_BASIN')
        block.add_lwpolyline([(-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8)], close=True, dxfattribs={'color': 6})
        block.add_lwpolyline([(-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2)], close=True, dxfattribs={'color': 6})
        block.add_text('CB', dxfattribs={'height': 0.8, 'color': 6}).set_placement((0, -0.3), align=TextEntityAlignment.CENTER)
        
        # 8. CLEANOUT
        block = doc.blocks.new(name='CLEANOUT')
        block.add_circle(center=(0, 0), radius=1.0, dxfattribs={'color': 3})
        block.add_text('CO', dxfattribs={'height': 0.6, 'color': 3}).set_placement((0, -0.2), align=TextEntityAlignment.CENTER)
        
        # 9. UTILITY POLE
        block = doc.blocks.new(name='UTILITY_POLE')
        block.add_circle(center=(0, 0), radius=0.8, dxfattribs={'color': 8})
        block.add_line((-1.2, -1.2), (1.2, 1.2), dxfattribs={'color': 8})
        block.add_line((-1.2, 1.2), (1.2, -1.2), dxfattribs={'color': 8})
        block.add_text('UP', dxfattribs={'height': 0.5, 'color': 8}).set_placement((0, 1.5), align=TextEntityAlignment.CENTER)
        
        # 10. STREET LIGHT
        block = doc.blocks.new(name='STREET_LIGHT')
        block.add_circle(center=(0, 0), radius=1.0, dxfattribs={'color': 51})
        block.add_circle(center=(0, 0), radius=0.4, dxfattribs={'color': 51})
        for angle in [0, 90, 180, 270]:
            import math
            x = 0.7 * math.cos(math.radians(angle))
            y = 0.7 * math.sin(math.radians(angle))
            block.add_line((0, 0), (x, y), dxfattribs={'color': 51})
        block.add_text('SL', dxfattribs={'height': 0.4, 'color': 51}).set_placement((0, 1.5), align=TextEntityAlignment.CENTER)
        
        # 11. SURVEY MONUMENT
        block = doc.blocks.new(name='MONUMENT')
        block.add_lwpolyline([(0, 1.5), (-1.3, -0.75), (1.3, -0.75)], close=True, dxfattribs={'color': 1})
        block.add_circle(center=(0, 0), radius=0.5, dxfattribs={'color': 1})
        block.add_text('MON', dxfattribs={'height': 0.5, 'color': 1}).set_placement((0, -2.2), align=TextEntityAlignment.CENTER)
        
        # 12. BENCHMARK
        block = doc.blocks.new(name='BENCHMARK')
        block.add_lwpolyline([(-1.5, -1.5), (1.5, -1.5), (1.5, 1.5), (-1.5, 1.5)], close=True, dxfattribs={'color': 2})
        block.add_lwpolyline([(-1.5, -1.5), (1.5, 1.5)], dxfattribs={'color': 2})
        block.add_lwpolyline([(-1.5, 1.5), (1.5, -1.5)], dxfattribs={'color': 2})
        block.add_text('BM', dxfattribs={'height': 0.6, 'color': 2}).set_placement((0, -2.5), align=TextEntityAlignment.CENTER)
        
        # 13. PROPERTY CORNER
        block = doc.blocks.new(name='PROPERTY_CORNER')
        block.add_circle(center=(0, 0), radius=0.8, dxfattribs={'color': 41})
        block.add_line((-1.2, 0), (1.2, 0), dxfattribs={'color': 41})
        block.add_line((0, -1.2), (0, 1.2), dxfattribs={'color': 41})
        block.add_text('PC', dxfattribs={'height': 0.5, 'color': 41}).set_placement((0, 1.5), align=TextEntityAlignment.CENTER)
        
        # 14. DECIDUOUS TREE
        block = doc.blocks.new(name='TREE_DECIDUOUS')
        block.add_circle(center=(0, 0), radius=2.5, dxfattribs={'color': 92})
        for i in range(8):
            import math
            angle = i * 45
            x = 2.0 * math.cos(math.radians(angle))
            y = 2.0 * math.sin(math.radians(angle))
            block.add_circle(center=(x, y), radius=1.2, dxfattribs={'color': 92})
        block.add_lwpolyline([(-0.3, 0), (-0.3, -3), (0.3, -3), (0.3, 0)], close=True, dxfattribs={'color': 8})
        
        # 15. SIGN POST
        block = doc.blocks.new(name='SIGN_POST')
        block.add_lwpolyline([(-2, 2), (2, 2), (2, -2), (-2, -2)], close=True, dxfattribs={'color': 30})
        block.add_lwpolyline([(-0.2, -2), (-0.2, -4), (0.2, -4), (0.2, -2)], dxfattribs={'color': 8})
        block.add_text('SIGN', dxfattribs={'height': 0.8, 'color': 30}).set_placement((0, 0), align=TextEntityAlignment.CENTER)
    
    @staticmethod
    def create_paper_space_blocks(doc):
        """Create paper space annotation blocks"""
        
        # 16. NORTH ARROW
        block = doc.blocks.new(name='NORTH_ARROW')
        # Arrow shaft
        block.add_line((0, -8), (0, 8), dxfattribs={'color': 7, 'lineweight': 35})
        # Arrow head
        block.add_lwpolyline([(0, 8), (-1.5, 5), (1.5, 5)], close=True, dxfattribs={'color': 7})
        # Tail
        block.add_lwpolyline([(-1, -8), (0, -5), (1, -8)], close=True, dxfattribs={'color': 7})
        # Circle
        block.add_circle(center=(0, 0), radius=3, dxfattribs={'color': 7})
        # N label
        block.add_text('N', dxfattribs={'height': 2.5, 'color': 7}).set_placement((0, 9), align=TextEntityAlignment.CENTER)
        
        # 17. SCALE BAR (GRAPHIC SCALE)
        block = doc.blocks.new(name='SCALE_BAR')
        # Bar outline
        block.add_lwpolyline([(0, 0), (20, 0), (20, 2), (0, 2)], close=True, dxfattribs={'color': 7})
        # Divisions
        for i in range(5):
            x = i * 5
            block.add_line((x, 0), (x, 2), dxfattribs={'color': 7})
            if i % 2 == 0:
                block.add_lwpolyline([(x, 0), (x+5, 0), (x+5, 2), (x, 2)], close=True, dxfattribs={'color': 7, 'layer': 'HATCH'})
        # Labels
        block.add_text('0', dxfattribs={'height': 1.2, 'color': 7}).set_placement((0, -2), align=TextEntityAlignment.CENTER)
        block.add_text('50\'', dxfattribs={'height': 1.2, 'color': 7}).set_placement((10, -2), align=TextEntityAlignment.CENTER)
        block.add_text('100\'', dxfattribs={'height': 1.2, 'color': 7}).set_placement((20, -2), align=TextEntityAlignment.CENTER)
        block.add_text('GRAPHIC SCALE', dxfattribs={'height': 0.8, 'color': 7}).set_placement((10, 3.5), align=TextEntityAlignment.CENTER)
        
        # 18. TITLE BLOCK (24x36)
        block = doc.blocks.new(name='TITLE_BLOCK_24X36')
        # Border
        block.add_lwpolyline([(0, 0), (36, 0), (36, 24), (0, 24)], close=True, dxfattribs={'color': 7, 'lineweight': 50})
        # Title block area
        block.add_lwpolyline([(0, 0), (36, 0), (36, 5), (0, 5)], close=True, dxfattribs={'color': 7})
        # Divisions
        block.add_line((0, 3), (36, 3), dxfattribs={'color': 7})
        block.add_line((0, 1.5), (15, 1.5), dxfattribs={'color': 7})
        block.add_line((15, 0), (15, 5), dxfattribs={'color': 7})
        block.add_line((25, 0), (25, 3), dxfattribs={'color': 7})
        # Labels
        block.add_text('PROJECT TITLE', dxfattribs={'height': 1.2, 'color': 7}).set_placement((18, 3.5), align=TextEntityAlignment.CENTER)
        block.add_text('SHEET NAME', dxfattribs={'height': 0.8, 'color': 7}).set_placement((7.5, 2), align=TextEntityAlignment.CENTER)
        block.add_text('DRAWN BY:', dxfattribs={'height': 0.5, 'color': 7}).set_placement((1, 1), align=TextEntityAlignment.LEFT)
        block.add_text('DATE:', dxfattribs={'height': 0.5, 'color': 7}).set_placement((1, 0.5), align=TextEntityAlignment.LEFT)
        block.add_text('SCALE:', dxfattribs={'height': 0.5, 'color': 7}).set_placement((16, 2), align=TextEntityAlignment.LEFT)
        block.add_text('SHEET', dxfattribs={'height': 0.8, 'color': 7}).set_placement((30, 1.5), align=TextEntityAlignment.CENTER)
        
        # 19. LEGEND FRAME
        block = doc.blocks.new(name='LEGEND_FRAME')
        # Frame
        block.add_lwpolyline([(0, 0), (15, 0), (15, 20), (0, 20)], close=True, dxfattribs={'color': 7, 'lineweight': 25})
        # Title bar
        block.add_lwpolyline([(0, 18), (15, 18), (15, 20), (0, 20)], close=True, dxfattribs={'color': 7})
        block.add_text('LEGEND', dxfattribs={'height': 1.2, 'color': 7}).set_placement((7.5, 18.5), align=TextEntityAlignment.CENTER)
        # Sample legend items
        y_positions = [16, 14, 12, 10, 8, 6]
        labels = ['EXISTING UTILITY', 'PROPOSED UTILITY', 'PROPERTY LINE', 'EASEMENT', 'BUILDING', 'PAVEMENT']
        colors = [8, 1, 41, 30, 5, 3]
        for i, (y, label, color) in enumerate(zip(y_positions, labels, colors)):
            block.add_line((1, y), (3, y), dxfattribs={'color': color, 'lineweight': 25})
            block.add_text(label, dxfattribs={'height': 0.8, 'color': 7}).set_placement((4, y-0.3), align=TextEntityAlignment.LEFT)
        
        # 20. MATCH LINE
        block = doc.blocks.new(name='MATCH_LINE')
        # Match line with arrows
        block.add_line((-20, 0), (20, 0), dxfattribs={'color': 7, 'lineweight': 50, 'linetype': 'PHANTOM'})
        # Left arrow
        block.add_lwpolyline([(-20, 0), (-18, 1), (-18, -1)], close=True, dxfattribs={'color': 7})
        # Right arrow
        block.add_lwpolyline([(20, 0), (18, 1), (18, -1)], close=True, dxfattribs={'color': 7})
        # Label
        block.add_text('MATCH LINE - SEE SHEET __', dxfattribs={'height': 1.5, 'color': 7}).set_placement((0, 2), align=TextEntityAlignment.CENTER)
        
    @staticmethod
    def insert_block(msp, block_name, location, scale=1.0, rotation=0, attributes=None):
        """
        Insert a block into model space with optional attributes
        
        Args:
            msp: ModelSpace object
            block_name: Name of block to insert
            location: (x, y) or (x, y, z) tuple
            scale: Scale factor (default 1.0)
            rotation: Rotation angle in degrees (default 0)
            attributes: Dictionary of attribute values (optional)
        
        Returns:
            Block reference entity
        """
        blockref = msp.add_blockref(
            block_name,
            location,
            dxfattribs={
                'xscale': scale,
                'yscale': scale,
                'rotation': rotation
            }
        )
        
        if attributes:
            for key, value in attributes.items():
                try:
                    blockref.add_attrib(key, str(value), (0, 0))
                except:
                    pass
        
        return blockref
    
    @staticmethod
    def get_block_descriptions():
        """Return descriptions of all available blocks"""
        return {
            # Model Space Symbols
            'MH_SANITARY': 'Sanitary sewer manhole - circular with MH label',
            'INLET_STORM': 'Storm drain inlet - diamond shape with SD label',
            'VALVE_WATER': 'Water valve - circle with crosshairs and WV label',
            'HYDRANT': 'Fire hydrant - circle with square and FH label',
            'WATER_METER': 'Water meter - square with circle and WM label',
            'VALVE_GAS': 'Gas valve - circle with diamond and GV label',
            'CATCH_BASIN': 'Catch basin - nested squares with CB label',
            'CLEANOUT': 'Cleanout - simple circle with CO label',
            'UTILITY_POLE': 'Utility pole - circle with crossed lines and UP label',
            'STREET_LIGHT': 'Street light - circle with radiating lines and SL label',
            'MONUMENT': 'Survey monument - triangle with circle and MON label',
            'BENCHMARK': 'Survey benchmark - crossed square with BM label',
            'PROPERTY_CORNER': 'Property corner - circle with crosshairs and PC label',
            'TREE_DECIDUOUS': 'Deciduous tree - stylized tree with circular canopy',
            'SIGN_POST': 'Sign post - rectangle on pole with SIGN label',
            
            # Paper Space Elements
            'NORTH_ARROW': 'North arrow - directional arrow with N label',
            'SCALE_BAR': 'Graphic scale bar - 0 to 100 feet with divisions',
            'TITLE_BLOCK_24X36': 'Title block for 24x36 sheet with fields',
            'LEGEND_FRAME': 'Legend frame with sample entries',
            'MATCH_LINE': 'Match line with arrows for sheet matching'
        }
