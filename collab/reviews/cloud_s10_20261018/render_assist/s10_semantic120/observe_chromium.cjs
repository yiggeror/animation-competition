// Existing system Chromium configuration; log actual server responses, including favicon.
require('../use_system_chromium.cjs');
const http = require('http');
const emit = http.Server.prototype.emit;
http.Server.prototype.emit = function(event, ...args) {
  if (event === 'request') {
    const [req, res] = args;
    res.on('finish', () => console.log('[server-response] ' + JSON.stringify({path:req.url,status:res.statusCode})));
  }
  return emit.call(this, event, ...args);
};
