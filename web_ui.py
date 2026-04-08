"""Simple Flask web UI for the Network Port Scanner.

Start this with the project's venv Python. It provides a single-page web UI
that can start a scan and poll for results. This avoids Tk/macOS issues and
works in a browser on any OS.
"""
from flask import Flask, request, jsonify, render_template_string
import threading
import time
from scanner import PortScanner

app = Flask(__name__)

# Shared state for a single scan at a time
scan_lock = threading.Lock()
scanner = PortScanner()
scan_thread = None
scan_results = []
scan_start_time = None
scan_total = 0
scan_scanned = 0

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Network Port Scanner — Web UI</title>
  <style>
    body { font-family: Arial, sans-serif; background:#111; color:#ddd; }
    .card { max-width:900px; margin:24px auto; padding:16px; background:#1a1a1a; border-radius:8px }
    input, button { font-size:14px; padding:6px }
    pre { background:#000; color:#0f0; padding:12px; height:380px; overflow:auto }
  </style>
</head>
<body>
  <div class="card">
    <h2>Network Port Scanner — Web UI</h2>
    <div>
      Target: <input id="target" value="127.0.0.1"> &nbsp;
      Start: <input id="start" value="1" size="6"> &nbsp;
      End: <input id="end" value="1000" size="6"> &nbsp;
      Threads: <input id="threads" value="50" size="6"> &nbsp;
      <button id="startBtn">Start Scan</button>
      <button id="stopBtn">Stop</button>
    </div>

    <p id="status">Idle</p>
    <pre id="log">Ready.</pre>
  </div>

  <script>
    const log = document.getElementById('log');
    const status = document.getElementById('status');
    document.getElementById('startBtn').onclick = async () => {
      const target = document.getElementById('target').value;
      const start = document.getElementById('start').value;
      const end = document.getElementById('end').value;
      const threads = document.getElementById('threads').value;
      log.textContent = 'Starting scan...\n';
      const resp = await fetch('/start', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({target,start,end,threads})});
      const data = await resp.json();
      status.textContent = data.message;
    };

    document.getElementById('stopBtn').onclick = async () => {
      await fetch('/stop');
      status.textContent = 'Requested stop';
    };

    async function poll() {
      try {
        const r = await fetch('/status');
        const j = await r.json();
        status.textContent = j.scanning ? `Scanning — ${Math.round(j.progress*100)}%` : 'Idle';
        if (j.new_entries && j.new_entries.length) {
          for (const e of j.new_entries) { log.textContent += e + '\n'; }
        }
      } catch (err) {
        // ignore
      }
      setTimeout(poll, 700);
    }
    poll();
  </script>
</body>
</html>
"""


def make_scan_callback():
    # produce a callback that appends to scan_results and updates counters
    def cb(port, is_open, service, status):
        global scan_results, scan_scanned
        if port == -1:
            entry = f"{status}: {service}"
        else:
            entry = f"{port:5d} {'OPEN' if is_open else 'CLOSED':6s} ({service})"
            with scan_lock:
                scan_scanned += 1
        with scan_lock:
            scan_results.append(entry)

    return cb


def run_scan(target, start_p, end_p, threads):
    global scan_thread, scan_results, scan_start_time, scan_total, scan_scanned
    with scan_lock:
        scan_results = []
        scan_scanned = 0
        scan_total = end_p - start_p + 1
        scan_start_time = time.time()

    cb = make_scan_callback()
    scanner.scan_ports(target, start_p, end_p, cb, max_workers=threads)


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/start', methods=['POST'])
def start():
    global scan_thread
    data = request.get_json() or {}
    target = data.get('target', '127.0.0.1')
    start_p = int(data.get('start', 1))
    end_p = int(data.get('end', 1000))
    threads = int(data.get('threads', 50))

    if scan_thread and scan_thread.is_alive():
        return jsonify({'message': 'Scan already running'}), 400

    scan_thread = threading.Thread(target=run_scan, args=(target, start_p, end_p, threads), daemon=True)
    scan_thread.start()
    return jsonify({'message': f'Scan started: {target} {start_p}-{end_p} ({threads} threads)'}), 200


@app.route('/status')
def status():
    with scan_lock:
        entries = list(scan_results)
        scanned = scan_scanned
        total = scan_total

    scanning = scan_thread.is_alive() if scan_thread else False
    progress = (scanned / total) if total else 0

    # return only new entries since the last poll to keep payload small
    # For simplicity return all entries and let client append; acceptable for small scans.
    return jsonify({'scanning': scanning, 'progress': progress, 'new_entries': entries})


@app.route('/stop')
def stop():
    scanner.stop_scan()
    return jsonify({'message': 'stop requested'})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
