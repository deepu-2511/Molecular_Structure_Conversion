
from urllib.parse import quote
import unicodedata

import requests


class ChemicalNameResolutionError(ValueError):
    """Raised when a chemical name cannot be safely resolved."""


class AmbiguousChemicalNameError(ChemicalNameResolutionError):
    """Raised when multiple possible compounds are found."""

    def __init__(self, name, candidates):
        self.name = name
        self.candidates = candidates

        super().__init__(
            f"Could not confidently resolve '{name}'. "
            "Multiple candidates require verification or selection."
        )


class IUPACResolver:
    PUBCHEM_BASE_URL = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    )

    TIMEOUT = 15
    MAX_CANDIDATES = 10

    PROPERTY_FIELDS = (
        "ConnectivitySMILES,SMILES,IUPACName,InChI,"
        "InChIKey,MolecularFormula,MolecularWeight"
    )

    @staticmethod
    def normalize_name(name):
        """Normalize Unicode and whitespace without changing chemistry."""
        name = unicodedata.normalize("NFKC", name or "")
        return " ".join(name.split()).strip()

    @classmethod
    def _get_json(cls, url, params=None):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=cls.TIMEOUT,
                headers={"Accept": "application/json"},
            )
        except requests.RequestException as error:
            raise ChemicalNameResolutionError(
                f"Unable to contact PubChem: {error}"
            ) from error

        # No result is normal during a fallback search.
        if response.status_code in (400, 404):
            return None

        try:
            response.raise_for_status()
        except requests.RequestException as error:
            raise ChemicalNameResolutionError(
                f"PubChem returned HTTP {response.status_code}."
            ) from error

        try:
            return response.json()
        except ValueError as error:
            raise ChemicalNameResolutionError(
                "PubChem returned an invalid JSON response."
            ) from error

    @classmethod
    def _get_cids(cls, name, word_search=False):
        encoded_name = quote(name, safe="")

        url = (
            f"{cls.PUBCHEM_BASE_URL}/compound/name/"
            f"{encoded_name}/cids/JSON"
        )

        params = {"name_type": "word"} if word_search else None
        data = cls._get_json(url, params=params)

        if not data:
            return []

        cids = data.get("IdentifierList", {}).get("CID", [])
        return list(dict.fromkeys(cids))

    @classmethod
    def _get_properties(cls, cid):
        url = (
            f"{cls.PUBCHEM_BASE_URL}/compound/cid/{cid}/"
            f"property/{cls.PROPERTY_FIELDS}/JSON"
        )

        data = cls._get_json(url)

        if not data:
            return None

        try:
            return data["PropertyTable"]["Properties"][0]
        except (KeyError, IndexError, TypeError):
            return None

    @classmethod
    def _get_synonyms(cls, cid):
        url = (
            f"{cls.PUBCHEM_BASE_URL}/compound/cid/{cid}/"
            "synonyms/JSON"
        )

        data = cls._get_json(url)

        if not data:
            return []

        try:
            records = data["InformationList"]["Information"]
            return records[0].get("Synonym", [])
        except (KeyError, IndexError, TypeError):
            return []

    @classmethod
    def _build_candidate(cls, cid):
        properties = cls._get_properties(cid)

        if not properties:
            return None

        smiles = (
            properties.get("ConnectivitySMILES")
            or properties.get("SMILES")
        )

        if not smiles:
            return None

        return {
            "cid": properties.get("CID", cid),
            "iupac_name": properties.get("IUPACName"),
            "canonical_smiles": properties.get("ConnectivitySMILES"),
            "isomeric_smiles": properties.get("SMILES"),
            "smiles": smiles,
            "inchi": properties.get("InChI"),
            "inchikey": properties.get("InChIKey"),
            "formula": properties.get("MolecularFormula"),
            "molecular_weight": properties.get("MolecularWeight"),
        }

    @classmethod
    def _matches_name(cls, name, candidate):
        """Check exact normalized equality against a returned name/synonym."""
        target = cls.normalize_name(name).casefold()

        possible_names = [
            candidate.get("iupac_name"),
            *cls._get_synonyms(candidate["cid"]),
        ]

        return any(
            isinstance(value, str)
            and cls.normalize_name(value).casefold() == target
            for value in possible_names
        )

    @classmethod
    def _candidate_list(cls, cids):
        candidates = []

        for cid in cids[:cls.MAX_CANDIDATES]:
            candidate = cls._build_candidate(cid)

            if candidate:
                candidates.append(candidate)

        return candidates

    @classmethod
    def _result(cls, name, candidate, match_type):
        return {
            **candidate,
            "name": name,
            "source": "PubChem",
            "match_type": match_type,
        }

    @classmethod
    def resolve(cls, name):
        name = cls.normalize_name(name)

        if not name:
            raise ChemicalNameResolutionError(
                "Chemical name cannot be empty."
            )

        # Stage 1: exact PubChem name lookup.
        exact_cids = cls._get_cids(name)
        exact_candidates = cls._candidate_list(exact_cids)

        if len(exact_candidates) == 1:
            return cls._result(
                name, exact_candidates[0], "exact_name"
            )

        if len(exact_candidates) > 1:
            matching = [
                candidate
                for candidate in exact_candidates
                if cls._matches_name(name, candidate)
            ]

            if len(matching) == 1:
                return cls._result(
                    name, matching[0], "verified_exact_name"
                )

            raise AmbiguousChemicalNameError(
                name,
                matching if matching else exact_candidates,
            )

        # Stage 2: looser lookup for alternative naming styles.
        word_cids = cls._get_cids(name, word_search=True)
        candidates = cls._candidate_list(word_cids)

        if not candidates:
            raise ChemicalNameResolutionError(
                "No chemical structure was found for this name. "
                "Check the spelling or try a recognized synonym."
            )

        # Accept a fallback result only when the returned IUPAC name
        # or a PubChem synonym exactly matches the normalized input.
        matching = [
            candidate
            for candidate in candidates
            if cls._matches_name(name, candidate)
        ]

        if len(matching) == 1:
            return cls._result(
                name, matching[0], "verified_synonym"
            )

        # Never silently accept an unverified word-search candidate.
        raise AmbiguousChemicalNameError(
            name,
            matching if matching else candidates,
        )
