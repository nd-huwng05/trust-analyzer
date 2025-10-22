// sidebar.js (inside shadow) - add startup log and expose toggle event handler
(function () {
  try {
    console.log('TA(Sidebar): script executed inside shadow root');
    const root = document.currentScript && document.currentScript.getRootNode ? document.currentScript.getRootNode() : document;
    const taRoot = root.getElementById('ta-root');

    if (!taRoot) {
      console.warn('TA(Sidebar): #ta-root not found');
      return;
    }

    const handle = root.querySelector('#ta-handle');
    const closeBtn = root.querySelector('.close-x');
    let isOpen = false;

    function setOpen(open) {
      isOpen = !!open;
      if (isOpen) taRoot.classList.add('open'); else taRoot.classList.remove('open');
    }

    function toggle() {
      setOpen(!isOpen);
      console.log('TA(Sidebar): toggled ->', isOpen);
    }

    handle && handle.addEventListener('click', toggle);
    closeBtn && closeBtn.addEventListener('click', toggle);

    // listen to dispatched events from content.js
    const host = (root && root.host) || document;
    host.addEventListener && host.addEventListener('ta-toggle-from-page', () => {
      console.log('TA(Sidebar): received ta-toggle-from-page');
      toggle();
    });

    console.log('TA(Sidebar): ready (open state =', isOpen, ')');
  } catch (err) {
    console.error('TA(Sidebar): unexpected error', err);
  }
})();