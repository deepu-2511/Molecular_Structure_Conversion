from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D


class Structure2DRenderer:
    """Professional 2D molecular structure renderer."""

    @staticmethod
    def prepare_molecule(molecule):
        """Generate clean 2D coordinates."""
        mol = Chem.Mol(molecule)
        Chem.rdDepictor.Compute2DCoords(mol)
        return mol

    @staticmethod
    def render_png(molecule, output_path, width=1200, height=900):
        """Render molecule as high-resolution PNG."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        mol = Structure2DRenderer.prepare_molecule(molecule)

        image = Draw.MolToImage(
            mol,
            size=(width, height)
        )

        image.save(output_path)

        return output_path

    @staticmethod
    def render_svg(molecule, output_path, width=1200, height=900):
        """Render molecule as scalable SVG."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        mol = Structure2DRenderer.prepare_molecule(molecule)

        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg = drawer.GetDrawingText()

        output_path.write_text(
            svg,
            encoding="utf-8"
        )

        return output_path
    