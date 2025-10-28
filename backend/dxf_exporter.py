"""
DXF Exporter
Reads drawing content from the database and writes a DXF file.

Strategy:
- If original DXF content exists, load it with ezdxf, optionally filter layers
  and/or exclude modelspace or paperspace, then save.
- If no original DXF exists, synthesize a minimal DXF from stored layers and
  block inserts, creating placeholder blocks so INSERTs are valid.

This preserves native coordinates and avoids CRS transforms. Georeferenced
drawings remain in their original CAD coordinate system.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import os

import ezdxf

# Support both running from backend/ and as a package import
try:  # pragma: no cover - import convenience
    from . import database  # type: ignore
except Exception:  # pragma: no cover - import convenience
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).resolve().parent))
    import database  # type: ignore


class DXFExporter:
    def __init__(self):
        pass

    def export_dxf(
        self,
        drawing_id: str,
        output_path: str,
        dxf_version: str = "AC1027",
        include_modelspace: bool = True,
        include_paperspace: bool = True,
        layer_filter: Optional[List[str]] = None,
    ) -> Dict:
        """Export a drawing to DXF.

        Returns stats dict: entities, layers, blocks, errors
        """

        stats = {
            "entities": 0,
            "text": 0,
            "dimensions": 0,
            "hatches": 0,
            "blocks": 0,
            "viewports": 0,
            "layers": [],
            "linetypes": [],
            "errors": [],
        }

        drawing = database.get_drawing(drawing_id)
        if not drawing:
            raise ValueError("Drawing not found")

        layers = database.get_layers(drawing_id)
        inserts = database.get_block_inserts(drawing_id)

        # Preferred: rehydrate from original DXF if available
        original_dxf = drawing.get("dxf_content")
        if original_dxf:
            try:
                # Use text loader to avoid temporary files when parsing
                doc = ezdxf.readfile_from_string(original_dxf)
            except AttributeError:
                # Older ezdxf versions do not have readfile_from_string; fallback to tmp path
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf", mode="w", encoding="utf-8", newline="") as tmp:
                    tmp.write(original_dxf)
                    tmp_path = tmp.name
                try:
                    doc = ezdxf.readfile(tmp_path)
                finally:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass

            # Optionally filter to specific layers
            allowed_layers = set(layer_filter) if layer_filter else None

            # Modelspace and paperspace control
            if not include_modelspace:
                try:
                    msp = doc.modelspace()
                    msp.delete_all_entities()
                except Exception:
                    pass

            if not include_paperspace:
                try:
                    for layout in list(doc.layouts):
                        if layout.name != "Model":
                            # Remove all entities in each paperspace layout
                            try:
                                layout.delete_all_entities()
                            except Exception:
                                pass
                except Exception:
                    pass

            # Layer filtering by deleting entities not on allowed layers
            if allowed_layers is not None:
                try:
                    # Filter modelspace
                    msp = doc.modelspace()
                    for e in list(msp):
                        try:
                            if e.dxf.layer not in allowed_layers:
                                msp.delete_entity(e)
                        except Exception:
                            continue
                    # Filter each layout (paperspace)
                    for layout in list(doc.layouts):
                        if layout.name == "Model":
                            continue
                        for e in list(layout):
                            try:
                                if e.dxf.layer not in allowed_layers:
                                    layout.delete_entity(e)
                            except Exception:
                                continue
                except Exception as exc:
                    stats["errors"].append(f"Layer filter failed: {exc}")

            # Save with requested version
            try:
                # ensure DXF version
                doc.header["$ACADVER"] = dxf_version
            except Exception:
                pass

            try:
                doc.saveas(output_path)
            except Exception as exc:
                stats["errors"].append(f"Failed saving DXF: {exc}")
                raise

            # Build rough stats from doc contents
            try:
                stats["layers"] = [l.dxf.name for l in doc.layers]
                stats["blocks"] = len(inserts)
                stats["entities"] = sum(1 for _ in doc.modelspace())
            except Exception:
                pass

            return stats

        # Fallback: synthesize minimal DXF
        doc = ezdxf.new(dxf_version)
        msp = doc.modelspace()

        # Create layers
        for lyr in layers:
            name = lyr.get("layer_name") or "0"
            try:
                if name not in doc.layers:
                    doc.layers.add(name)
            except Exception:
                # ignore invalid names
                continue

        # Create placeholder block definitions for all block names we will reference
        unique_block_names = set(i.get("block_name") for i in inserts if i.get("block_name"))
        for bname in unique_block_names:
            try:
                if bname and bname not in doc.blocks:
                    blk = doc.blocks.new(name=bname)
                    # Draw a small square placeholder centered at origin
                    size = 1.0
                    blk.add_lwpolyline([( -size, -size), ( size, -size), ( size, size), ( -size, size), ( -size, -size)])
            except Exception as exc:
                stats["errors"].append(f"Block '{bname}' placeholder failed: {exc}")

        # Add inserts into modelspace
        for ins in inserts:
            try:
                bname = ins.get("block_name")
                if not bname:
                    continue
                layer_name = ins.get("layer_name") or "0"
                ipt = (float(ins.get("insert_x", 0.0)), float(ins.get("insert_y", 0.0)), float(ins.get("insert_z")) if ins.get("insert_z") is not None else 0.0)
                sx = float(ins.get("scale_x", 1.0)) or 1.0
                sy = float(ins.get("scale_y", 1.0)) or 1.0
                rotation = float(ins.get("rotation", 0.0)) or 0.0
                e = msp.add_blockref(bname, ipt, dxfattribs={"layer": layer_name})
                if sx != 1.0:
                    e.dxf.xscale = sx
                if sy != 1.0:
                    e.dxf.yscale = sy
                if rotation:
                    e.dxf.rotation = rotation
                stats["blocks"] += 1
                stats["entities"] += 1
            except Exception as exc:
                stats["errors"].append(f"Insert add failed: {exc}")

        try:
            doc.saveas(output_path)
        except Exception as exc:
            stats["errors"].append(f"Failed saving synthesized DXF: {exc}")
            raise

        stats["layers"] = [l.get("layer_name") for l in layers]
        return stats

