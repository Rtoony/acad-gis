"""
Design standards and rules for civil engineering validation.
Provides configurable standards for pipe networks, including jurisdiction-specific requirements.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PipeMaterialStandards:
    """Standards for a specific pipe material."""
    material_name: str
    min_velocity_fps: float = 2.0  # Minimum velocity to prevent settling
    max_velocity_fps: float = 10.0  # Maximum to prevent erosion
    max_slope_percent: float = 20.0  # Maximum allowable slope
    roughness_coefficient: float = 0.013  # Manning's n value

    # Material-specific max velocities
    MATERIAL_MAX_VELOCITIES = {
        'PVC': 5.0,
        'HDPE': 5.0,
        'Concrete': 10.0,
        'RCP': 10.0,  # Reinforced Concrete Pipe
        'DIP': 8.0,   # Ductile Iron Pipe
        'CMP': 7.0,   # Corrugated Metal Pipe
        'STEEL': 8.0,
    }

    def __post_init__(self):
        """Set material-specific max velocity if available."""
        material_upper = self.material_name.upper() if self.material_name else ''
        for mat_key, max_vel in self.MATERIAL_MAX_VELOCITIES.items():
            if mat_key in material_upper:
                self.max_velocity_fps = max_vel
                break


@dataclass
class PipeDesignStandards:
    """Comprehensive design standards for pipe networks."""

    # Minimum slopes based on diameter (in percent)
    # These are industry-standard minimums to ensure self-cleansing velocity
    MIN_SLOPES_BY_DIAMETER: Dict[int, float] = field(default_factory=lambda: {
        4: 0.60,    # 4" pipe
        6: 0.40,    # 6" pipe
        8: 0.40,    # 8" pipe
        10: 0.28,   # 10" pipe
        12: 0.33,   # 12" pipe
        15: 0.25,   # 15" pipe
        18: 0.19,   # 18" pipe
        24: 0.15,   # 24" pipe
        30: 0.12,   # 30" pipe
        36: 0.10,   # 36" pipe
        42: 0.08,   # 42" pipe
        48: 0.07,   # 48" pipe and larger
    })

    # Standard pipe diameters (inches)
    STANDARD_DIAMETERS: List[int] = field(default_factory=lambda: [
        4, 6, 8, 10, 12, 15, 18, 21, 24, 27, 30, 33, 36, 42, 48, 54, 60, 66, 72
    ])

    # Minimum diameter (inches)
    min_diameter_in: int = 12  # Most jurisdictions require 12" minimum for storm

    # Maximum depth-to-diameter ratio for cover
    min_cover_ft: float = 2.0  # Minimum cover over pipe crown
    max_cover_ft: float = 15.0  # Maximum practical cover

    # Velocity constraints (fps - feet per second)
    min_velocity_fps: float = 2.0  # Prevent sediment deposition
    max_velocity_fps: float = 10.0  # Prevent erosion (material-dependent)

    # Slope constraints (percent)
    max_slope_percent: float = 20.0  # Maximum practical slope

    # Connection tolerances
    max_invert_mismatch_ft: float = 0.1  # Maximum allowable invert mismatch at connections
    max_diameter_increase_ratio: float = 1.5  # Max ratio when upsizing (e.g., 12" to 18" = 1.5)

    # Network topology
    allow_loops: bool = False  # Most storm systems should be tree-structured
    require_outfall: bool = True  # Network must have at least one outfall

    # Hydraulic constraints
    max_hgl_to_ground_ratio: float = 0.90  # HGL should not exceed 90% of ground elevation

    def get_min_slope_for_diameter(self, diameter_in: float) -> float:
        """Get minimum slope (percent) for a given diameter."""
        # Find the closest standard diameter
        closest_diameter = min(
            self.MIN_SLOPES_BY_DIAMETER.keys(),
            key=lambda x: abs(x - diameter_in)
        )

        # If diameter is larger than largest in table, use the largest
        if diameter_in >= max(self.MIN_SLOPES_BY_DIAMETER.keys()):
            return self.MIN_SLOPES_BY_DIAMETER[max(self.MIN_SLOPES_BY_DIAMETER.keys())]

        return self.MIN_SLOPES_BY_DIAMETER[closest_diameter]

    def is_standard_diameter(self, diameter_in: float) -> bool:
        """Check if diameter is a standard size."""
        return any(abs(diameter_in - std) < 0.5 for std in self.STANDARD_DIAMETERS)


@dataclass
class JurisdictionStandards:
    """Jurisdiction-specific standards (e.g., city, county, DOT)."""
    jurisdiction_name: str
    pipe_standards: PipeDesignStandards = field(default_factory=PipeDesignStandards)

    # Specific overrides for this jurisdiction
    notes: str = ""

    @classmethod
    def get_default(cls) -> 'JurisdictionStandards':
        """Get default industry-standard rules."""
        return cls(
            jurisdiction_name="Industry Standard (ASCE/APWA)",
            notes="Default standards based on ASCE and APWA best practices"
        )

    @classmethod
    def get_strict(cls) -> 'JurisdictionStandards':
        """Get stricter standards (conservative design)."""
        standards = PipeDesignStandards()
        standards.min_diameter_in = 15  # More conservative minimum
        standards.min_cover_ft = 3.0  # More cover required
        standards.max_velocity_fps = 8.0  # More conservative velocity

        return cls(
            jurisdiction_name="Strict/Conservative",
            pipe_standards=standards,
            notes="Conservative design standards for high-risk areas"
        )


# Pre-defined standards
DEFAULT_STANDARDS = JurisdictionStandards.get_default()
STRICT_STANDARDS = JurisdictionStandards.get_strict()


def calculate_velocity(
    diameter_in: float,
    slope_percent: float,
    roughness: float = 0.013,
    depth_ratio: float = 0.8
) -> float:
    """
    Calculate flow velocity using Manning's equation (simplified).

    Args:
        diameter_in: Pipe diameter in inches
        slope_percent: Slope in percent
        roughness: Manning's roughness coefficient (n)
        depth_ratio: Ratio of flow depth to diameter (0-1)

    Returns:
        Velocity in feet per second
    """
    # Convert to feet
    diameter_ft = diameter_in / 12.0
    slope_decimal = slope_percent / 100.0

    # Calculate hydraulic radius for circular pipe
    # For partial flow, this is approximate
    radius_ft = (diameter_ft / 2.0) * depth_ratio

    # Manning's equation: V = (1.486/n) * R^(2/3) * S^(1/2)
    velocity_fps = (1.486 / roughness) * (radius_ft ** (2/3)) * (slope_decimal ** 0.5)

    return velocity_fps


def calculate_flow_capacity(
    diameter_in: float,
    slope_percent: float,
    roughness: float = 0.013
) -> float:
    """
    Calculate pipe flow capacity using Manning's equation (full flow).

    Args:
        diameter_in: Pipe diameter in inches
        slope_percent: Slope in percent
        roughness: Manning's roughness coefficient (n)

    Returns:
        Flow capacity in cubic feet per second (CFS)
    """
    import math

    # Convert to feet
    diameter_ft = diameter_in / 12.0
    slope_decimal = slope_percent / 100.0

    # Full pipe calculations
    area_ft2 = math.pi * (diameter_ft ** 2) / 4.0
    wetted_perimeter_ft = math.pi * diameter_ft
    hydraulic_radius_ft = area_ft2 / wetted_perimeter_ft

    # Manning's equation: Q = (1.486/n) * A * R^(2/3) * S^(1/2)
    velocity = (1.486 / roughness) * (hydraulic_radius_ft ** (2/3)) * (slope_decimal ** 0.5)
    capacity_cfs = area_ft2 * velocity

    return capacity_cfs
