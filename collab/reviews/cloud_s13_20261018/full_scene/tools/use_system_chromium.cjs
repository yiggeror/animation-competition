// Process-local launch configuration. Repository frames.cjs/rendering files are unchanged.
const { chromium } = require('playwright');
const launch = chromium.launch.bind(chromium);
chromium.launch = (options = {}) => launch({ ...options, executablePath: process.env.S13_CHROMIUM || '/usr/bin/chromium' });
