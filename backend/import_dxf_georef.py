"""
Enhanced DXF Import with Georeferencing Detection
Automatically detects if a DXF is in CA State Plane Zone 2 coordinates

Usage:
    python import_dxf_georef.py --file site_plan.dxf --project-id <uuid>
    python import_dxf_georef.py --file topo_survey.dxf --project-id <uuid> --force-georef
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import ezdxf
from pyproj import Transformer
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent))
    from database import (  # type: ignore
        create_drawing,
        create_layer,
        create_block_insert,
        create_block_definition,
        get_project,
        get_block_definition,
        execute_query,
        clear_canonical_features,
        insert_canonical_feature,
    )
else:
    from .database import (  # type: ignore
        create_drawing,
        create_layer,
        create_block_insert,
        create_block_definition,
        get_project,
        get_block_definition,
        execute_query,
        clear_canonical_features,
        insert_canonical_feature,
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
    
    def __init__(
        self,
        dxf_path: str,
        project_id: str,
        force_georef: bool = False,
        override_epsg: Optional[int] = None,
        override_coordinate_system: Optional[str] = None
    ):
        self.dxf_path = Path(dxf_path)
        self.project_id = project_id
        self.force_georef = force_georef
        self.doc = None
        self.drawing_id = None
        self.is_georeferenced = False
        self.epsg_code = None
        self.coordinate_system = None
        self.override_epsg = override_epsg
        self.override_coordinate_system = override_coordinate_system
        self.transformer: Optional[Transformer] = None
        self.stats = {
            'layers': 0,
            'blocks': 0,
            'inserts': 0,
            'entities': 0,
            'canonical_features': 0
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

        if self.override_epsg:
            epsg = int(self.override_epsg)
            label = self.override_coordinate_system or f"EPSG:{epsg}"
            print(f"  📌 Using override EPSG: {epsg} ({label})")
            return True, epsg, label
        
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

        if self.override_epsg:
            self.is_georeferenced = True
            self.epsg_code = int(self.override_epsg)
            if not self.coordinate_system:
                self.coordinate_system = (
                    self.override_coordinate_system or f"EPSG:{self.epsg_code}"
                )

        if self.is_georeferenced and self.epsg_code:
            self._ensure_transformer()
        
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
            json.dumps(metadata),
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

    def _ensure_transformer(self):
        """Prepare a CRS transformer when georeferencing is available."""
        if not self.is_georeferenced or not self.epsg_code:
            self.transformer = None
            return

        if self.transformer is not None:
            return

        try:
            self.transformer = Transformer.from_crs(
                f"EPSG:{self.epsg_code}",
                "EPSG:4326",
                always_xy=True
            )
        except Exception as exc:
            print(f"  ⚠️  Failed to initialise transformer: {exc}")
            self.transformer = None

    @staticmethod
    def _format_number(value: float) -> str:
        """Format coordinates with sensible precision."""
        return f"{value:.8f}".rstrip('0').rstrip('.') if abs(value) < 1e6 else f"{value:.3f}"

    def _point_wkt(self, coord: Tuple[float, float]) -> Optional[str]:
        if not coord:
            return None
        x, y = coord
        return f"POINT ({self._format_number(x)} {self._format_number(y)})"

    def _linestring_wkt(self, coords: List[Tuple[float, float]]) -> Optional[str]:
        if not coords or len(coords) < 2:
            return None
        pairs = ", ".join(
            f"{self._format_number(x)} {self._format_number(y)}" for x, y in coords
        )
        return f"LINESTRING ({pairs})"

    def _polygon_wkt(self, coords: List[Tuple[float, float]]) -> Optional[str]:
        if not coords or len(coords) < 4:
            return None
        if coords[0] != coords[-1]:
            coords = coords + [coords[0]]
        pairs = ", ".join(
            f"{self._format_number(x)} {self._format_number(y)}" for x, y in coords
        )
        return f"POLYGON (({pairs}))"

    def _transform_coords(
        self,
        coords: List[Tuple[float, float]]
    ) -> Optional[List[Tuple[float, float]]]:
        """Transform coordinates to EPSG:4326 if possible."""
        if not coords or not self.transformer:
            return None
        transformed: List[Tuple[float, float]] = []
        for x, y in coords:
            try:
                lon, lat = self.transformer.transform(x, y)
                transformed.append((lon, lat))
            except Exception:
                return None
        return transformed

    def _extract_canonical_feature(
        self,
        entity
    ) -> Optional[Tuple[str, Optional[str], Optional[str], Optional[str], Dict[str, Any]]]:
        """Convert a DXF entity into native/canonical WKTs."""
        entity_type = entity.dxftype()
        layer_name = getattr(entity.dxf, "layer", None)
        handle = getattr(entity.dxf, "handle", None)

        metadata: Dict[str, Any] = {
            "source": "dxf_import",
            "entity_type": entity_type,
            "layer": layer_name,
            "handle": handle
        }

        try:
            if entity_type == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                coords = [(start.x, start.y), (end.x, end.y)]
                native_wkt = self._linestring_wkt(coords)
                canonical_coords = self._transform_coords(coords)
                canonical_wkt = self._linestring_wkt(canonical_coords) if canonical_coords else None
                return ("line", layer_name, native_wkt, canonical_wkt, metadata)

            if entity_type == "LWPOLYLINE":
                coords = [(x, y) for x, y, *_ in entity.get_points("xyseb")]
                is_closed = bool(entity.closed)
                metadata["closed"] = is_closed
                if is_closed and len(coords) >= 3:
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    native_wkt = self._polygon_wkt(coords)
                    canonical_coords = self._transform_coords(coords)
                    canonical_wkt = self._polygon_wkt(canonical_coords) if canonical_coords else None
                    return ("polygon", layer_name, native_wkt, canonical_wkt, metadata)
                native_wkt = self._linestring_wkt(coords)
                canonical_coords = self._transform_coords(coords)
                canonical_wkt = self._linestring_wkt(canonical_coords) if canonical_coords else None
                return ("line", layer_name, native_wkt, canonical_wkt, metadata)

            if entity_type == "POLYLINE":
                coords = []
                for vertex in entity.vertices():
                    loc = vertex.dxf.location
                    coords.append((loc.x, loc.y))
                is_closed = bool(entity.is_closed)
                metadata["closed"] = is_closed
                if is_closed and len(coords) >= 3:
                    if coords[0] != coords[-1]:
                        coords.append(coords[0])
                    native_wkt = self._polygon_wkt(coords)
                    canonical_coords = self._transform_coords(coords)
                    canonical_wkt = self._polygon_wkt(canonical_coords) if canonical_coords else None
                    return ("polygon", layer_name, native_wkt, canonical_wkt, metadata)
                native_wkt = self._linestring_wkt(coords)
                canonical_coords = self._transform_coords(coords)
                canonical_wkt = self._linestring_wkt(canonical_coords) if canonical_coords else None
                return ("line", layer_name, native_wkt, canonical_wkt, metadata)

            if entity_type == "POINT":
                location = entity.dxf.location
                coord = (location.x, location.y)
                native_wkt = self._point_wkt(coord)
                canonical_coords = self._transform_coords([coord])
                canonical_wkt = None
                if canonical_coords:
                    canonical_wkt = self._point_wkt(canonical_coords[0])
                return ("point", layer_name, native_wkt, canonical_wkt, metadata)

            if entity_type == "INSERT":
                insert = entity.dxf.insert
                coord = (insert.x, insert.y)
                metadata["block_name"] = entity.dxf.name
                metadata["has_attributes"] = bool(getattr(entity, "attribs", []))
                native_wkt = self._point_wkt(coord)
                canonical_coords = self._transform_coords([coord])
                canonical_wkt = None
                if canonical_coords:
                    canonical_wkt = self._point_wkt(canonical_coords[0])
                return ("symbol", layer_name, native_wkt, canonical_wkt, metadata)

            if entity_type in {"TEXT", "MTEXT"}:
                insert = getattr(entity.dxf, "insert", None)
                if insert is None:
                    return None
                coord = (insert.x, insert.y)
                text_value = getattr(entity.dxf, "text", None) or getattr(entity, "text", None)
                metadata["text"] = text_value
                native_wkt = self._point_wkt(coord)
                canonical_coords = self._transform_coords([coord])
                canonical_wkt = None
                if canonical_coords:
                    canonical_wkt = self._point_wkt(canonical_coords[0])
                return ("label", layer_name, native_wkt, canonical_wkt, metadata)
        except Exception as exc:
            metadata["error"] = str(exc)
            return None

        return None

    def import_canonical_geometry(self):
        """Populate canonical_features from the DXF model space."""
        print(f"\n🌐 Writing canonical geometries...")

        try:
            clear_canonical_features(self.drawing_id)
        except Exception as exc:
            print(f"  ✗ Failed to clear existing canonical features: {exc}")
            return

        # Refresh transformer in case overrides were applied
        self._ensure_transformer()

        msp = self.doc.modelspace()
        inserted = 0
        skipped = 0

        for entity in msp:
            feature = self._extract_canonical_feature(entity)
            if not feature:
                continue

            feature_type, layer_name, native_wkt, canonical_wkt, metadata = feature
            if not native_wkt and not canonical_wkt:
                skipped += 1
                continue

            try:
                insert_canonical_feature(
                    drawing_id=self.drawing_id,
                    project_id=self.project_id,
                    feature_type=feature_type,
                    layer_name=layer_name,
                    native_wkt=native_wkt,
                    native_srid=self.epsg_code if self.is_georeferenced else None,
                    canonical_wkt=canonical_wkt,
                    metadata=metadata
                )
                inserted += 1
            except Exception as exc:
                skipped += 1
                print(f"  ✗ Failed to store canonical {feature_type}: {exc}")

        self.stats['canonical_features'] = inserted
        if inserted:
            print(f"✅ Canonical features stored: {inserted}")
        else:
            print("ℹ️  No canonical geometries were generated.")
        if skipped:
            print(f"   ⚠️  Skipped {skipped} entities. See logs for details.")
    
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
        self.import_canonical_geometry()
        
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
        print(f"Canonical Feat: {self.stats['canonical_features']}")
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
