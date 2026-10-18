// Existing system-Chromium configuration, plus read-only resource observations.
require('../use_system_chromium.cjs');
const { chromium } = require('playwright');
const launch = chromium.launch.bind(chromium);
chromium.launch = async (options) => {
  const browser = await launch(options);
  const newPage = browser.newPage.bind(browser);
  browser.newPage = async (options) => {
    const page = await newPage(options);
    page.on('response', (r) => {
      if (r.status() >= 400 || /\.(png|jpe?g|webp)(\?|$)/i.test(r.url()))
        console.log(`[resource ${r.status()}] ${r.url()}`);
    });
    page.on('requestfailed', (r) => console.log(`[requestfailed] ${r.url()} ${r.failure()?.errorText}`));
    return page;
  };
  return browser;
};
