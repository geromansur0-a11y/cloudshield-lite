import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch('http://localhost:8000/scan', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div style={{ padding: 20, maxWidth: 600, margin: '0 auto', fontFamily: 'system-ui' }}>
      <h1 style={{ textAlign: 'center', color: '#1e40af' }}>🛡️ CloudShield Lite</h1>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        style={{ width: '100%', marginBottom: 10 }}
      />
      <button
        onClick={handleScan}
        disabled={!file || loading}
        style={{
          width: '108%',
          padding: '12px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: 6,
          fontSize: 16,
        }}
      >
        {loading ? '🔍 Memindai...' : 'Scan File'}
      </button>

      {result && (
        <div style={{ marginTop: 20, padding: 15, borderRadius: 8, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
          <h3>Hasil Pemindaian</h3>
          <p>
            Status: <strong style={{ color: result.malicious ? 'red' : 'green' }}>
              {result.malicious ? '❌ Berbahaya' : '✅ Aman'}
            </strong>
          </p>
          <p>File: {result.filename}</p>
          <p>Hash: {result.hash?.substring(0, 16)}...</p>
          {result.ai_score > 0 && <p>Skor AI: {(result.ai_score * 100).toFixed(1)}%</p>}
          {result.reason && <p>Alasan: {result.reason}</p>}
        </div>
      )}
    </div>
  );
      }
