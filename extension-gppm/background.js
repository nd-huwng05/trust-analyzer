console.log('TA: background service worker starting');

async function tryToggleViaExecuteScript(tabId) {
  try {
    const res = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => {
        const c = document.getElementById('ta-sidebar-container');
        if (c) {
          c.dispatchEvent(new CustomEvent('ta-toggle-from-page'));
          return { toggled: true, reason: 'dispatched' };
        }
        return { toggled: false, reason: 'no-container' };
      }
    });
    return res && res[0] && res[0].result && res[0].result.toggled;
  } catch (e) {
    console.error('TA: executeScript dispatch failed', e);
    return false;
  }
}

async function injectContentScript(tabId) {
  try {
    console.log('TA: injecting content.js dynamically');
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ['content.js']
    });
    await new Promise(resolve => setTimeout(resolve, 250));
    return true;
  } catch (e) {
    console.error('TA: dynamic injection failed', e);
    return false;
  }
}

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab || !tab.id) return;
  console.log('TA: action clicked, tabId=', tab.id);

  let toggled = await tryToggleViaExecuteScript(tab.id);
  if (!toggled) {
    const injected = await injectContentScript(tab.id);
    if (injected) {
      toggled = await tryToggleViaExecuteScript(tab.id);
      console.log(toggled ? 'TA: toggled after injection' : 'TA: still cannot toggle');
    }
  } else {
    console.log('TA: toggled via executeScript directly');
  }
});
