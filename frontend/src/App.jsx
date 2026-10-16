import { useState } from "react";

import {
  generateStructure,
  generateIUPACStructure,
  getFileUrl,
} from "./services/api";

import "./App.css";


function App() {
  // ============================================================
  // STATE
  // ============================================================

  const [inputMode, setInputMode] = useState("smiles");

  const [smiles, setSmiles] = useState(
    "CC(=O)OC1=CC=CC=C1C(=O)O"
  );

  const [iupacName, setIupacName] = useState(
    "2-acetyloxybenzoic acid"
  );

  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");


  // ============================================================
  // CHANGE INPUT MODE
  // ============================================================

  const handleModeChange = (mode) => {
    setInputMode(mode);
    setError("");
  };


  // ============================================================
  // GENERATE STRUCTURE
  // ============================================================

  const handleGenerate = async () => {
    setError("");
    setResult(null);

    try {
      setLoading(true);

      // --------------------------------------------------------
      // SMILES
      // --------------------------------------------------------

      if (inputMode === "smiles") {
        const value = smiles.trim();

        if (!value) {
          throw new Error("Please enter a SMILES string.");
        }

        const data = await generateStructure(value);

        setResult(data);
      }

      // --------------------------------------------------------
      // IUPAC
      // --------------------------------------------------------

      else if (inputMode === "iupac") {
        const value = iupacName.trim();

        if (!value) {
          throw new Error("Please enter an IUPAC name.");
        }

        const data = await generateIUPACStructure(value);

        setResult(data);
      }

      // --------------------------------------------------------
      // IMAGE
      // --------------------------------------------------------

      else if (inputMode === "image") {
        throw new Error(
          "Image input will be available in the next module."
        );
      }

    } catch (err) {
      setError(
        err?.message ||
        "Failed to generate molecular structure."
      );
    } finally {
      setLoading(false);
    }
  };


  // ============================================================
  // EXAMPLE INPUTS
  // ============================================================

  const useSMILESExample = () => {
    setSmiles("CC(=O)OC1=CC=CC=C1C(=O)O");
    setError("");
  };

  const useIUPACExample = () => {
    setIupacName("2-acetyloxybenzoic acid");
    setError("");
  };


  // ============================================================
  // DOWNLOAD URL
  // ============================================================

  const getDownloadUrl = (format) => {
    if (!result?.job_id) {
      return "#";
    }

    return getFileUrl(
      `/api/v1/structure/${result.job_id}/download/${format}`
    );
  };


  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="app-shell">

      {/* ======================================================
          SIDEBAR
      ======================================================= */}

      <aside className="sidebar">

        {/* BRAND */}

        <div className="brand">

          <div className="brand-mark">
            MS
          </div>

          <div>
            <div className="brand-name">
              MolecularStructureAI
            </div>

            <div className="brand-version">
              v0.1.0
            </div>
          </div>

        </div>


        {/* INPUT NAVIGATION */}

        <div className="sidebar-section">

          <div className="section-label">
            INPUT
          </div>


          <button
            className={`nav-item ${
              inputMode === "smiles" ? "active" : ""
            }`}
            onClick={() => handleModeChange("smiles")}
          >

            <span>
              SM
            </span>

            Structure

          </button>


          <button
            className={`nav-item ${
              inputMode === "iupac" ? "active" : ""
            }`}
            onClick={() => handleModeChange("iupac")}
          >

            <span>
              IN
            </span>

            IUPAC Name

          </button>


          <button
            className={`nav-item ${
              inputMode === "image" ? "active" : ""
            }`}
            onClick={() => handleModeChange("image")}
          >

            <span>
              IM
            </span>

            Image Input

          </button>

        </div>


        {/* ANALYSIS NAVIGATION */}

        <div className="sidebar-section">

          <div className="section-label">
            ANALYSIS
          </div>


          <button className="nav-item selected">
            <span>
              2D
            </span>

            Structure
          </button>


          <button className="nav-item">
            <span>
              PR
            </span>

            Properties
          </button>


          <button className="nav-item">
            <span>
              ID
            </span>

            Identifiers
          </button>

        </div>


        {/* SIDEBAR BOTTOM */}

        <div className="sidebar-bottom">

          <div className="engine-status">

            <span className="status-dot"></span>

            <div>

              <div className="status-title">
                CHEMISTRY ENGINE
              </div>

              <div className="status-value">
                RDKit
              </div>

            </div>

          </div>

        </div>

      </aside>


      {/* ======================================================
          MAIN AREA
      ======================================================= */}

      <main className="main-area">


        {/* ====================================================
            TOP BAR
        ===================================================== */}

        <header className="topbar">

          <div className="breadcrumb">

            <strong>
              MolecularStructureAI
            </strong>

            <span className="separator">
              /
            </span>

            <span>
              Structure Generator
            </span>

          </div>


          <div className="topbar-right">

            <div className="engine-pill">

              <span className="status-dot"></span>

              RDKit

            </div>


            <div className="system-chip">
              SYSTEM ONLINE
            </div>

          </div>

        </header>


        {/* ====================================================
            WORKSPACE
        ===================================================== */}

        <div className="workspace">


          {/* ==================================================
              WORKSPACE HEADER
          =================================================== */}

          <div className="workspace-header">

            <div>

              <div className="eyebrow">
                MOLECULAR ANALYSIS WORKSTATION
              </div>

              <h1>
                Molecular Structure Generator
              </h1>

              <p>
                Generate, validate and analyze molecular structures
                from chemical representations.
              </p>

            </div>


            <div className="job-badge">

              <span className="job-dot"></span>

              {result
                ? "STRUCTURE READY"
                : "READY"}

            </div>

          </div>


          {/* ==================================================
              INPUT PANEL
          =================================================== */}

          <section className="panel input-panel">


            <div className="panel-header">

              <div>

                <div className="panel-title">
                  Input Structure
                </div>

                <div className="panel-subtitle">

                  {inputMode === "smiles" &&
                    "Enter a valid SMILES representation"}

                  {inputMode === "iupac" &&
                    "Resolve a chemical name to molecular structure"}

                  {inputMode === "image" &&
                    "Reconstruct structure from a chemical image"}

                </div>

              </div>


              <div className="input-type">

                {inputMode === "smiles" && "SMILES"}

                {inputMode === "iupac" && "IUPAC"}

                {inputMode === "image" && "IMAGE"}

              </div>

            </div>


            {/* ==================================================
                SMILES
            =================================================== */}

            {inputMode === "smiles" && (

              <>

                <div className="input-row">

                  <textarea
                    value={smiles}
                    onChange={(event) =>
                      setSmiles(event.target.value)
                    }
                    placeholder="Enter SMILES..."
                    spellCheck="false"
                  />


                  <button
                    className="generate-button"
                    onClick={handleGenerate}
                    disabled={loading}
                  >

                    {loading ? (
                      <>
                        <span className="spinner"></span>
                        Processing
                      </>
                    ) : (
                      <>
                        Generate
                        <span>→</span>
                      </>
                    )}

                  </button>

                </div>


                <div className="input-footer">

                  <span>
                    Example
                  </span>

                  <button onClick={useSMILESExample}>
                    Aspirin
                  </button>

                  <span className="footer-separator">
                    /
                  </span>

                  <span>
                    CC(=O)OC1=CC=CC=C1C(=O)O
                  </span>

                </div>

              </>

            )}


            {/* ==================================================
                IUPAC
            =================================================== */}

            {inputMode === "iupac" && (

              <>

                <div className="input-row">

                  <textarea
                    value={iupacName}
                    onChange={(event) =>
                      setIupacName(event.target.value)
                    }
                    placeholder="Enter IUPAC name..."
                    spellCheck="false"
                  />


                  <button
                    className="generate-button"
                    onClick={handleGenerate}
                    disabled={loading}
                  >

                    {loading ? (
                      <>
                        <span className="spinner"></span>
                        Processing
                      </>
                    ) : (
                      <>
                        Generate
                        <span>→</span>
                      </>
                    )}

                  </button>

                </div>


                <div className="input-footer">

                  <span>
                    Example
                  </span>

                  <button onClick={useIUPACExample}>
                    2-acetyloxybenzoic acid
                  </button>

                  <span className="footer-separator">
                    /
                  </span>

                  <span>
                    PubChem resolver
                  </span>

                </div>

              </>

            )}


            {/* ==================================================
                IMAGE
            =================================================== */}

            {inputMode === "image" && (

              <>

                <div className="input-row">

                  <textarea
                    disabled
                    placeholder="Image input will be available in the next module."
                  />

                  <button
                    className="generate-button"
                    onClick={handleGenerate}
                    disabled={loading}
                  >
                    Generate
                    <span>→</span>
                  </button>

                </div>


                <div className="input-footer">

                  <span>
                    Image → Structure ML module
                  </span>

                </div>

              </>

            )}


          </section>


          {/* ==================================================
              ERROR
          =================================================== */}

          {error && (

            <div className="error-panel">

              <span>
                !
              </span>

              <div>
                {error}
              </div>

            </div>

          )}


          {/* ==================================================
              RESULT
          =================================================== */}

          {!result && !loading && (

            <div className="panel empty-workspace">

              <div className="empty-icon">
                +
              </div>

              <div className="empty-title">
                No structure generated
              </div>

              <div className="empty-text">
                Enter a SMILES string or IUPAC chemical name
                above to begin molecular analysis.
              </div>

            </div>

          )}


          {loading && (

            <div className="panel empty-workspace">

              <div className="empty-icon">
                <span className="spinner"></span>
              </div>

              <div className="empty-title">
                Generating molecular structure
              </div>

              <div className="empty-text">
                Parsing input, validating chemistry,
                generating 2D coordinates and 3D conformer.
              </div>

            </div>

          )}


          {result && !loading && (

            <>

              {/* ==================================================
                  MAIN RESULT LAYOUT
              =================================================== */}

              <div className="result-layout">


                {/* =================================================
                    STRUCTURE COLUMN
                ================================================== */}

                <section className="panel structure-panel">


                  <div className="panel-header">

                    <div>

                      <div className="panel-title">
                        Molecular Structure
                      </div>

                      <div className="panel-subtitle">
                        2D molecular graph generated by RDKit
                      </div>

                    </div>


                    <div className="structure-format">
                      PNG / SVG
                    </div>

                  </div>


                  <div className="structure-viewer">

                    {result.structure_2d?.png && (

                      <img
                        src={getFileUrl(
                          result.structure_2d.png
                        )}
                        alt="Generated molecular structure"
                      />

                    )}

                  </div>


                  {/* STRUCTURE FOOTER */}

                  <div className="structure-footer">

                    <div>

                      <span className="footer-label">
                        FORMULA
                      </span>

                      <strong>
                        {result.properties?.formula || "-"}
                      </strong>

                    </div>


                    <div>

                      <span className="footer-label">
                        MOLECULAR WEIGHT
                      </span>

                      <strong>
                        {result.properties?.molecular_weight ?? "-"}
                      </strong>

                    </div>


                    <div>

                      <span className="footer-label">
                        INPUT
                      </span>

                      <strong>
                        {result.input?.type || "-"}
                      </strong>

                    </div>

                  </div>

                </section>


                {/* =================================================
                    ANALYSIS COLUMN
                ================================================== */}

                <aside className="analysis-column">

                  <div className="panel analysis-panel">


                    {/* ---------------------------------------------
                        SUMMARY
                    ---------------------------------------------- */}

                    <div className="panel-header">

                      <div>

                        <div className="panel-title">
                          Molecular Summary
                        </div>

                        <div className="panel-subtitle">
                          Core molecular descriptors
                        </div>

                      </div>

                    </div>


                    <div className="summary-grid">


                      <div className="summary-card">

                        <span>
                          Formula
                        </span>

                        <strong>
                          {result.properties?.formula || "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Heavy Atoms
                        </span>

                        <strong>
                          {result.properties?.heavy_atoms ?? "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Rings
                        </span>

                        <strong>
                          {result.properties?.rings ?? "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Aromatic
                        </span>

                        <strong>
                          {result.properties?.aromatic_rings ?? "-"}
                        </strong>

                      </div>


                    </div>


                    {/* ---------------------------------------------
                        QUICK PROPERTIES
                    ---------------------------------------------- */}

                    <div className="quick-properties">

                      <div className="property-line">

                        <span>
                          Exact Mass
                        </span>

                        <strong>
                          {result.properties?.exact_mass ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          LogP
                        </span>

                        <strong>
                          {result.properties?.logp ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          TPSA
                        </span>

                        <strong>
                          {result.properties?.tpsa ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          HBD
                        </span>

                        <strong>
                          {result.properties?.hbd ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          HBA
                        </span>

                        <strong>
                          {result.properties?.hba ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          Rotatable Bonds
                        </span>

                        <strong>
                          {result.properties?.rotatable_bonds ?? "-"}
                        </strong>

                      </div>


                      <div className="property-line">

                        <span>
                          Formal Charge
                        </span>

                        <strong>
                          {result.properties?.formal_charge ?? "-"}
                        </strong>

                      </div>

                    </div>


                    {/* ---------------------------------------------
                        PROPERTY TABLE
                    ---------------------------------------------- */}

                    <div className="panel-header">

                      <div>

                        <div className="panel-title">
                          Chemical Properties
                        </div>

                      </div>

                    </div>


                    <div className="property-table">


                      <div className="property-row">

                        <span>
                          Molecular Weight
                        </span>

                        <strong>
                          {result.properties?.molecular_weight ?? "-"}
                        </strong>

                      </div>


                      <div className="property-row">

                        <span>
                          Exact Mass
                        </span>

                        <strong>
                          {result.properties?.exact_mass ?? "-"}
                        </strong>

                      </div>


                      <div className="property-row">

                        <span>
                          Heavy Atoms
                        </span>

                        <strong>
                          {result.properties?.heavy_atoms ?? "-"}
                        </strong>

                      </div>


                      <div className="property-row">

                        <span>
                          Ring Count
                        </span>

                        <strong>
                          {result.properties?.rings ?? "-"}
                        </strong>

                      </div>


                    </div>


                    {/* ---------------------------------------------
                        IDENTIFIERS
                    ---------------------------------------------- */}

                    <div className="panel-header">

                      <div>

                        <div className="panel-title">
                          Chemical Identifiers
                        </div>

                      </div>

                    </div>


                    <div className="identifier-block">

                      <div className="identifier-label">
                        CANONICAL SMILES
                      </div>

                      <div className="identifier-value">
                        {result.identifiers?.canonical_smiles || "-"}
                      </div>

                    </div>


                    <div className="identifier-block">

                      <div className="identifier-label">
                        ISOMERIC SMILES
                      </div>

                      <div className="identifier-value">
                        {result.identifiers?.isomeric_smiles || "-"}
                      </div>

                    </div>


                    <div className="identifier-block">

                      <div className="identifier-label">
                        INCHIKEY
                      </div>

                      <div className="identifier-value">
                        {result.identifiers?.inchikey || "-"}
                      </div>

                    </div>


                    {/* ---------------------------------------------
                        3D
                    ---------------------------------------------- */}

                    <div className="panel-header">

                      <div>

                        <div className="panel-title">
                          3D Conformer
                        </div>

                        <div className="panel-subtitle">
                          Computational geometry
                        </div>

                      </div>

                    </div>


                    <div className="threeD-grid">

                      <div className="summary-card">

                        <span>
                          Atoms
                        </span>

                        <strong>
                          {result.structure_3d?.atom_count ?? "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Conformers
                        </span>

                        <strong>
                          {result.structure_3d?.conformer_count ?? "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Method
                        </span>

                        <strong>
                          {result.structure_3d?.optimization_method || "-"}
                        </strong>

                      </div>


                      <div className="summary-card">

                        <span>
                          Energy
                        </span>

                        <strong>
                          {result.structure_3d?.energy ?? "-"}
                          <small>
                            kcal/mol
                          </small>
                        </strong>

                      </div>

                    </div>


                    <div className="method-note">

                      <div className="note-icon">
                        i
                      </div>

                      <p>
                        The 3D conformer is computationally
                        generated using RDKit ETKDG followed
                        by force-field optimization.
                      </p>

                    </div>


                  </div>

                </aside>

              </div>


              {/* ==================================================
                  EXPORT CENTER
              =================================================== */}

              <section className="panel export-panel">

                <div className="panel-header">

                  <div>

                    <div className="panel-title">
                      Export Center
                    </div>

                    <div className="panel-subtitle">
                      Download generated molecular structure
                      and metadata
                    </div>

                  </div>


                  <div className="export-count">
                    7 FORMATS
                  </div>

                </div>


                <div className="export-grid">


                  <a
                    className="download-card"
                    href={getDownloadUrl("png")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      PNG
                    </div>

                    <div className="download-info">
                      2D image
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("svg")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      SVG
                    </div>

                    <div className="download-info">
                      Vector structure
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("sdf")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      SDF
                    </div>

                    <div className="download-info">
                      3D structure
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("mol")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      MOL
                    </div>

                    <div className="download-info">
                      Molfile
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("pdb")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      PDB
                    </div>

                    <div className="download-info">
                      3D coordinates
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("xyz")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      XYZ
                    </div>

                    <div className="download-info">
                      Atomic coordinates
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                  <a
                    className="download-card"
                    href={getDownloadUrl("json")}
                    target="_blank"
                    rel="noreferrer"
                  >

                    <div className="download-format">
                      JSON
                    </div>

                    <div className="download-info">
                      Complete metadata
                    </div>

                    <div className="download-arrow">
                      ↓
                    </div>

                  </a>


                </div>

              </section>


              {/* ==================================================
                  JOB INFO
              =================================================== */}

              <div className="input-footer">

                <span>
                  JOB
                </span>

                <span>
                  {result.job_id}
                </span>

                <span className="footer-separator">
                  /
                </span>

                <span>
                  INPUT
                </span>

                <span>
                  {result.input?.type}
                </span>


                {result.resolver?.source && (

                  <>
                    <span className="footer-separator">
                      /
                    </span>

                    <span>
                      RESOLVER
                    </span>

                    <span>
                      {result.resolver.source}
                    </span>
                  </>

                )}

              </div>

            </>

          )}

        </div>

      </main>

    </div>
  );
}


export default App;