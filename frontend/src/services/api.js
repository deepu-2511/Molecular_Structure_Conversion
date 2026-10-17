const API_BASE_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8010"
).replace(/\/+$/, "");

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    const message =
      data?.detail?.error ||
      data?.detail ||
      "Request failed.";

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    );
  }

  return data;
}

export async function generateStructure(smiles) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/structure/smiles/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ smiles: smiles.trim() }),
    }
  );

  return handleResponse(response);
}

export async function generateIUPACStructure(name) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/structure/iupac/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ name: name.trim() }),
    }
  );

  return handleResponse(response);
}

export function getFileUrl(path) {
  if (!path) return "";

  if (/^https?:\/\//i.test(path)) {
    return path;
  }

  return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}
