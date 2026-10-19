// Render-environment adapter and logging only. Production modules stay unchanged.
const fs = require('fs');
const path = require('path');
const pw = require('playwright');
const out = __dirname;
const log = path.join(out, 'browser_resources.jsonl');
const summaryPath = path.join(out, 'browser_resource_summary.json');
fs.writeFileSync(log, '');
const summary = { source_commit: 'c3c63cc288807740114a4689af6ea18277a63794', cwd: process.cwd(), argv: process.argv.slice(1), started_utc: new Date().toISOString(), pages: 0, requests: 0, responses: 0, request_failures: [], page_errors: [], console_errors: [], response_status_counts: {}, chromium_runtime: null };
const record = data => fs.appendFileSync(log, JSON.stringify({ utc: new Date().toISOString(), ...data }) + '\n');
const launch = pw.chromium.launch.bind(pw.chromium);
pw.chromium.launch = async function(options = {}) {
  const runtime = options;
  summary.chromium_runtime = { effective_executable: options.executablePath, options, production_changes: false, launch_options_unchanged: true };
  record({ event: 'launch', ...summary.chromium_runtime });
  const browser = await launch(runtime);
  summary.chromium_version = browser.version();
  const newPage = browser.newPage.bind(browser);
  browser.newPage = async function(...args) {
    const page = await newPage(...args); const pageId = ++summary.pages;
    page.on('request', r => { summary.requests++; record({ event: 'request', page: pageId, method: r.method(), type: r.resourceType(), url: r.url() }); });
    page.on('response', r => { summary.responses++; const status = r.status(); summary.response_status_counts[status] = (summary.response_status_counts[status] || 0) + 1; record({ event: 'response', page: pageId, status, url: r.url() }); });
    page.on('requestfailed', r => { const e = { page: pageId, url: r.url(), failure: r.failure() }; summary.request_failures.push(e); record({ event: 'requestfailed', ...e }); });
    page.on('pageerror', e => { const v = { page: pageId, message: e.message }; summary.page_errors.push(v); record({ event: 'pageerror', ...v }); });
    page.on('console', m => { if (m.type() === 'error') { const v = { page: pageId, message: m.text(), location: m.location() }; summary.console_errors.push(v); record({ event: 'console_error', ...v }); } });
    return page;
  };
  return browser;
};
process.on('exit', code => { summary.process_exit_code = code; summary.finished_utc = new Date().toISOString(); fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2) + '\n'); });
