(function () {
  try {
    if (window.__taInjected) return;
    window.__taInjected = true;

    const container = document.createElement('div');
    container.id = 'ta-sidebar-container';
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.right = '0';
    container.style.height = '100vh';
    container.style.width = '360px';
    container.style.zIndex = '2147483647';
    container.style.pointerEvents = 'auto';
    container.style.background = '#fff';
    container.style.boxShadow = '0 4px 20px rgba(0,0,0,0.2)';
    container.style.borderLeft = '1px solid #ddd';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.fontFamily = 'Arial, sans-serif';
    container.style.color = '#111';

    const shadow = container.attachShadow({ mode: 'open' });

    shadow.innerHTML = `
      <style>
        :host { all: initial; }
        #ta-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          background: linear-gradient(90deg,#6b59ff,#8f5dfc);
          color: #fff;
          font-weight: 700;
          font-size: 16px;
        }
        #ta-close {
          background: transparent;
          border: none;
          color: #fff;
          font-size: 18px;
          cursor: pointer;
        }
        #ta-body {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
        }
        .ta-section {
          margin-bottom: 12px;
        }
        .btn {
          padding: 6px 12px;
          border-radius: 6px;
          border: none;
          cursor: pointer;
          background: #5e17eb;
          color: #fff;
          font-size: 14px;
        }
      </style>

      <div id="ta-header">
        Trust Analyzer
        <button id="ta-close">✕</button>
      </div>
      <div id="ta-body">
        <div class="ta-section">
          <div id="meta-url" style="font-size:12px;color:#666;">Đang lấy URL...</div>
          <div id="meta-title" style="font-weight:600;margin-top:4px;">Đang tải tiêu đề...</div>
        </div>
        <div class="ta-section">
          <button id="analyze-btn" class="btn">🔒 Phân tích ngay</button>
        </div>
        <div id="status" style="margin-top:8px;color:#444;">Sẵn sàng</div>
        <div id="result-area" style="display:none;margin-top:12px;padding:8px;border-radius:8px;background:#f9f9fb;color:#111;">
          <div id="score" style="font-weight:700;">Điểm: 0</div>
          <div id="warning" style="margin-top:4px;font-weight:600;"></div>
          <div id="details" style="margin-top:4px;color:#555;white-space:pre-wrap;"></div>
        </div>
      </div>
    `;

    document.documentElement.appendChild(container);

    const closeBtn = shadow.getElementById('ta-close');
    const analyzeBtn = shadow.getElementById('analyze-btn');
    const statusEl = shadow.getElementById('status');
    const resultArea = shadow.getElementById('result-area');
    const scoreEl = shadow.getElementById('score');
    const warningEl = shadow.getElementById('warning');
    const detailsEl = shadow.getElementById('details');
    const metaUrl = shadow.getElementById('meta-url');
    const metaTitle = shadow.getElementById('meta-title');

    closeBtn.addEventListener('click', () => {
      container.style.display = 'none';
    });

    function updateTabInfo() {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs && tabs[0];
        if (!tab) return;
        metaUrl.textContent = tab.url || 'Không có URL';
        metaTitle.textContent = tab.title || '';
      });
    }

    analyzeBtn.addEventListener('click', async () => {
      try {
        statusEl.textContent = 'Đang phân tích...';
        resultArea.style.display = 'none';
        const tabs = await new Promise(resolve => chrome.tabs.query({ active: true, currentWindow: true }, resolve));
        const tab = tabs && tabs[0];
        if (!tab || !tab.url) { statusEl.textContent = 'Không lấy được URL'; return; }
        const res = await fetch('http://localhost:8000/api/trust-analyzer/analyze/full', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: tab.url })
        });
        const data = await res.json();
        const score = Math.round((data.trust_score||0)*100);
        scoreEl.textContent = 'Điểm: ' + score + '/100';
        warningEl.textContent = score<50?'Cảnh báo: Lừa đảo!':score<75?'Cẩn thận':'An toàn';
        detailsEl.textContent = data.details||'';
        resultArea.style.display = 'block';
        statusEl.textContent = 'Hoàn tất';
      } catch(e) {
        console.error(e);
        statusEl.textContent = 'Lỗi: '+ (e.message||e);
      }
    });

    updateTabInfo();
    console.log('TA: sidebar hiện sẵn, header + nút X');
  } catch(e) {
    console.error('TA: content.js error', e);
  }
})();
