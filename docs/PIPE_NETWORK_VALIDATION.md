# Pipe Network Validation Guide

## Overview

The ACAD-GIS pipe network validation system provides comprehensive checks for civil engineering design standards, hydraulic performance, network topology, and geometric integrity. This system helps catch design errors early, ensure compliance with industry standards, and validate that pipe networks will function as intended.

## Table of Contents

- [Quick Start](#quick-start)
- [Validation Categories](#validation-categories)
- [Design Standards](#design-standards)
- [API Reference](#api-reference)
- [Frontend Integration](#frontend-integration)
- [Validation Issue Codes](#validation-issue-codes)
- [Best Practices](#best-practices)

---

## Quick Start

### Using the Web Interface

1. Open the **Pipe Network Editor** tool
2. Select a network from the list
3. Click **"Run Comprehensive Validation"**
4. Choose standards: **Default** (industry standard) or **Strict** (conservative)
5. Review validation results grouped by category

### Using the API

```bash
# POST request with network ID
curl -X POST http://localhost:8000/api/validate/pipe-network \
  -H "Content-Type: application/json" \
  -d '{
    "network_id": "your-network-uuid",
    "standards": "default"
  }'

# GET request for specific network
curl http://localhost:8000/api/validate/pipe-network/your-network-uuid?standards=default
```

### Python Example

```python
import requests

response = requests.post(
    'http://localhost:8000/api/validate/pipe-network',
    json={
        'network_id': 'your-network-uuid',
        'standards': 'strict'
    }
)

result = response.json()['result']

print(f"Network is valid: {result['is_valid']}")
print(f"Total issues: {result['summary']['total_issues']}")
print(f"Errors: {result['summary']['errors']}")
print(f"Warnings: {result['summary']['warnings']}")

# Iterate through issues
for issue in result['issues']:
    print(f"[{issue['severity'].upper()}] {issue['code']}: {issue['message']}")
```

---

## Validation Categories

The validation system checks five key categories:

### 1. Continuity Checks

Ensures pipes and structures are properly connected.

**What it checks:**
- Pipes reference existing structures (upstream and downstream)
- All connections are accounted for
- Invert elevations match at connection points
- No orphaned pipes or structures

**Common Issues:**
- `ORPHANED_PIPE` - Pipe not connected to any structure
- `MISSING_UPSTREAM_STRUCTURE` - Referenced structure doesn't exist
- `INVERT_MISMATCH` - Invert elevations don't match at connection (tolerance: 0.1 ft)

### 2. Hydraulic Validation

Validates flow characteristics and hydraulic performance.

**What it checks:**
- Slope meets minimum for self-cleansing velocity
- Slope doesn't exceed maximum (erosion risk)
- Velocity > 2.0 fps (prevents sediment settling)
- Velocity < max for material (prevents erosion)
- Flow capacity calculations

**Common Issues:**
- `SLOPE_TOO_LOW` - Won't achieve self-cleansing velocity
- `SLOPE_TOO_HIGH` - Risk of erosion or pipe damage
- `VELOCITY_TOO_LOW` - Sediment will settle (< 2 fps)
- `VELOCITY_TOO_HIGH` - Material-specific max exceeded

**Minimum Slopes by Diameter:**

| Diameter | Min Slope | Reason |
|----------|-----------|--------|
| 4" | 0.60% | Small diameter needs steeper slope |
| 6" | 0.40% | |
| 8" | 0.40% | |
| 10" | 0.28% | |
| 12" | 0.33% | |
| 15" | 0.25% | |
| 18" | 0.19% | |
| 24" | 0.15% | Larger diameter more efficient |
| 30"+ | 0.12% | |

**Maximum Velocities by Material:**

| Material | Max Velocity | Reason |
|----------|--------------|--------|
| PVC | 5.0 fps | Plastic erosion threshold |
| HDPE | 5.0 fps | Plastic erosion threshold |
| Concrete (RCP) | 10.0 fps | Concrete can handle higher velocities |
| Ductile Iron | 8.0 fps | Metal erosion threshold |
| Corrugated Metal | 7.0 fps | Corrugation reduces threshold |
| Steel | 8.0 fps | Metal erosion threshold |

### 3. Standards Compliance

Checks adherence to design standards and best practices.

**What it checks:**
- Minimum pipe diameter (typically 12" for storm)
- Standard pipe sizes used
- Material specified
- Diameter transitions (no upsizing downstream)
- Cover requirements (min 2 ft, max 15 ft)

**Common Issues:**
- `DIAMETER_TOO_SMALL` - Below jurisdiction minimum
- `NON_STANDARD_DIAMETER` - Non-standard size (informational)
- `MATERIAL_NOT_SPECIFIED` - Missing material designation
- `DIAMETER_INCREASE_DOWNSTREAM` - Upsizing in flow direction (bad practice)

### 4. Topology Analysis

Validates network structure and drainage patterns.

**What it checks:**
- Network has at least one outfall
- Drainage flows downhill (upstream higher than downstream)
- No loops/cycles (storm systems should be tree-structured)
- Proper upstream/downstream relationships

**Common Issues:**
- `NO_OUTFALL` - Network has no discharge point
- `REVERSE_DRAINAGE` - Pipe drains uphill
- `NETWORK_LOOP_DETECTED` - Circular flow pattern

### 5. Geometry Checks

Validates geometric data integrity.

**What it checks:**
- All pipes have geometry defined
- All structures have geometry defined
- Pipe lengths are reasonable (not zero-length)
- Coordinates are valid

**Common Issues:**
- `MISSING_GEOMETRY` - No geometry stored in database
- `PIPE_TOO_SHORT` - Unusually short segment (< 1.6 ft)

---

## Design Standards

### Default Standards (Industry Standard)

Based on ASCE and APWA best practices:

```python
min_diameter_in = 12          # Minimum pipe diameter
min_velocity_fps = 2.0        # Prevent settling
max_velocity_fps = 10.0       # Prevent erosion (material-dependent)
min_cover_ft = 2.0            # Minimum cover over pipe
max_cover_ft = 15.0           # Maximum practical depth
max_slope_percent = 20.0      # Maximum allowable slope
allow_loops = False           # Storm systems should be tree-structured
require_outfall = True        # Must have discharge point
```

### Strict Standards (Conservative Design)

For high-risk areas or conservative jurisdictions:

```python
min_diameter_in = 15          # Larger minimum diameter
min_velocity_fps = 2.0        # Same minimum velocity
max_velocity_fps = 8.0        # More conservative max velocity
min_cover_ft = 3.0            # More cover required
max_cover_ft = 15.0           # Same max depth
max_slope_percent = 20.0      # Same max slope
```

### Custom Standards

You can create custom jurisdiction standards in `backend/validators/standards.py`:

```python
from validators.standards import JurisdictionStandards, PipeDesignStandards

# Create custom standards
custom_standards = PipeDesignStandards()
custom_standards.min_diameter_in = 18  # City requires 18" minimum
custom_standards.min_velocity_fps = 2.5  # Higher velocity requirement
custom_standards.max_slope_percent = 15.0  # Lower max slope

jurisdiction = JurisdictionStandards(
    jurisdiction_name="City of Example",
    pipe_standards=custom_standards,
    notes="Custom standards for City of Example storm drainage"
)
```

---

## API Reference

### POST /api/validate/pipe-network

Comprehensive validation of a pipe network.

**Request Body:**
```json
{
  "network_id": "uuid-string",
  "standards": "default" | "strict"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Validated network: 15 issues found (3 errors, 12 warnings)",
  "result": {
    "network_id": "uuid",
    "network_name": "Storm Network A",
    "project_id": "uuid",
    "project_name": "Main Street Reconstruction",
    "is_valid": false,
    "issues": [
      {
        "severity": "error",
        "category": "hydraulic",
        "code": "SLOPE_TOO_LOW",
        "message": "Slope 0.25% is below minimum 0.33% for 12\" pipe",
        "pipe_id": "uuid",
        "expected_value": 0.33,
        "actual_value": 0.25
      }
    ],
    "statistics": {
      "total_pipes": 45,
      "total_structures": 23,
      "total_length_m": 450.5,
      "total_length_ft": 1478.0,
      "average_slope_percent": 0.65,
      "diameter_range_in": {
        "min": 12,
        "max": 24,
        "avg": 15.2
      },
      "calculated_velocities_fps": {
        "min": 1.8,
        "max": 4.5,
        "avg": 2.9
      }
    },
    "summary": {
      "total_issues": 15,
      "errors": 3,
      "warnings": 12,
      "info": 0
    }
  }
}
```

### GET /api/validate/pipe-network/{network_id}

Same as POST but using GET with query parameters.

**Query Parameters:**
- `standards` (optional): "default" or "strict" (default: "default")

**Example:**
```
GET /api/validate/pipe-network/abc-123?standards=strict
```

### GET /api/validate/standards

Get information about available validation standards.

**Response:**
```json
{
  "success": true,
  "standards": {
    "default": {
      "name": "Industry Standard (ASCE/APWA)",
      "min_diameter_in": 12,
      "min_velocity_fps": 2.0,
      "max_velocity_fps": 10.0,
      "min_cover_ft": 2.0,
      "max_slope_percent": 20.0
    },
    "strict": {
      "name": "Strict/Conservative",
      "min_diameter_in": 15,
      "min_velocity_fps": 2.0,
      "max_velocity_fps": 8.0,
      "min_cover_ft": 3.0,
      "max_slope_percent": 20.0
    }
  },
  "min_slopes_by_diameter": {
    "4": 0.6,
    "12": 0.33,
    "24": 0.15
  },
  "standard_diameters": [4, 6, 8, 10, 12, 15, 18, 21, 24, 30, 36, 42, 48]
}
```

---

## Frontend Integration

### Using the Pipe Network Editor

The Pipe Network Editor includes a built-in validation interface:

1. **Select a Network**: Click on a network in the table
2. **Run Validation**: Click "Run Comprehensive Validation" button
3. **Choose Standards**: Select from dropdown (Default or Strict)
4. **View Results**: Issues are grouped by category with color-coded severity
5. **Review Details**: Each issue shows:
   - Severity level (Error, Warning, Info)
   - Category (Continuity, Hydraulic, Standards, Topology, Geometry)
   - Descriptive message
   - Affected pipe/structure ID
   - Expected vs. actual values (when applicable)

### Validation Result Display

**Summary Cards:**
- **Status**: Valid/Invalid with color coding
- **Errors**: Critical issues that must be fixed
- **Warnings**: Issues to review (may be acceptable)
- **Info**: Informational notices

**Network Statistics:**
- Total pipes and structures
- Total length
- Average calculated velocity
- Diameter range
- Material breakdown

**Issues by Category:**
- Expandable sections for each category
- Color-coded severity indicators
- Detailed issue descriptions
- Quick identification of problem areas

---

## Validation Issue Codes

### Continuity Codes

| Code | Severity | Description |
|------|----------|-------------|
| `MISSING_UPSTREAM_STRUCTURE` | ERROR | Pipe references non-existent upstream structure |
| `MISSING_DOWNSTREAM_STRUCTURE` | ERROR | Pipe references non-existent downstream structure |
| `NO_UPSTREAM_CONNECTION` | WARNING | Pipe has no upstream connection |
| `NO_DOWNSTREAM_CONNECTION` | WARNING | Pipe has no downstream connection |
| `INVERT_MISMATCH_UPSTREAM` | WARNING | Invert mismatch at upstream connection |
| `INVERT_MISMATCH_DOWNSTREAM` | WARNING | Invert mismatch at downstream connection |

### Hydraulic Codes

| Code | Severity | Description |
|------|----------|-------------|
| `SLOPE_TOO_LOW` | ERROR | Slope below minimum for diameter |
| `SLOPE_TOO_HIGH` | ERROR | Slope exceeds maximum allowable |
| `VELOCITY_TOO_LOW` | WARNING | Velocity below 2 fps (sediment settling) |
| `VELOCITY_TOO_HIGH` | WARNING | Velocity exceeds material-specific maximum |
| `MISSING_HYDRAULIC_DATA` | ERROR | Missing diameter or slope data |

### Standards Codes

| Code | Severity | Description |
|------|----------|-------------|
| `DIAMETER_TOO_SMALL` | ERROR | Diameter below jurisdiction minimum |
| `NON_STANDARD_DIAMETER` | INFO | Non-standard pipe size used |
| `MATERIAL_NOT_SPECIFIED` | WARNING | Pipe material not specified |
| `DIAMETER_INCREASE_DOWNSTREAM` | WARNING | Upsizing in flow direction |

### Topology Codes

| Code | Severity | Description |
|------|----------|-------------|
| `NO_OUTFALL` | ERROR | Network has no outfall structure |
| `REVERSE_DRAINAGE` | ERROR | Pipe drains uphill |
| `NETWORK_LOOP_DETECTED` | WARNING | Circular flow pattern detected |

### Geometry Codes

| Code | Severity | Description |
|------|----------|-------------|
| `MISSING_GEOMETRY` | ERROR | No geometry defined for pipe/structure |
| `PIPE_TOO_SHORT` | WARNING | Unusually short pipe segment |

---

## Best Practices

### 1. Validate Early and Often

- Run validation during design, not just at the end
- Fix errors incrementally as you design
- Use validation to guide design decisions

### 2. Understand Severity Levels

- **Errors**: Must be fixed before construction
- **Warnings**: Review carefully, may be acceptable with justification
- **Info**: Informational notices, no action required

### 3. Document Exceptions

When warnings are acceptable:
- Document the justification
- Get approval from reviewing engineer
- Note in project records

Example: "12" pipe used instead of 15" due to space constraints; velocity still adequate at 2.3 fps"

### 4. Use Appropriate Standards

- **Default**: General commercial/residential projects
- **Strict**: High-risk areas, critical infrastructure, conservative jurisdictions
- **Custom**: When jurisdiction has specific requirements

### 5. Review Statistics

Network statistics help identify patterns:
- If average velocity is low across network, consider steeper slopes
- If many pipes are at minimum slope, review grades
- If diameter range is very wide, review sizing approach

### 6. Fix by Category

Address issues systematically:
1. **Geometry** - Ensure all data is present
2. **Continuity** - Fix connections and references
3. **Topology** - Ensure proper drainage direction
4. **Hydraulic** - Adjust slopes and diameters
5. **Standards** - Verify compliance

### 7. Export Validation Reports

Use validation results for:
- Design review meetings
- Submittal packages
- Quality assurance documentation
- Training examples

### 8. Understand Manning's Equation

The validator uses Manning's equation for velocity and capacity:

```
V = (1.486/n) × R^(2/3) × S^(1/2)
Q = A × V

Where:
V = velocity (fps)
n = roughness coefficient (0.013 for smooth pipe)
R = hydraulic radius (ft)
S = slope (decimal)
Q = flow (cfs)
A = area (ft²)
```

### 9. Common Fixes

**Slope Too Low:**
- Increase slope if possible
- Consider larger diameter (more efficient)
- Review if inlet elevation can be lowered

**Velocity Too High:**
- Decrease slope
- Increase diameter
- Add energy dissipation structure

**Reverse Drainage:**
- Check invert elevations for errors
- Verify flow direction
- May need to redesign segment

**Missing Outfall:**
- Add outfall structure
- Connect to existing system
- Define discharge point

---

## Testing

Run validation unit tests:

```bash
cd backend
pytest test_pipe_validation.py -v
```

Expected output:
```
test_pipe_validation.py::TestPipeDesignStandards::test_get_min_slope_for_diameter PASSED
test_pipe_validation.py::TestHydraulicCalculations::test_calculate_velocity PASSED
test_pipe_validation.py::TestValidationIssue::test_create_issue PASSED
test_pipe_validation.py::TestValidationResult::test_add_issue_error PASSED
...
```

---

## Troubleshooting

### Validation Returns No Results

**Cause**: Network has no pipes or structures
**Solution**: Ensure network is populated with data

### Validation Fails with Error

**Cause**: Database connection issue or missing data
**Solution**: Check database connection, verify network exists

### Too Many Warnings

**Cause**: Network may need design refinement
**Solution**: Review warnings systematically, adjust design as needed

### False Positives

**Cause**: Custom design conditions not accounted for
**Solution**: Consider creating custom standards or documenting exceptions

---

## Future Enhancements

Planned improvements to the validation system:

- [ ] Hydraulic grade line (HGL) analysis
- [ ] Capacity vs. flow analysis (design storm)
- [ ] Clash detection with other utilities
- [ ] Buildability checks (access, easements)
- [ ] Cost estimation integration
- [ ] Automated fix suggestions
- [ ] Historical validation reporting
- [ ] Export to PDF report

---

## References

- **ASCE**: American Society of Civil Engineers design standards
- **APWA**: American Public Works Association guidelines
- **Manning's Equation**: Standard hydraulic calculation method
- **Industry Standards**: Based on common municipal requirements

---

## Support

For questions or issues:
1. Check this documentation
2. Review API endpoint documentation
3. Run unit tests to verify installation
4. Submit issues on GitHub

---

**Last Updated**: October 2025
**Version**: 1.0.0
**Maintainer**: ACAD-GIS Development Team
