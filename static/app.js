// static/app.js
class CloudShield {
  constructor() {
    this.history = JSON.parse(localStorage.getItem('scanHistory') || '[]');
    this.init();
  }

  init() {
    document.getElementById('scanBtn').addEventListener('click', () => this.scan());
    this.renderHistory();
  }

  async scan() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) return alert('Pilih file dulu!');

    const btn = document.getElementById('scanBtn');
    btn.disabled = true;
    btn.textContent = 'Memindai...';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/scan', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Forwarded-For': '127.0.0.1' // untuk rate limit di localhost
        }
      });

      if (res.status === 429) {
        alert('Terlalu banyak permintaan! Tunggu 1 menit.');
        return;
      }

      const data = await res.json();
      this.showResult(data);
      this.saveToHistory(data);
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Scan File';
    }
  }

  showResult(data) {
    const status = data.malicious 
      ? `<span style="color:red">❌ BERBAHAYA</span>`
      : `<span style="color:green">✅ AMAN</span>`;

    document.getElementById('result').innerHTML = `
      <div class="result">
        <h3>Hasil Pemindaian</h3>
        <p><strong>File:</strong> ${data.filename}</p>
        <p><strong>Status:</strong> ${status}</p>
        <p><strong>Alasan:</strong> ${data.reason}</p>
        ${data.hash ? `<p><strong>Hash:</strong> ${data.hash.substring(0, 16)}...</p>` : ''}
        <button onclick="cloudshield.exportReport(${JSON.stringify(data)})">Ekspor Laporan</button>
      </div>
    `;
  }

  saveToHistory(scan) {
    this.history.unshift({ ...scan, timestamp: new Date().toISOString() });
    this.history = this.history.slice(0, 10); // Simpan 10 terakhir
    localStorage.setItem('scanHistory', JSON.stringify(this.history));
    this.renderHistory();
  }

  renderHistory() {
    const list = document.getElementById('historyList') || document.createElement('div');
    list.id = 'historyList';
    list.innerHTML = `
      <h3>Riwayat (Offline)</h3>
      ${this.history.map(item => `
        <div style="border-bottom:1px solid #eee;padding:8px">
          ${item.malicious ? '❌' : '✅'} ${item.filename}
        </div>
      `).join('')}
    `;
    if (!document.getElementById('historyList')) {
      document.body.appendChild(list);
    }
  }

  exportReport(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cloudshield-report-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

// Jalankan saat halaman siap
document.addEventListener('DOMContentLoaded', () => {
  window.cloudshield = new CloudShield();
});
