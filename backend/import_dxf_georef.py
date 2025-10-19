"""
Enhanced DXF Import with Georeferencing Detection
Automatically detects if a DXF is in CA State Plane Zone 2 coordinates

Usage:
    python import_dxf_georef.py --file site_plan.dxf --project-id <uuid>
    python import_dxf_georef.py --file topo_survey.dxf --project-id <uuid> --force-georef
"""

import argparse
import ezdxf
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from database import (
    create_drawing, create_layer, create_block_insert,
    create_block_definition, get_project, get_block_definition,
    execute_query
)

class GeoreferencedDXFImporter:
    """Import DXF files with automatic georeferencing detection."""
    
    # Expected coordinate ranges for EPSG:2226 (CA State Plane Zone 2)
    # Sonoma County typical ranges:
    # X: ~6,200,000 to 6,350,000 (US Survey Feet)
    # Y: ~2,050,000 to 2,200,000 (US Survey Feet)
    
    EPSG_2226_X_MIN = 6000000
    EPSG_2226_X_MAX = 6500000
    EPSG_2226_Y_MIN = 1900000
    EPSG_2226_Y_MAX = 2300000
    
    def __init__(self, dxf_path: str, project_id: str, force_georef: bool = False):
        self.dxf_path = Path(dxf_path)
        self.project_id = project_id
        self.force_georef = force_georef
        self.doc = None
        self.drawing_id = None
        self.is_georeferenced = False
        self.epsg_code = None
        self.coordinate_system = None
        self.stats = {
            'layers': 0,
            'blocks': 0,
            'inserts': 0,
            'entities': 0
        }
    
    def load_dxf(self):
        """Load DXF file."""
        print(f"📂 Loading DXF file: {self.dxf_path}")
        
        try:
            self.doc = ezdxf.readfile(str(self.dxf_path))
            print(f"✅ Loaded DXF version: {self.doc.dxfversion}")
        except Exception as e:
            raise Exception(f"Failed to load DXF: {e}")
    
    def detect_georeferencing(self) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Detect if the DXF file contains georeferenced coordinates.
        
        Returns:
            Tuple of (is_georeferenced, epsg_code, coordinate_system_name)
        """
        
        print(f"\n🔍 Analyzing coordinate system...")
        
        # Method 1: Check DXF header variables for coordinate system info
        try:
            # Try to get EPSG code from DXF header (if present)
            if hasattr(self.doc.header, '$GEOGRAPHICMODE'):
                geographic_mode = self.doc.header.get('$GEOGRAPHICMODE')
                if geographic_mode:
                    print("  📍 DXF has geographic mode enabled")
        except:
            pass
        
        # Method 2: Analyze coordinate ranges of all entities
        x_coords = []
        y_coords = []
        
        msp = self.doc.modelspace()
        
        # Sample block inserts (most common entities)
        for entity in msp.query('INSERT'):
            try:
                x_coords.append(entity.dxf.insert.x)
                y_coords.append(entity.dxf.insert.y)
            except:
                pass
        
        # Sample other entities (lines, polylines, etc.)
        for entity in msp.query('LINE'):
            try:
                x_coords.append(entity.dxf.start.x)
                y_coords.append(entity.dxf.end.x)
                y_coords.append(entity.dxf.start.y)
                y_coords.append(entity.dxf.end.y)
            except:
                pass
        
        if not x_coords or not y_coords:
            print("  ⚠️  No coordinate data found in DXF")
            return False, None, None
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        print(f"  📊 Coordinate ranges:")
        print(f"     X: {min_x:,.2f} to {max_x:,.2f}")
        print(f"     Y: {min_y:,.2f} to {max_y:,.2f}")
        
        # Check if coordinates fall within CA State Plane Zone 2 range
        is_in_epsg_2226 = (
            self.EPSG_2226_X_MIN <= min_x <= self.EPSG_2226_X_MAX and
            self.EPSG_2226_X_MIN <= max_x <= self.EPSG_2226_X_MAX and
            self.EPSG_2226_Y_MIN <= min_y <= self.EPSG_2226_Y_MAX and
            self.EPSG_2226_Y_MIN <= max_y <= self.EPSG_2226_Y_MAX
        )
        
        if is_in_epsg_2226 or self.force_georef:
            print(f"  ✅ Coordinates match EPSG:2226 (CA State Plane Zone 2)")
            return True, 2226, "NAD83 / California zone 2 (ftUS)"
        else:
            print(f"  ℹ️  Coordinates do not match EPSG:2226 range")
            print(f"  ℹ️  Drawing will use local CAD coordinates")
            return False, None, None
    
    def store_raw_dxf(self, drawing_name: str, drawing_type: str = None) -> str:
        """Store the raw DXF content and create drawing record."""
        
        print(f"\n💾 Creating drawing record...")
        
        # Detect georeferencing
        self.is_georeferenced, self.epsg_code, self.coordinate_system = self.detect_georeferencing()
        
        # Read raw DXF content
        with open(self.dxf_path, 'r', encoding='utf-8', errors='ignore') as f:
            dxf_content = f.read()
        
        # Extract metadata
        metadata = {
            'dxf_version': self.doc.dxfversion,
            'filename': self.dxf_path.name,
            'units': str(self.doc.units) if hasattr(self.doc, 'units') else 'Unknown',
            'layer_count': len(self.doc.layers),
            'block_count': len([b for b in self.doc.blocks if not b.name.startswith('*')]),
            'is_georeferenced': self.is_georeferenced,
            'epsg_code': self.epsg_code,
            'coordinate_system': self.coordinate_system
        }
        
        # Get drawing scale from viewport if available
        scale = self.extract_scale()
        
        # Create drawing with georeferencing info
        query = """
            INSERT INTO drawings (
                drawing_id, project_id, drawing_name, drawing_number,
                drawing_type, scale, dxf_content, description, tags, metadata,
                is_georeferenced, drawing_epsg_code, drawing_coordinate_system,
                cad_units
            ) VALUES (
                gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb,
                %s, %s, %s, %s
            )
            RETURNING drawing_id
        """
        
        result = execute_query(query, (
            self.project_id,
            drawing_name,
            self.extract_drawing_number(),
            drawing_type or "UNKNOWN",
            scale,
            dxf_content,
            f"Imported from {self.dxf_path.name}",
            None,  # tags
            str(metadata).replace("'", '"'),  # metadata as json string
            self.is_georeferenced,
            self.epsg_code,
            self.coordinate_system,
            'US Survey Feet'
        ), fetch=True)
        
        self.drawing_id = result[0]['drawing_id']
        
        print(f"✅ Drawing created: {self.drawing_id}")
        if self.is_georeferenced:
            print(f"   🗺️  Georeferenced: {self.coordinate_system} (EPSG:{self.epsg_code})")
        else:
            print(f"   📐 Using local CAD coordinates")
        
        return self.drawing_id
    
    def extract_scale(self) -> str:
        """Try to extract scale from drawing."""
        return "1:1"  # Default
    
    def extract_drawing_number(self) -> str:
        """Try to extract drawing number from title block."""
        return None
    
    def import_layers(self):
        """Import all layers from DXF."""
        
        print(f"\n📑 Importing layers...")
        
        for layer in self.doc.layers:
            try:
                layer_name = layer.dxf.name
                color = layer.dxf.color if hasattr(layer.dxf, 'color') else 7
                linetype = layer.dxf.linetype if hasattr(layer.dxf, 'linetype') else 'CONTINUOUS'
                lineweight = getattr(layer.dxf, 'lineweight', 0.25)
                
                if lineweight > 0:
                    lineweight = lineweight / 100.0
                else:
                    lineweight = 0.25
                
                create_layer(
                    drawing_id=self.drawing_id,
                    layer_name=layer_name,
                    color=color,
                    linetype=linetype,
                    lineweight=lineweight,
                    is_locked=layer.is_locked(),
                    is_frozen=layer.is_frozen()
                )
                
                self.stats['layers'] += 1
                print(f"  ✓ {layer_name}")
                
            except Exception as e:
                print(f"  ✗ Failed to import layer {layer.dxf.name}: {e}")
        
        print(f"✅ Imported {self.stats['layers']} layers")
    
    def import_blocks(self):
        """Import block definitions from DXF."""
        
        print(f"\n🔷 Importing block definitions...")
        
        for block in self.doc.blocks:
            if block.name.startswith('*'):
                continue
            
            try:
                existing = get_block_definition(block.name)
                if existing:
                    print(f"  ⭐ {block.name} (already exists)")
                    continue
                
                svg_content = self.block_to_svg(block)
                
                parts = block.name.split('.')
                if len(parts) >= 3:
                    domain, category = parts[0], parts[1]
                else:
                    domain, category = 'CUSTOM', 'IMPORTED'
                
                create_block_definition(
                    block_name=block.name,
                    svg_content=svg_content,
                    domain=domain,
                    category=category,
                    semantic_type=block.name,
                    semantic_label=block.name.replace('_', ' ').title(),
                    usage_context=f"Block imported from {self.dxf_path.name}",
                    tags=[domain, category, 'IMPORTED'],
                    metadata={'source': 'dxf_import', 'georeferenced': self.is_georeferenced}
                )
                
                self.stats['blocks'] += 1
                print(f"  ✓ {block.name}")
                
            except Exception as e:
                print(f"  ✗ Failed to import block {block.name}: {e}")
        
        print(f"✅ Imported {self.stats['blocks']} block definitions")
    
    def block_to_svg(self, block) -> str:
        """Convert DXF block to SVG placeholder."""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <title>{block.name}</title>
    <rect x="10" y="10" width="80" height="80" fill="none" stroke="black" stroke-width="2"/>
    <text x="50" y="55" text-anchor="middle" font-size="12">{block.name}</text>
</svg>'''
        return svg
    
    def import_block_inserts(self):
        """Import block insert placements."""
        
        print(f"\n🔹 Importing block inserts...")
        
        msp = self.doc.modelspace()
        
        for entity in msp.query('INSERT'):
            try:
                create_block_insert(
                    drawing_id=self.drawing_id,
                    block_name=entity.dxf.name,
                    insert_x=entity.dxf.insert.x,
                    insert_y=entity.dxf.insert.y,
                    insert_z=entity.dxf.insert.z if hasattr(entity.dxf.insert, 'z') else 0,
                    scale_x=entity.dxf.xscale,
                    scale_y=entity.dxf.yscale,
                    rotation=entity.dxf.rotation,
                    layer_name=entity.dxf.layer,
                    metadata={
                        'handle': entity.dxf.handle,
                        'has_attributes': len(entity.attribs) > 0,
                        'layer': entity.dxf.layer
                    }
                )
                
                self.stats['inserts'] += 1
                
                if self.stats['inserts'] % 10 == 0:
                    print(f"  ... {self.stats['inserts']} inserts imported")
                
            except Exception as e:
                print(f"  ✗ Failed to import insert: {e}")
        
        print(f"✅ Imported {self.stats['inserts']} block inserts")
    
    def import_other_entities(self):
        """Count other entities."""
        
        print(f"\n📊 Counting other entities...")
        
        msp = self.doc.modelspace()
        entity_counts = {}
        
        for entity in msp:
            entity_type = entity.dxftype()
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        print(f"  Entity breakdown:")
        for entity_type, count in sorted(entity_counts.items()):
            print(f"    {entity_type}: {count}")
        
        self.stats['entities'] = sum(entity_counts.values())
        
        print(f"ℹ️  Note: Entities are stored in raw DXF content")
    
    def run(self, drawing_name: str = None, drawing_type: str = None):
        """Run the full import process."""
        
        print("="*60)
        print("GEOREFERENCED DXF IMPORT")
        print("="*60)
        
        # Verify project exists
        project = get_project(self.project_id)
        if not project:
            raise Exception(f"Project not found: {self.project_id}")
        
        print(f"🗂️ Project: {project['project_name']}")
        
        # Load DXF
        self.load_dxf()
        
        # Store raw DXF and create drawing (includes georef detection)
        if not drawing_name:
            drawing_name = self.dxf_path.stem
        
        self.store_raw_dxf(drawing_name, drawing_type)
        
        # Import components
        self.import_layers()
        self.import_blocks()
        self.import_block_inserts()
        self.import_other_entities()
        
        # Summary
        print("\n" + "="*60)
        print("IMPORT SUMMARY")
        print("="*60)
        print(f"Drawing ID:     {self.drawing_id}")
        print(f"Drawing Name:   {drawing_name}")
        print(f"Georeferenced:  {'YES ✅' if self.is_georeferenced else 'NO'}")
        if self.is_georeferenced:
            print(f"EPSG Code:      {self.epsg_code}")
            print(f"Coord System:   {self.coordinate_system}")
        print(f"Layers:         {self.stats['layers']}")
        print(f"Blocks:         {self.stats['blocks']}")
        print(f"Inserts:        {self.stats['inserts']}")
        print(f"Total Entities: {self.stats['entities']}")
        print("="*60)
        print(f"\n✅ Import complete! Drawing stored in database.")
        
        if self.is_georeferenced:
            print(f"\n🗺️  This drawing can be viewed with GIS basemaps and overlays!")
        
        return self.drawing_id


def main():
    parser = argparse.ArgumentParser(
        description='Import DXF file with georeferencing detection'
    )
    parser.add_argument('--file', type=str, required=True, help='Path to DXF file')
    parser.add_argument('--project-id', type=str, required=True, help='Project UUID')
    parser.add_argument('--name', type=str, help='Drawing name (default: filename)')
    parser.add_argument('--type', type=str, help='Drawing type (e.g., "SITE PLAN")')
    parser.add_argument(
        '--force-georef', 
        action='store_true',
        help='Force georeferencing even if coordinates are outside expected range'
    )
    
    args = parser.parse_args()
    
    # Run import
    importer = GeoreferencedDXFImporter(
        args.file, 
        args.project_id,
        force_georef=args.force_georef
    )
    importer.run(args.name, args.type)


if __name__ == "__main__":
    main()
