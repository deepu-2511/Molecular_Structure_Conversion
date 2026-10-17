
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import shutil
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.chemistry.core import MoleculeEngine
from backend.chemistry.structure_2d import Structure2DRenderer
from backend.chemistry.structure_3d import Structure3DEngine
from backend.chemistry.iupac import (
    IUPACResolver,
    AmbiguousChemicalNameError,
    ChemicalNameResolutionError,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="MolecularStructureAI",
    description=(
        "AI-assisted molecular structure generation, "
        "visualization and chemical analysis platform."
    ),
    version="0.2.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "https://molecular-structure-conversion.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC EXPORTS
# ============================================================

app.mount(
    "/exports",
    StaticFiles(directory=str(EXPORT_DIR)),
    name="exports",
)


# ============================================================
# REQUEST MODELS
# ============================================================

class SMILESRequest(BaseModel):
    smiles: str = Field(
        ...,
        min_length=1,
        description="SMILES representation of the molecule",
    )


class IUPACRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        description="IUPAC or chemical name",
    )


# ============================================================
# ERROR HANDLING
# ============================================================

def resolver_http_exception(error):
    """Convert chemical-name errors into structured API responses."""

    if isinstance(error, AmbiguousChemicalNameError):
        return HTTPException(
            status_code=409,
            detail={
                "success": False,
                "code": "ambiguous_chemical_name",
                "error": str(error),
                "candidates": [
                    {
                        "cid": candidate.get("cid"),
                        "iupac_name": candidate.get("iupac_name"),
                        "formula": candidate.get("formula"),
                        "inchikey": candidate.get("inchikey"),
                    }
                    for candidate in error.candidates
                ],
            },
        )

    if isinstance(error, ChemicalNameResolutionError):
        return HTTPException(
            status_code=422,
            detail={
                "success": False,
                "code": "chemical_name_resolution_failed",
                "error": str(error),
            },
        )

    return HTTPException(
        status_code=400,
        detail={
            "success": False,
            "error": str(error),
        },
    )


def get_job_directory(job_id: str) -> Path:
    """Validate a job ID before accessing its output directory."""

    if not re.fullmatch(r"[0-9a-f]{32}", job_id):
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid job ID.",
            },
        )

    job_dir = EXPORT_DIR / job_id

    if job_dir.resolve().parent != EXPORT_DIR.resolve():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid job path.",
            },
        )

    return job_dir


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "MolecularStructureAI",
        "version": app.version,
        "status": "online",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "chemistry_engine": "RDKit",
        "name_resolver": "PubChem PUG REST",
    }


# ============================================================
# COMMON STRUCTURE GENERATION ENGINE
# ============================================================

def generate_complete_structure(
    molecule,
    input_type,
    input_value,
):
    """
    Shared generation engine for SMILES and IUPAC input.

    Generates identifiers, descriptors, 2D images, a computational
    3D conformer, structure exports and metadata.
    """

    job_id = uuid.uuid4().hex
    job_dir = get_job_directory(job_id)

    job_dir.mkdir(
        parents=True,
        exist_ok=False,
    )

    try:
        # 1. Identifiers
        identifiers = MoleculeEngine.get_identifiers(molecule)

        # 2. Molecular properties
        properties = MoleculeEngine.get_properties(molecule)

        # 3. Generate 2D outputs
        png_path = job_dir / "structure_2d.png"
        svg_path = job_dir / "structure_2d.svg"

        Structure2DRenderer.render_png(
            molecule,
            png_path,
            width=1200,
            height=900,
        )

        Structure2DRenderer.render_svg(
            molecule,
            svg_path,
            width=1200,
            height=900,
        )

        # 4. Generate computational 3D conformer
        result_3d = Structure3DEngine.generate_3d(molecule)
        molecule_3d = result_3d["molecule"]

        # 5. Export 3D formats
        Structure3DEngine.export_sdf(
            molecule_3d,
            job_dir / "structure_3d.sdf",
        )

        Structure3DEngine.export_mol(
            molecule_3d,
            job_dir / "structure_3d.mol",
        )

        Structure3DEngine.export_pdb(
            molecule_3d,
            job_dir / "structure_3d.pdb",
        )

        Structure3DEngine.export_xyz(
            molecule_3d,
            job_dir / "structure_3d.xyz",
        )

        # 6. Metadata
        created_at = datetime.now(timezone.utc).isoformat()

        metadata = {
            "job_id": job_id,
            "created_at": created_at,
            "input": {
                "type": input_type,
                "value": input_value,
            },
            "identifiers": identifiers,
            "properties": properties,
            "structure_2d": {
                "png": f"/exports/{job_id}/structure_2d.png",
                "svg": f"/exports/{job_id}/structure_2d.svg",
            },
            "structure_3d": {
                "sdf": f"/exports/{job_id}/structure_3d.sdf",
                "mol": f"/exports/{job_id}/structure_3d.mol",
                "pdb": f"/exports/{job_id}/structure_3d.pdb",
                "xyz": f"/exports/{job_id}/structure_3d.xyz",
                "optimization_method": result_3d[
                    "optimization_method"
                ],
                "energy": result_3d["energy"],
                "atom_count": result_3d["atom_count"],
                "conformer_count": result_3d["conformer_count"],
            },
        }

        metadata_path = job_dir / "metadata.json"

        metadata_path.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )

        return {
            "success": True,
            **metadata,
        }

    except Exception:
        # Remove partial files if generation fails.
        shutil.rmtree(job_dir, ignore_errors=True)
        raise


# ============================================================
# SMILES â†’ STRUCTURE
# ============================================================

@app.post("/api/v1/structure/smiles")
def smiles_to_structure(request: SMILESRequest):
    try:
        molecule = MoleculeEngine.from_smiles(request.smiles)

        identifiers = MoleculeEngine.get_identifiers(molecule)
        properties = MoleculeEngine.get_properties(molecule)

        return {
            "success": True,
            "input": {
                "type": "smiles",
                "value": request.smiles,
            },
            "identifiers": identifiers,
            "properties": properties,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(error),
            },
        ) from error


# ============================================================
# SMILES â†’ COMPLETE GENERATION
# ============================================================

@app.post("/api/v1/structure/smiles/generate")
def generate_smiles_structure(request: SMILESRequest):
    try:
        molecule = MoleculeEngine.from_smiles(request.smiles)

        return generate_complete_structure(
            molecule=molecule,
            input_type="smiles",
            input_value=request.smiles,
        )

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(error),
            },
        ) from error


# ============================================================
# IUPAC â†’ RESOLVE ONLY
# ============================================================

@app.post("/api/v1/structure/iupac")
def iupac_to_structure(request: IUPACRequest):
    try:
        resolved = IUPACResolver.resolve(request.name)

        molecule = MoleculeEngine.from_smiles(
            resolved["smiles"]
        )

        return {
            "success": True,
            "input": {
                "type": "iupac",
                "value": request.name,
            },
            "resolver": {
                "source": resolved.get("source", "PubChem"),
                "match_type": resolved.get("match_type"),
                "cid": resolved["cid"],
                "resolved_name": resolved["iupac_name"],
            },
            "resolved_structure": {
                "smiles": resolved["smiles"],
            },
            "identifiers": MoleculeEngine.get_identifiers(molecule),
            "properties": MoleculeEngine.get_properties(molecule),
        }

    except ChemicalNameResolutionError as error:
        raise resolver_http_exception(error) from error

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(error),
            },
        ) from error


# ============================================================
# IUPAC â†’ COMPLETE GENERATION
# ============================================================

@app.post("/api/v1/structure/iupac/generate")
def generate_iupac_structure(request: IUPACRequest):
    try:
        # 1. Resolve the chemical name
        resolved = IUPACResolver.resolve(request.name)

        # 2. Validate the resolved molecular representation
        molecule = MoleculeEngine.from_smiles(
            resolved["smiles"]
        )

        # 3. Generate the structure package
        result = generate_complete_structure(
            molecule=molecule,
            input_type="iupac",
            input_value=request.name,
        )

        # 4. Add resolver provenance
        resolver_metadata = {
            "source": resolved.get("source", "PubChem"),
            "match_type": resolved.get("match_type"),
            "cid": resolved["cid"],
            "resolved_name": resolved["iupac_name"],
            "resolved_smiles": resolved["smiles"],
            "inchikey": resolved.get("inchikey"),
        }

        result["resolver"] = resolver_metadata

        # 5. Persist resolver metadata
        job_dir = get_job_directory(result["job_id"])
        metadata_path = job_dir / "metadata.json"

        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )

        metadata["resolver"] = resolver_metadata

        metadata_path.write_text(
            json.dumps(metadata, indent=2),
            encoding="utf-8",
        )

        return result

    except ChemicalNameResolutionError as error:
        raise resolver_http_exception(error) from error

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": str(error),
            },
        ) from error


# ============================================================
# GET STRUCTURE RESULT
# ============================================================

@app.get("/api/v1/structure/{job_id}")
def get_structure(job_id: str):
    job_dir = get_job_directory(job_id)
    metadata_path = job_dir / "metadata.json"

    if not metadata_path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Structure job not found.",
                "job_id": job_id,
            },
        )

    try:
        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )

        return {
            "success": True,
            **metadata,
        }

    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Unable to read structure metadata.",
            },
        ) from error


# ============================================================
# DOWNLOAD STRUCTURE FILE
# ============================================================

@app.get(
    "/api/v1/structure/{job_id}/download/{file_format}"
)
def download_structure(job_id: str, file_format: str):
    allowed_formats = {
        "png": "structure_2d.png",
        "svg": "structure_2d.svg",
        "sdf": "structure_3d.sdf",
        "mol": "structure_3d.mol",
        "pdb": "structure_3d.pdb",
        "xyz": "structure_3d.xyz",
        "json": "metadata.json",
    }

    file_format = file_format.lower()

    if file_format not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": (
                    "Unsupported format. Supported formats: "
                    + ", ".join(allowed_formats.keys())
                ),
            },
        )

    job_dir = get_job_directory(job_id)
    file_path = job_dir / allowed_formats[file_format]

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Requested file not found.",
                "job_id": job_id,
                "format": file_format,
            },
        )

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
    )


# ============================================================
# JSON RESULT
# ============================================================

@app.get("/api/v1/structure/{job_id}/json")
def get_structure_json(job_id: str):
    job_dir = get_job_directory(job_id)
    metadata_path = job_dir / "metadata.json"

    if not metadata_path.is_file():
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "Structure job not found.",
                "job_id": job_id,
            },
        )

    return FileResponse(
        path=str(metadata_path),
        filename="metadata.json",
        media_type="application/json",
    )



