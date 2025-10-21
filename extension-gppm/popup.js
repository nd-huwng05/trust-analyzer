// popup.js - tương tác UI popup
document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('analyze-btn');
  const urlTextEl = document.getElementById('url-text');
  const titleEl = document.getElementById('page-title');

  const resultEl = document.getElementById('result');
  const loadingEl = document.getElementById('loading');
  const errorCardEl = document.getElementById('error');
  const errorTextEl = document.getElementById('error-text');
  const scoreBadgeEl = document.getElementById('score-badge');
  const warningEl = document.getElementById('warning');
  const detailsEl = document.getElementById('details');

  // Hiển thị URL + title của tab hiện tại
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tab = tabs && tabs[0];
    if (!tab) {
      urlTextEl.textContent = 'Không có tab';
      titleEl.textContent = '';
      return;
    }
    const url = tab.url || '';
    const title = tab.title || 'Không có tiêu đề';
    urlTextEl.textContent = url.length > 70 ? url.substring(0, 70) + '...' : url;
    titleEl.textContent = title;
  });

  analyzeBtn.addEventListener('click', async () => {
    // Lấy URL hiện tại
    const tabs = await new Promise(resolve => chrome.tabs.query({ active: true, currentWindow: true }, resolve));
    const tab = tabs && tabs[0];
    if (!tab || !tab.url) {
      showError('Không lấy được URL tab hiện tại.');
      return;
    }
    const currentUrl = tab.url;

    // Reset UI
    hideAllStates();
    loadingEl.classList.remove('hidden');

    try {
      const resp = await fetch('http://localhost:8000/api/trust-analyzer/analyze/full', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: currentUrl })
      });

      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`HTTP ${resp.status}: ${text ? text.substring(0, 200) : ''}`);
      }

      const data = await resp.json();
      loadingEl.classList.add('hidden');

      // Tính điểm (0..100)
      const scoreNum = Math.round((data.trust_score || 0) * 100);
      scoreBadgeEl.textContent = `${scoreNum}/100`;

      // Cảnh báo / icon / màu
      let icon = '', color = '', msg = '';
      if (data.error) {
        icon = 'error'; color = '#c62828'; msg = `Lỗi: ${data.error}`;
      } else if (scoreNum < 50) {
        icon = 'dangerous'; color = '#d32f2f'; msg = 'Cảnh báo: Có dấu hiệu lừa đảo!';
      } else if (scoreNum < 75) {
        icon = 'warning'; color = '#f57c00'; msg = 'Cẩn thận: Nên kiểm tra kỹ.';
      } else {
        icon = 'verified'; color = '#388e3c'; msg = 'An toàn: Trang web đáng tin cậy.';
      }

      warningEl.innerHTML = `
        <span class="material-icons" style="color:${color}; vertical-align:middle; font-size:20px; margin-right:6px;">
          ${icon}
        </span>
        <span style="font-weight:600;">${msg}</span>
      `;

      // Chi tiết
      let detailsHtml = '';
      if (data.name) detailsHtml += `Sản phẩm: <b>${escapeHtml(String(data.name))}</b><br>`;
      if (data.price) detailsHtml += `Giá: <b>${escapeHtml(String(data.price))}</b><br>`;
      if (data.seller) detailsHtml += `Người bán: <b>${escapeHtml(String(data.seller))}</b><br>`;
      if (data.url) detailsHtml += `URL: <small>${escapeHtml(String(data.url))}</small>`;

      detailsEl.innerHTML = detailsHtml;

      resultEl.classList.remove('hidden');
    } catch (err) {
      loadingEl.classList.add('hidden');
      showError(err.message || 'Lỗi không xác định');
      console.error('Fetch error:', err);
    }
  });

  function hideAllStates() {
    resultEl.classList.add('hidden');
    loadingEl.classList.add('hidden');
    errorCardEl.classList.add('hidden');
    warningEl.innerHTML = '';
    detailsEl.innerHTML = '';
  }

  function showError(msg) {
    errorTextEl.textContent = `Lỗi: ${msg}`;
    errorCardEl.classList.remove('hidden');
  }

  // Simple HTML escape
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (m) => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' })[m]);
  }
});