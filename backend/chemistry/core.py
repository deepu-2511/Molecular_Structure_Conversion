from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, Crippen, rdMolDescriptors


class MoleculeEngine:
    """Core molecular parsing, validation and property engine."""

    @staticmethod
    def from_smiles(smiles: str):
        if not smiles or not smiles.strip():
            raise ValueError("SMILES input cannot be empty.")

        molecule = Chem.MolFromSmiles(smiles.strip())

        if molecule is None:
            raise ValueError("Invalid SMILES: unable to parse molecule.")

        Chem.SanitizeMol(molecule)

        return molecule

    @staticmethod
    def get_properties(molecule):
        return {
            "formula": rdMolDescriptors.CalcMolFormula(molecule),
            "molecular_weight": round(Descriptors.MolWt(molecule), 4),
            "exact_mass": round(Descriptors.ExactMolWt(molecule), 6),
            "logp": round(Crippen.MolLogP(molecule), 4),
            "tpsa": round(rdMolDescriptors.CalcTPSA(molecule), 4),
            "hbd": Lipinski.NumHDonors(molecule),
            "hba": Lipinski.NumHAcceptors(molecule),
            "rotatable_bonds": Lipinski.NumRotatableBonds(molecule),
            "heavy_atoms": molecule.GetNumHeavyAtoms(),
            "rings": rdMolDescriptors.CalcNumRings(molecule),
            "aromatic_rings": rdMolDescriptors.CalcNumAromaticRings(molecule),
            "formal_charge": Chem.GetFormalCharge(molecule),
        }

    @staticmethod
    def get_identifiers(molecule):
        return {
            "canonical_smiles": Chem.MolToSmiles(
                molecule,
                canonical=True
            ),
            "isomeric_smiles": Chem.MolToSmiles(
                molecule,
                canonical=True,
                isomericSmiles=True
            ),
            "inchi": Chem.MolToInchi(molecule),
            "inchikey": Chem.InchiToInchiKey(
                Chem.MolToInchi(molecule)
            ),
        }

    @classmethod
    def analyze_smiles(cls, smiles: str):
        molecule = cls.from_smiles(smiles)

        return {
            "valid": True,
            "input_smiles": smiles,
            "identifiers": cls.get_identifiers(molecule),
            "properties": cls.get_properties(molecule),
        }