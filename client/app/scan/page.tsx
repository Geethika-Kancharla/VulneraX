"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [url, setUrl] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    if (!url.trim()) return alert("Please enter a URL");

    setLoading(true);
    setResponse("");

    try {
        const res = await axios.post("/api/scan", {
            input: `Scan ${url}`,
          });

      if (res.data) {
        setResponse(JSON.stringify(res.data, null, 2));
      } else {
        setResponse("No response from agent.");
      }
    } catch (error: any) {
      setResponse("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <div className="max-w-xl mx-auto bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-4">Security Scanner</h1>

        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter a target URL (e.g., http://example.com)"
          className="w-full p-2 border rounded mb-4"
        />

        <button
          onClick={handleScan}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {loading ? "Scanning..." : "Scan"}
        </button>

        <pre className="mt-6 bg-gray-200 p-4 rounded max-h-96 overflow-auto">
          {response || "Results will appear here..."}
        </pre>
      </div>
    </div>
  );
}
