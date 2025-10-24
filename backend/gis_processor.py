"""
QGIS processing entry points for ACAD-GIS.

The module is intentionally lightweight so the rest of the application can
import it without hard failures when QGIS is not installed. Callers should use
``get_processor`` to obtain a processor instance; ``None`` is returned when
QGIS is unavailable so the API layer can degrade gracefully.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    from qgis.core import QgsApplication  # type: ignore

    QGIS_AVAILABLE = True
except Exception:  # pragma: no cover - absence of QGIS is expected in dev
    QgsApplication = None  # type: ignore
    QGIS_AVAILABLE = False


@dataclass
class QGISProcessor:
    """Thin wrapper that will host future QGIS processing helpers."""

    database_url: Optional[str]

    def __post_init__(self) -> None:
        if not QGIS_AVAILABLE:
            raise RuntimeError("QGIS is not available on this system.")

        # Lazy initialisation placeholder – flesh out when wiring full QGIS env.
        self._app: Optional[QgsApplication] = None  # type: ignore

    # Example placeholder methods ------------------------------------------------
    # Implementers can expand these to execute qgis processing algorithms and
    # return results or job identifiers.
    def buffer(self, *_args, **_kwargs):
        raise NotImplementedError("QGIS buffer processing not yet implemented.")


def _build_database_url() -> Optional[str]:
    """Assemble a DATABASE_URL from existing env vars if one is not provided."""

    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return dsn

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbname = os.getenv("DB_NAME", "postgres")
    port = os.getenv("DB_PORT", "5432")

    if host and user and password:
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    return None


def get_processor(database_url: Optional[str] = None) -> Optional[QGISProcessor]:
    """
    Return a QGISProcessor when QGIS is installed; otherwise ``None``.
    """

    if not QGIS_AVAILABLE:
        return None

    dsn = database_url or _build_database_url()
    return QGISProcessor(database_url=dsn)
