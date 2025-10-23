if (!document.getElementById("tiki-sidebar-wrapper")) {
    const wrapper = document.createElement("div");
    wrapper.id = "tiki-sidebar-wrapper";
    wrapper.style.cssText = `
        display: flex;
        flex-direction: column;
        position: fixed;
        top: 0;
        right: 0;
        width: 420px;
        height: 100%;
        z-index: 999999;
        pointer-events: none; /* tránh click nhầm trước khi mở */
        transform: translateX(100%); /* bắt đầu ẩn ngoài màn hình */
        transition: transform 0.3s ease-in-out; /* hiệu ứng trượt */
        background: transparent;
    `;

    // Nút Close luôn hiện
    const closeBtn = document.createElement("button");
    closeBtn.id = "close-btn";
    closeBtn.innerText = "×";
    closeBtn.style.cssText = `

        width: 100%;
        text-align: right;
        font-size: 23px;
        border: none;
        cursor: pointer;
        background: #fff;
        z-index: 1000001;
    `;
    // Hover effect
    closeBtn.addEventListener("mouseenter", () => {
        closeBtn.style.color = "#0d17acff";
        
    });
    closeBtn.addEventListener("mouseleave", () => {
        closeBtn.style.color = "#000000ff";
        
    });
    closeBtn.addEventListener("click", () => {
        wrapper.style.transform = "translateX(100%)"; // trượt ra ngoài
        setTimeout(() => wrapper.remove(), 300);
    });

    // Iframe sidebar
    const iframe = document.createElement("iframe");
    iframe.id = "tiki-sidebar";
    iframe.src = chrome.runtime.getURL("sidebar.html");
    iframe.style.cssText = `
        width: 100%;
        height: 100%;
        border: none;
        box-shadow: -3px 0 10px rgba(0,0,0,0.2);
        pointer-events: all;
    `;

    wrapper.appendChild(closeBtn);
    wrapper.appendChild(iframe);
    document.body.appendChild(wrapper);

    // Gửi URL trang hiện tại vào iframe khi load xong
    iframe.onload = () => {
        iframe.contentWindow.postMessage({ action: "SET_PAGE_URL", url: window.location.href }, "*");

        // Mở wrapper mượt
        setTimeout(() => {
            wrapper.style.transform = "translateX(0)";
            wrapper.style.pointerEvents = "all";
        }, 50);
    };
}
