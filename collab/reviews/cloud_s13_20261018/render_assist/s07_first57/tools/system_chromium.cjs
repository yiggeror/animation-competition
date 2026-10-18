// Local process configuration only; fixed-commit scene/renderer sources are untouched.
const { chromium } = require('playwright');
const launch = chromium.launch.bind(chromium);
chromium.launch = (options = {}) => launch({ ...options, executablePath: '/usr/bin/chromium' });
