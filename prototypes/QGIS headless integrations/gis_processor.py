"""
GIS Processor Module for ACAD=GIS
Provides PyQGIS (headless QGIS) integration for advanced GIS operations.

This module initializes QGIS in headless mode and provides high-level
functions for spatial analysis, data transformation, and GIS processing.

Usage:
    from gis_processor import QGISProcessor
    
    processor = QGISProcessor()
    result = processor.buffer_features(
        layer_id='some-uuid',
        distance=100,
        segments=5
    )
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager
from datetime import datetime

# Database imports
from database import (
    get_db_connection,
    execute_query,
    execute_single,
    DB_CONFIG
)

# QGIS imports (only imported if QGIS is available)
QGIS_AVAILABLE = False
try:
    from qgis.core import (
        QgsApplication,
        QgsProject,
        QgsVectorLayer,
        QgsRasterLayer,
        QgsDataSourceUri,
        QgsCoordinateReferenceSystem,
        QgsCoordinateTransform,
        QgsFeature,
        QgsGeometry,
        QgsPointXY,
        QgsField,
        QgsFields,
        QgsVectorFileWriter,
        QgsFeatureRequest,
        QgsExpression,
        QgsExpressionContext,
        QgsExpressionContextUtils,
        Qgs
    )
    from qgis.analysis import QgsNativeAlgorithms
    from processing.core.Processing import Processing
    import processing
    
    QGIS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  QGIS not available: {e}")
    print("   GIS processing features will be disabled.")
    print("   To enable: Install QGIS and set QGIS_PREFIX_PATH")


class QGISNotAvailableError(Exception):
    """Raised when QGIS operations are attempted but QGIS is not installed."""
    pass


class QGISProcessor:
    """
    Main class for QGIS processing operations.
    
    Manages QGIS application lifecycle and provides high-level GIS operations.
    Uses PostGIS database as the primary data source.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one QGIS instance."""
        if cls._instance is None:
            cls._instance = super(QGISProcessor, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize QGIS processor (only once)."""
        if not QGIS_AVAILABLE:
            raise QGISNotAvailableError(
                "QGIS is not available. Please install QGIS and configure environment."
            )
        
        if not self._initialized:
            self._init_qgis()
            self._initialized = True
    
    def _init_qgis(self):
        """Initialize QGIS application and processing framework."""
        print("🗺️  Initializing QGIS...")
        
        # Create QGIS application (headless mode)
        self.app = QgsApplication([], False)
        
        # Initialize QGIS
        self.app.initQgis()
        
        # Initialize processing framework
        Processing.initialize()
        
        # Add processing algorithms
        QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
        
        # Create empty project
        self.project = QgsProject.instance()
        
        print("✅ QGIS initialized successfully")
        
        # Cache available algorithms
        self._cache_algorithms()
    
    def _cache_algorithms(self):
        """Cache available QGIS algorithms for quick access."""
        self.algorithms = {}
        
        for alg in QgsApplication.processingRegistry().algorithms():
            self.algorithms[alg.id()] = {
                'name': alg.displayName(),
                'description': alg.shortDescription(),
                'group': alg.group(),
                'tags': alg.tags()
            }
        
        print(f"📚 Cached {len(self.algorithms)} QGIS algorithms")
    
    def list_algorithms(self, group: Optional[str] = None, 
                       search: Optional[str] = None) -> List[Dict]:
        """
        List available QGIS algorithms.
        
        Args:
            group: Filter by algorithm group (e.g., 'Vector geometry')
            search: Search term to filter algorithms
            
        Returns:
            List of algorithm metadata dictionaries
        """
        results = []
        
        for alg_id, info in self.algorithms.items():
            # Filter by group
            if group and info['group'] != group:
                continue
            
            # Filter by search term
            if search:
                search_lower = search.lower()
                if not (
                    search_lower in info['name'].lower() or
                    search_lower in info['description'].lower() or
                    any(search_lower in tag.lower() for tag in info['tags'])
                ):
                    continue
            
            results.append({
                'id': alg_id,
                **info
            })
        
        return results
    
    def _get_postgis_layer(self, table_name: str, 
                          geom_column: str = 'geom',
                          layer_name: Optional[str] = None) -> QgsVectorLayer:
        """
        Load a PostGIS layer into QGIS.
        
        Args:
            table_name: Name of PostGIS table
            geom_column: Name of geometry column
            layer_name: Optional display name for layer
            
        Returns:
            QgsVectorLayer connected to PostGIS
        """
        # Build connection URI
        uri = QgsDataSourceUri()
        uri.setConnection(
            DB_CONFIG['host'],
            str(DB_CONFIG['port']),
            DB_CONFIG['database'],
            DB_CONFIG['user'],
            DB_CONFIG['password']
        )
        
        # Set data source (schema.table)
        schema = 'public'
        uri.setDataSource(schema, table_name, geom_column)
        
        # Create layer
        display_name = layer_name or table_name
        layer = QgsVectorLayer(uri.uri(), display_name, 'postgres')
        
        if not layer.isValid():
            raise Exception(f"Failed to load PostGIS layer: {table_name}")
        
        return layer
    
    def _get_layer_by_id(self, layer_id: str) -> QgsVectorLayer:
        """
        Get a QGIS layer from database using layer_id.
        
        This is a helper that queries the database to find which table
        the layer corresponds to, then loads it.
        """
        # Query to find layer metadata
        query = """
            SELECT 
                table_name,
                geom_column,
                layer_name
            FROM layer_metadata 
            WHERE layer_id = %s
        """
        
        result = execute_single(query, (layer_id,))
        
        if not result:
            # For now, assume canonical_features table for most operations
            # This should be enhanced with proper layer metadata tracking
            return self._get_postgis_layer('canonical_features', 'geometry', layer_id)
        
        return self._get_postgis_layer(
            result['table_name'],
            result['geom_column'],
            result['layer_name']
        )
    
    def _save_layer_to_postgis(self, layer: QgsVectorLayer, 
                              table_name: str,
                              overwrite: bool = False) -> bool:
        """
        Save a QGIS layer back to PostGIS.
        
        Args:
            layer: QGIS vector layer to save
            table_name: Target table name in PostGIS
            overwrite: Whether to overwrite existing table
            
        Returns:
            True if successful
        """
        # Build connection options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = 'PostgreSQL'
        options.layerName = table_name
        
        if overwrite:
            options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
        
        # Build connection string
        connection_string = (
            f"PG: host={DB_CONFIG['host']} "
            f"port={DB_CONFIG['port']} "
            f"dbname={DB_CONFIG['database']} "
            f"user={DB_CONFIG['user']} "
            f"password={DB_CONFIG['password']}"
        )
        
        # Write layer
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer,
            connection_string,
            QgsCoordinateTransformContext(),
            options
        )
        
        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"Failed to save layer: {error}")
        
        return True
    
    # ============================================
    # HIGH-LEVEL GIS OPERATIONS
    # ============================================
    
    def buffer_features(self, 
                       source_table: str,
                       distance: float,
                       segments: int = 5,
                       dissolve: bool = False,
                       output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Create buffer around features.
        
        Args:
            source_table: Source PostGIS table
            distance: Buffer distance (in layer units)
            segments: Number of segments for circle approximation
            dissolve: Whether to dissolve overlapping buffers
            output_table: Output table name (auto-generated if None)
            
        Returns:
            Dictionary with operation results
        """
        print(f"🔵 Creating buffer: distance={distance}, segments={segments}")
        
        # Load source layer
        source_layer = self._get_postgis_layer(source_table)
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"{source_table}_buffer_{timestamp}"
        
        # Run QGIS processing algorithm
        params = {
            'INPUT': source_layer,
            'DISTANCE': distance,
            'SEGMENTS': segments,
            'DISSOLVE': dissolve,
            'OUTPUT': 'memory:'  # First create in memory
        }
        
        result = processing.run("native:buffer", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        # Get feature count
        feature_count = output_layer.featureCount()
        
        print(f"✅ Buffer created: {feature_count} features → {output_table}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'operation': 'buffer',
            'parameters': {
                'distance': distance,
                'segments': segments,
                'dissolve': dissolve
            }
        }
    
    def clip_layer(self,
                   input_table: str,
                   clip_table: str,
                   output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Clip features by another layer.
        
        Args:
            input_table: Input PostGIS table
            clip_table: Clip boundary PostGIS table
            output_table: Output table name
            
        Returns:
            Dictionary with operation results
        """
        print(f"✂️  Clipping {input_table} by {clip_table}")
        
        # Load layers
        input_layer = self._get_postgis_layer(input_table)
        clip_layer = self._get_postgis_layer(clip_table)
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"{input_table}_clipped_{timestamp}"
        
        # Run clip algorithm
        params = {
            'INPUT': input_layer,
            'OVERLAY': clip_layer,
            'OUTPUT': 'memory:'
        }
        
        result = processing.run("native:clip", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        feature_count = output_layer.featureCount()
        
        print(f"✅ Clip complete: {feature_count} features → {output_table}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'operation': 'clip'
        }
    
    def intersection(self,
                    layer1_table: str,
                    layer2_table: str,
                    output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Find intersection between two layers.
        
        Args:
            layer1_table: First PostGIS table
            layer2_table: Second PostGIS table
            output_table: Output table name
            
        Returns:
            Dictionary with operation results
        """
        print(f"🔀 Finding intersection: {layer1_table} ∩ {layer2_table}")
        
        # Load layers
        layer1 = self._get_postgis_layer(layer1_table)
        layer2 = self._get_postgis_layer(layer2_table)
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"intersection_{timestamp}"
        
        # Run intersection algorithm
        params = {
            'INPUT': layer1,
            'OVERLAY': layer2,
            'OUTPUT': 'memory:'
        }
        
        result = processing.run("native:intersection", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        feature_count = output_layer.featureCount()
        
        print(f"✅ Intersection complete: {feature_count} features → {output_table}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'operation': 'intersection'
        }
    
    def dissolve(self,
                input_table: str,
                field: Optional[str] = None,
                output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Dissolve features based on attribute.
        
        Args:
            input_table: Input PostGIS table
            field: Field to dissolve on (None = dissolve all)
            output_table: Output table name
            
        Returns:
            Dictionary with operation results
        """
        print(f"🔗 Dissolving {input_table}" + (f" by {field}" if field else ""))
        
        # Load layer
        input_layer = self._get_postgis_layer(input_table)
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"{input_table}_dissolved_{timestamp}"
        
        # Run dissolve algorithm
        params = {
            'INPUT': input_layer,
            'FIELD': [field] if field else [],
            'OUTPUT': 'memory:'
        }
        
        result = processing.run("native:dissolve", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        feature_count = output_layer.featureCount()
        
        print(f"✅ Dissolve complete: {feature_count} features → {output_table}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'operation': 'dissolve'
        }
    
    def reproject_layer(self,
                       input_table: str,
                       target_crs: int,
                       output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Reproject layer to different coordinate system.
        
        Args:
            input_table: Input PostGIS table
            target_crs: Target EPSG code
            output_table: Output table name
            
        Returns:
            Dictionary with operation results
        """
        print(f"🌐 Reprojecting {input_table} to EPSG:{target_crs}")
        
        # Load layer
        input_layer = self._get_postgis_layer(input_table)
        source_crs = input_layer.crs().authid()
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"{input_table}_epsg{target_crs}_{timestamp}"
        
        # Run reproject algorithm
        target_crs_obj = QgsCoordinateReferenceSystem(f"EPSG:{target_crs}")
        
        params = {
            'INPUT': input_layer,
            'TARGET_CRS': target_crs_obj,
            'OUTPUT': 'memory:'
        }
        
        result = processing.run("native:reprojectlayer", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        feature_count = output_layer.featureCount()
        
        print(f"✅ Reproject complete: {source_crs} → EPSG:{target_crs}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'source_crs': source_crs,
            'target_crs': f"EPSG:{target_crs}",
            'operation': 'reproject'
        }
    
    def spatial_join(self,
                    target_table: str,
                    join_table: str,
                    predicate: str = 'intersects',
                    output_table: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform spatial join between layers.
        
        Args:
            target_table: Target PostGIS table
            join_table: Join PostGIS table
            predicate: Spatial predicate (intersects, contains, within, etc.)
            output_table: Output table name
            
        Returns:
            Dictionary with operation results
        """
        print(f"🔗 Spatial join: {target_table} + {join_table} ({predicate})")
        
        # Load layers
        target_layer = self._get_postgis_layer(target_table)
        join_layer = self._get_postgis_layer(join_table)
        
        # Generate output table name
        if not output_table:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_table = f"join_{timestamp}"
        
        # Map predicate to QGIS constant
        predicate_map = {
            'intersects': 0,
            'contains': 1,
            'equals': 2,
            'touches': 3,
            'overlaps': 4,
            'within': 5,
            'crosses': 6
        }
        
        # Run spatial join algorithm
        params = {
            'INPUT': target_layer,
            'JOIN': join_layer,
            'PREDICATE': [predicate_map.get(predicate, 0)],
            'JOIN_FIELDS': [],  # Join all fields
            'METHOD': 0,  # Create separate feature for each match
            'OUTPUT': 'memory:'
        }
        
        result = processing.run("native:joinattributesbylocation", params)
        output_layer = result['OUTPUT']
        
        # Save to PostGIS
        self._save_layer_to_postgis(output_layer, output_table, overwrite=True)
        
        feature_count = output_layer.featureCount()
        
        print(f"✅ Spatial join complete: {feature_count} features → {output_table}")
        
        return {
            'success': True,
            'output_table': output_table,
            'feature_count': feature_count,
            'operation': 'spatial_join',
            'predicate': predicate
        }
    
    def export_to_shapefile(self,
                           input_table: str,
                           output_path: str) -> Dict[str, Any]:
        """
        Export PostGIS layer to Shapefile.
        
        Args:
            input_table: Source PostGIS table
            output_path: Path to output .shp file
            
        Returns:
            Dictionary with export results
        """
        print(f"💾 Exporting {input_table} to Shapefile: {output_path}")
        
        # Load layer
        input_layer = self._get_postgis_layer(input_table)
        
        # Export
        error = QgsVectorFileWriter.writeAsVectorFormat(
            input_layer,
            output_path,
            'UTF-8',
            input_layer.crs(),
            'ESRI Shapefile'
        )
        
        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"Shapefile export failed: {error}")
        
        print(f"✅ Export complete: {output_path}")
        
        return {
            'success': True,
            'output_path': output_path,
            'format': 'shapefile',
            'feature_count': input_layer.featureCount()
        }
    
    def export_to_geojson(self,
                         input_table: str,
                         output_path: str) -> Dict[str, Any]:
        """
        Export PostGIS layer to GeoJSON.
        
        Args:
            input_table: Source PostGIS table
            output_path: Path to output .geojson file
            
        Returns:
            Dictionary with export results
        """
        print(f"💾 Exporting {input_table} to GeoJSON: {output_path}")
        
        # Load layer
        input_layer = self._get_postgis_layer(input_table)
        
        # Export
        error = QgsVectorFileWriter.writeAsVectorFormat(
            input_layer,
            output_path,
            'UTF-8',
            input_layer.crs(),
            'GeoJSON'
        )
        
        if error[0] != QgsVectorFileWriter.NoError:
            raise Exception(f"GeoJSON export failed: {error}")
        
        print(f"✅ Export complete: {output_path}")
        
        return {
            'success': True,
            'output_path': output_path,
            'format': 'geojson',
            'feature_count': input_layer.featureCount()
        }
    
    def cleanup(self):
        """Clean up QGIS resources."""
        if hasattr(self, 'app'):
            self.app.exitQgis()
            print("🧹 QGIS cleaned up")


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def get_processor() -> QGISProcessor:
    """Get the singleton QGIS processor instance."""
    try:
        return QGISProcessor()
    except QGISNotAvailableError:
        print("⚠️  QGIS is not available")
        return None


def check_qgis_available() -> bool:
    """Check if QGIS is available and properly configured."""
    return QGIS_AVAILABLE


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("QGIS PROCESSOR TEST")
    print("="*60)
    
    if not check_qgis_available():
        print("❌ QGIS is not available. Cannot run tests.")
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = QGISProcessor()
        
        # List algorithms
        print("\n📚 Available algorithm groups:")
        groups = set(info['group'] for info in processor.algorithms.values())
        for group in sorted(groups):
            count = sum(1 for info in processor.algorithms.values() 
                       if info['group'] == group)
            print(f"  • {group}: {count} algorithms")
        
        # Search for buffer algorithms
        print("\n🔍 Buffer-related algorithms:")
        buffer_algs = processor.list_algorithms(search='buffer')
        for alg in buffer_algs[:5]:  # Show first 5
            print(f"  • {alg['id']}: {alg['name']}")
        
        print("\n✅ QGIS processor test completed successfully")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if processor:
            processor.cleanup()
