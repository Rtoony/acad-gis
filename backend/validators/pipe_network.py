"""
Comprehensive validation for pipe networks.
Includes continuity, hydraulic, standards compliance, and topology checks.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import execute_query, execute_single
from validators.standards import (
    PipeDesignStandards,
    JurisdictionStandards,
    calculate_velocity,
    calculate_flow_capacity,
    DEFAULT_STANDARDS
)


class Severity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"  # Must be fixed before construction
    WARNING = "warning"  # Should be reviewed, may be acceptable
    INFO = "info"  # Informational, no action required


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: Severity
    category: str  # e.g., "continuity", "hydraulic", "standards", "topology"
    code: str  # e.g., "ORPHANED_PIPE", "VELOCITY_LOW"
    message: str
    pipe_id: Optional[str] = None
    structure_id: Optional[str] = None
    location: Optional[str] = None  # Human-readable location
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['severity'] = self.severity.value
        return result


@dataclass
class ValidationResult:
    """Results from network validation."""
    network_id: str
    network_name: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None

    def add_issue(self, issue: ValidationIssue):
        """Add an issue and update validity status."""
        self.issues.append(issue)
        if issue.severity == Severity.ERROR:
            self.is_valid = False

    def get_issues_by_severity(self, severity: Severity) -> List[ValidationIssue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_category(self, category: str) -> List[ValidationIssue]:
        """Get all issues in a specific category."""
        return [issue for issue in self.issues if issue.category == category]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'network_id': self.network_id,
            'network_name': self.network_name,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'is_valid': self.is_valid,
            'issues': [issue.to_dict() for issue in self.issues],
            'statistics': self.statistics,
            'timestamp': self.timestamp,
            'summary': {
                'total_issues': len(self.issues),
                'errors': len(self.get_issues_by_severity(Severity.ERROR)),
                'warnings': len(self.get_issues_by_severity(Severity.WARNING)),
                'info': len(self.get_issues_by_severity(Severity.INFO))
            }
        }


class PipeNetworkValidator:
    """Comprehensive validator for pipe networks."""

    def __init__(self, standards: JurisdictionStandards = None):
        """Initialize validator with design standards."""
        self.standards = standards or DEFAULT_STANDARDS
        self.pipes: List[Dict] = []
        self.structures: List[Dict] = []
        self.network_info: Dict = {}

    def validate_network(self, network_id: str) -> ValidationResult:
        """
        Run all validation checks on a pipe network.

        Args:
            network_id: UUID of the pipe network to validate

        Returns:
            ValidationResult with all issues found
        """
        # Load network data
        self._load_network_data(network_id)

        # Create result container
        result = ValidationResult(
            network_id=network_id,
            network_name=self.network_info.get('name'),
            project_id=self.network_info.get('project_id'),
            project_name=self.network_info.get('project_name')
        )

        # Run all validation checks
        self._check_continuity(result)
        self._check_hydraulics(result)
        self._check_standards_compliance(result)
        self._check_topology(result)
        self._check_geometry(result)

        # Add statistics
        result.statistics = self._calculate_statistics()

        return result

    def _load_network_data(self, network_id: str):
        """Load all network data from database."""
        # Get network info
        network_query = """
            SELECT pn.*, p.project_name
            FROM pipe_networks pn
            LEFT JOIN projects p ON pn.project_id = p.project_id
            WHERE pn.network_id = %s
        """
        self.network_info = execute_single(network_query, (network_id,)) or {}

        # Get all pipes
        pipes_query = """
            SELECT
                pipe_id,
                network_id,
                diameter_mm,
                material,
                slope,
                length_m,
                invert_up,
                invert_dn,
                status,
                up_structure_id,
                down_structure_id,
                ST_AsText(geom) as geom_wkt,
                ST_X(ST_StartPoint(geom)) as start_x,
                ST_Y(ST_StartPoint(geom)) as start_y,
                ST_X(ST_EndPoint(geom)) as end_x,
                ST_Y(ST_EndPoint(geom)) as end_y
            FROM pipes
            WHERE network_id = %s
        """
        self.pipes = execute_query(pipes_query, (network_id,))

        # Get all structures
        structures_query = """
            SELECT
                structure_id,
                network_id,
                type,
                rim_elev,
                sump_depth,
                ST_AsText(geom) as geom_wkt,
                ST_X(geom) as x,
                ST_Y(geom) as y
            FROM structures
            WHERE network_id = %s
        """
        self.structures = execute_query(structures_query, (network_id,))

    def _check_continuity(self, result: ValidationResult):
        """Check network continuity (connections, orphaned elements)."""
        structure_ids = {s['structure_id'] for s in self.structures}

        for pipe in self.pipes:
            pipe_id = pipe['pipe_id']

            # Check upstream connection
            if pipe.get('up_structure_id'):
                if pipe['up_structure_id'] not in structure_ids:
                    result.add_issue(ValidationIssue(
                        severity=Severity.ERROR,
                        category="continuity",
                        code="MISSING_UPSTREAM_STRUCTURE",
                        message=f"Pipe references non-existent upstream structure",
                        pipe_id=pipe_id,
                        structure_id=pipe['up_structure_id']
                    ))
            else:
                # Pipe has no upstream structure
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="continuity",
                    code="NO_UPSTREAM_CONNECTION",
                    message=f"Pipe has no upstream structure connection",
                    pipe_id=pipe_id
                ))

            # Check downstream connection
            if pipe.get('down_structure_id'):
                if pipe['down_structure_id'] not in structure_ids:
                    result.add_issue(ValidationIssue(
                        severity=Severity.ERROR,
                        category="continuity",
                        code="MISSING_DOWNSTREAM_STRUCTURE",
                        message=f"Pipe references non-existent downstream structure",
                        pipe_id=pipe_id,
                        structure_id=pipe['down_structure_id']
                    ))
            else:
                # Pipe has no downstream structure
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="continuity",
                    code="NO_DOWNSTREAM_CONNECTION",
                    message=f"Pipe has no downstream structure connection",
                    pipe_id=pipe_id
                ))

            # Check invert continuity at connections
            # NOTE: Disabled - structures table does not have invert_elev column
            # This check would require calculating structure inverts from connected pipes
            # or adding invert_elev column to structures table
            # if pipe.get('up_structure_id') and pipe.get('invert_up') is not None:
            #     upstream_struct = next((s for s in self.structures if s['structure_id'] == pipe['up_structure_id']), None)
            #     if upstream_struct and upstream_struct.get('invert_elev') is not None:
            #         mismatch = abs(float(pipe['invert_up']) - float(upstream_struct['invert_elev']))
            #         max_mismatch = self.standards.pipe_standards.max_invert_mismatch_ft
            #
            #         if mismatch > max_mismatch:
            #             result.add_issue(ValidationIssue(
            #                 severity=Severity.WARNING,
            #                 category="continuity",
            #                 code="INVERT_MISMATCH_UPSTREAM",
            #                 message=f"Invert mismatch at upstream connection: {mismatch:.2f} ft",
            #                 pipe_id=pipe_id,
            #                 structure_id=pipe['up_structure_id'],
            #                 expected_value=float(upstream_struct['invert_elev']),
            #                 actual_value=float(pipe['invert_up'])
            #             ))
            #
            # if pipe.get('down_structure_id') and pipe.get('invert_dn') is not None:
            #     downstream_struct = next((s for s in self.structures if s['structure_id'] == pipe['down_structure_id']), None)
            #     if downstream_struct and downstream_struct.get('invert_elev') is not None:
            #         mismatch = abs(float(pipe['invert_dn']) - float(downstream_struct['invert_elev']))
            #         max_mismatch = self.standards.pipe_standards.max_invert_mismatch_ft
            #
            #         if mismatch > max_mismatch:
            #             result.add_issue(ValidationIssue(
            #                 severity=Severity.WARNING,
            #                 category="continuity",
            #                 code="INVERT_MISMATCH_DOWNSTREAM",
            #                 message=f"Invert mismatch at downstream connection: {mismatch:.2f} ft",
            #                 pipe_id=pipe_id,
            #                 structure_id=pipe['down_structure_id'],
            #                 expected_value=float(downstream_struct['invert_elev']),
            #                 actual_value=float(pipe['invert_dn'])
            #             ))

    def _check_hydraulics(self, result: ValidationResult):
        """Check hydraulic performance (velocity, slope, capacity)."""
        for pipe in self.pipes:
            pipe_id = pipe['pipe_id']
            diameter_mm = pipe.get('diameter_mm')
            slope = pipe.get('slope')
            material = pipe.get('material', 'Unknown')

            if diameter_mm is None or slope is None:
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="hydraulic",
                    code="MISSING_HYDRAULIC_DATA",
                    message=f"Missing diameter or slope data",
                    pipe_id=pipe_id
                ))
                continue

            diameter_in = float(diameter_mm) / 25.4
            slope_percent = float(slope)

            # Check slope minimum
            min_slope = self.standards.pipe_standards.get_min_slope_for_diameter(diameter_in)
            if slope_percent < min_slope:
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="hydraulic",
                    code="SLOPE_TOO_LOW",
                    message=f"Slope {slope_percent:.2f}% is below minimum {min_slope:.2f}% for {diameter_in:.0f}\" pipe",
                    pipe_id=pipe_id,
                    expected_value=min_slope,
                    actual_value=slope_percent
                ))

            # Check slope maximum
            max_slope = self.standards.pipe_standards.max_slope_percent
            if slope_percent > max_slope:
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="hydraulic",
                    code="SLOPE_TOO_HIGH",
                    message=f"Slope {slope_percent:.2f}% exceeds maximum {max_slope:.2f}%",
                    pipe_id=pipe_id,
                    expected_value=max_slope,
                    actual_value=slope_percent
                ))

            # Calculate velocity
            velocity_fps = calculate_velocity(diameter_in, slope_percent)

            # Check minimum velocity
            min_velocity = self.standards.pipe_standards.min_velocity_fps
            if velocity_fps < min_velocity:
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="hydraulic",
                    code="VELOCITY_TOO_LOW",
                    message=f"Velocity {velocity_fps:.2f} fps is below minimum {min_velocity:.2f} fps (sediment may settle)",
                    pipe_id=pipe_id,
                    expected_value=min_velocity,
                    actual_value=velocity_fps,
                    metadata={'diameter_in': diameter_in, 'slope_percent': slope_percent}
                ))

            # Check maximum velocity (material-dependent)
            from validators.standards import PipeMaterialStandards
            material_standards = PipeMaterialStandards(material)
            max_velocity = material_standards.max_velocity_fps

            if velocity_fps > max_velocity:
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="hydraulic",
                    code="VELOCITY_TOO_HIGH",
                    message=f"Velocity {velocity_fps:.2f} fps exceeds maximum {max_velocity:.2f} fps for {material} (erosion risk)",
                    pipe_id=pipe_id,
                    expected_value=max_velocity,
                    actual_value=velocity_fps,
                    metadata={'diameter_in': diameter_in, 'slope_percent': slope_percent, 'material': material}
                ))

            # Calculate flow capacity
            capacity_cfs = calculate_flow_capacity(diameter_in, slope_percent)

            # Store calculated values in metadata for reporting
            pipe['_calculated_velocity_fps'] = velocity_fps
            pipe['_calculated_capacity_cfs'] = capacity_cfs

    def _check_standards_compliance(self, result: ValidationResult):
        """Check compliance with design standards."""
        for pipe in self.pipes:
            pipe_id = pipe['pipe_id']
            diameter_mm = pipe.get('diameter_mm')
            material = pipe.get('material')

            if diameter_mm is None:
                continue

            diameter_in = float(diameter_mm) / 25.4

            # Check minimum diameter
            min_diameter = self.standards.pipe_standards.min_diameter_in
            if diameter_in < min_diameter:
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="standards",
                    code="DIAMETER_TOO_SMALL",
                    message=f"Diameter {diameter_in:.0f}\" is below minimum {min_diameter:.0f}\"",
                    pipe_id=pipe_id,
                    expected_value=min_diameter,
                    actual_value=diameter_in
                ))

            # Check if diameter is standard size
            if not self.standards.pipe_standards.is_standard_diameter(diameter_in):
                result.add_issue(ValidationIssue(
                    severity=Severity.INFO,
                    category="standards",
                    code="NON_STANDARD_DIAMETER",
                    message=f"Diameter {diameter_in:.0f}\" is not a standard size",
                    pipe_id=pipe_id,
                    actual_value=diameter_in,
                    metadata={'standard_sizes': self.standards.pipe_standards.STANDARD_DIAMETERS}
                ))

            # Check material is specified
            if not material or material.strip() == '':
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="standards",
                    code="MATERIAL_NOT_SPECIFIED",
                    message=f"Pipe material not specified",
                    pipe_id=pipe_id
                ))

        # Check diameter transitions (upsizing in flow direction is bad)
        self._check_diameter_transitions(result)

    def _check_diameter_transitions(self, result: ValidationResult):
        """Check for improper diameter transitions (upsizing downstream)."""
        # Build adjacency map
        pipe_by_upstream: Dict[str, List[Dict]] = {}
        for pipe in self.pipes:
            up_struct = pipe.get('up_structure_id')
            if up_struct:
                if up_struct not in pipe_by_upstream:
                    pipe_by_upstream[up_struct] = []
                pipe_by_upstream[up_struct].append(pipe)

        for pipe in self.pipes:
            dn_struct = pipe.get('down_structure_id')
            if not dn_struct or pipe.get('diameter_mm') is None:
                continue

            current_diameter = float(pipe['diameter_mm'])

            # Find downstream pipes
            downstream_pipes = pipe_by_upstream.get(dn_struct, [])

            for dn_pipe in downstream_pipes:
                if dn_pipe.get('diameter_mm') is None:
                    continue

                dn_diameter = float(dn_pipe['diameter_mm'])

                # Check if diameter increases downstream (usually bad)
                if dn_diameter > current_diameter:
                    ratio = dn_diameter / current_diameter
                    max_ratio = self.standards.pipe_standards.max_diameter_increase_ratio

                    if ratio > max_ratio:
                        result.add_issue(ValidationIssue(
                            severity=Severity.WARNING,
                            category="standards",
                            code="DIAMETER_INCREASE_DOWNSTREAM",
                            message=f"Diameter increases from {current_diameter/25.4:.0f}\" to {dn_diameter/25.4:.0f}\" downstream (ratio {ratio:.2f})",
                            pipe_id=pipe['pipe_id'],
                            metadata={
                                'downstream_pipe_id': dn_pipe['pipe_id'],
                                'current_diameter_in': current_diameter / 25.4,
                                'downstream_diameter_in': dn_diameter / 25.4,
                                'ratio': ratio
                            }
                        ))

    def _check_topology(self, result: ValidationResult):
        """Check network topology (loops, outfalls, drainage direction)."""
        # Build graph structure
        graph = self._build_network_graph()

        # Find outfalls (structures with no downstream pipes)
        outfalls = self._find_outfalls(graph)

        if len(outfalls) == 0 and self.standards.pipe_standards.require_outfall:
            result.add_issue(ValidationIssue(
                severity=Severity.ERROR,
                category="topology",
                code="NO_OUTFALL",
                message=f"Network has no outfall structure",
                metadata={'network_id': self.network_info['network_id']}
            ))

        # Check for loops/cycles
        if not self.standards.pipe_standards.allow_loops:
            cycles = self._find_cycles(graph)
            if cycles:
                for cycle in cycles:
                    result.add_issue(ValidationIssue(
                        severity=Severity.WARNING,
                        category="topology",
                        code="NETWORK_LOOP_DETECTED",
                        message=f"Loop detected in network (typically not allowed for storm drainage)",
                        metadata={'structures_in_loop': cycle}
                    ))

        # Check drainage direction (upstream elevation should be higher than downstream)
        self._check_drainage_direction(result)

    def _build_network_graph(self) -> Dict[str, List[str]]:
        """Build adjacency list representation of network."""
        graph: Dict[str, List[str]] = {}

        for structure in self.structures:
            graph[structure['structure_id']] = []

        for pipe in self.pipes:
            up_struct = pipe.get('up_structure_id')
            dn_struct = pipe.get('down_structure_id')

            if up_struct and dn_struct:
                if up_struct not in graph:
                    graph[up_struct] = []
                graph[up_struct].append(dn_struct)

        return graph

    def _find_outfalls(self, graph: Dict[str, List[str]]) -> List[str]:
        """Find all outfall structures (no downstream connections)."""
        outfalls = []
        for struct_id, downstream in graph.items():
            if len(downstream) == 0:
                # Check if this structure actually has pipes flowing TO it
                has_incoming = any(
                    pipe.get('down_structure_id') == struct_id
                    for pipe in self.pipes
                )
                if has_incoming:
                    outfalls.append(struct_id)
        return outfalls

    def _find_cycles(self, graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find cycles in the network using DFS."""
        cycles = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:])
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _check_drainage_direction(self, result: ValidationResult):
        """Check that flow direction follows gravity (uphill to downhill)."""
        for pipe in self.pipes:
            invert_up = pipe.get('invert_up')
            invert_dn = pipe.get('invert_dn')

            if invert_up is None or invert_dn is None:
                continue

            invert_up = float(invert_up)
            invert_dn = float(invert_dn)

            # Downstream invert should be lower than upstream
            if invert_dn >= invert_up:
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="topology",
                    code="REVERSE_DRAINAGE",
                    message=f"Pipe drains uphill: upstream invert {invert_up:.2f} <= downstream invert {invert_dn:.2f}",
                    pipe_id=pipe['pipe_id'],
                    metadata={
                        'invert_up': invert_up,
                        'invert_dn': invert_dn,
                        'calculated_slope': ((invert_up - invert_dn) / pipe.get('length_m', 1) * 100) if pipe.get('length_m') else None
                    }
                ))

    def _check_geometry(self, result: ValidationResult):
        """Check geometric validity (valid coordinates, reasonable lengths)."""
        for pipe in self.pipes:
            pipe_id = pipe['pipe_id']
            length_m = pipe.get('length_m')

            # Check for zero-length or very short pipes
            if length_m is not None and float(length_m) < 0.5:  # Less than 0.5 meters (1.6 ft)
                result.add_issue(ValidationIssue(
                    severity=Severity.WARNING,
                    category="geometry",
                    code="PIPE_TOO_SHORT",
                    message=f"Pipe length {float(length_m):.2f}m ({float(length_m)*3.28:.1f}ft) is unusually short",
                    pipe_id=pipe_id,
                    actual_value=float(length_m)
                ))

            # Check for missing geometry
            if not pipe.get('geom_wkt'):
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="geometry",
                    code="MISSING_GEOMETRY",
                    message=f"Pipe has no geometry defined",
                    pipe_id=pipe_id
                ))

        for structure in self.structures:
            # Check for missing geometry
            if not structure.get('geom_wkt'):
                result.add_issue(ValidationIssue(
                    severity=Severity.ERROR,
                    category="geometry",
                    code="MISSING_GEOMETRY",
                    message=f"Structure has no geometry defined",
                    structure_id=structure['structure_id']
                ))

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate summary statistics for the network."""
        if not self.pipes:
            return {}

        total_length = sum(float(p.get('length_m', 0)) for p in self.pipes)
        avg_slope = sum(float(p.get('slope', 0)) for p in self.pipes if p.get('slope')) / len([p for p in self.pipes if p.get('slope')]) if self.pipes else 0

        diameters = [float(p['diameter_mm']) / 25.4 for p in self.pipes if p.get('diameter_mm')]
        materials = [p.get('material', 'Unknown') for p in self.pipes]

        # Count by material
        material_counts = {}
        for mat in materials:
            material_counts[mat] = material_counts.get(mat, 0) + 1

        return {
            'total_pipes': len(self.pipes),
            'total_structures': len(self.structures),
            'total_length_m': total_length,
            'total_length_ft': total_length * 3.28084,
            'average_slope_percent': avg_slope,
            'diameter_range_in': {
                'min': min(diameters) if diameters else None,
                'max': max(diameters) if diameters else None,
                'avg': sum(diameters) / len(diameters) if diameters else None
            },
            'materials': material_counts,
            'calculated_velocities_fps': {
                'min': min((p.get('_calculated_velocity_fps', 0) for p in self.pipes if '_calculated_velocity_fps' in p), default=None),
                'max': max((p.get('_calculated_velocity_fps', 0) for p in self.pipes if '_calculated_velocity_fps' in p), default=None),
                'avg': sum((p.get('_calculated_velocity_fps', 0) for p in self.pipes if '_calculated_velocity_fps' in p)) / len([p for p in self.pipes if '_calculated_velocity_fps' in p]) if self.pipes else None
            }
        }


def validate_pipe_network(
    network_id: str,
    standards: Optional[JurisdictionStandards] = None
) -> ValidationResult:
    """
    Validate a pipe network with comprehensive checks.

    Args:
        network_id: UUID of the network to validate
        standards: Optional custom standards (uses DEFAULT_STANDARDS if not provided)

    Returns:
        ValidationResult with all issues and statistics
    """
    validator = PipeNetworkValidator(standards)
    return validator.validate_network(network_id)
