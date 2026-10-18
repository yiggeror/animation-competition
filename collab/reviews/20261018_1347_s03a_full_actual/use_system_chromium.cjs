// Renderer compatibility shim only. Shot module and frame renderer stay unchanged.
// Global Playwright is installed; its bundled browser is not. Use installed Chromium.
const { chromium } = require('playwright');
const originalLaunch = chromium.launch.bind(chromium);
chromium.launch = (options = {}) => originalLaunch({ ...options, executablePath: '/usr/bin/chromium' });
