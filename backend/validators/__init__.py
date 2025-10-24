"""
Validation modules for ACAD-GIS.
Provides comprehensive validation for pipe networks, alignments, and other civil design elements.
"""

from .pipe_network import (
    validate_pipe_network,
    ValidationResult,
    ValidationIssue,
    Severity
)

__all__ = [
    'validate_pipe_network',
    'ValidationResult',
    'ValidationIssue',
    'Severity'
]
