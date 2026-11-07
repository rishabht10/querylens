let history = [], chart = null;
const $ = id => document.getElementById(id);

async function ask() {
  const question = $("q").value.trim();
  if (!question) return;
  $("go").disabled = true;
  setStatus("Thinking…");
  try {
    const res = await fetch("/api/query", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question, history})
    });
    const d = await res.json();
    render(d);
    if (d.sql && !d.error) {
      history.push({role: "user", content: question}, {role: "assistant", content: d.sql});
    }
  } catch (e) { setStatus("Network error: " + e, true); }
  $("go").disabled = false;
}

function setStatus(msg, isErr) {
  $("status").textContent = msg;
  $("status").className = isErr ? "err" : "";
}

function render(d) {
  $("sql").hidden = !d.sql;
  $("sql").textContent = d.sql || "";
  if (d.error) { setStatus(d.error, true); $("tablebox").innerHTML = ""; drawChart(null); return; }
  setStatus(`${d.rows.length} row(s)`);
  drawTable(d.columns, d.rows);
  drawChart(d.chart, d.columns, d.rows);
}

function drawTable(cols, rows) {
  const t = document.createElement("table");
  const head = t.createTHead().insertRow();
  cols.forEach(c => { const th = document.createElement("th"); th.textContent = c; head.appendChild(th); });
  const body = t.createTBody();
  rows.forEach(r => {
    const tr = body.insertRow();
    r.forEach(v => { tr.insertCell().textContent = v === null ? "" : v; });
  });
  $("tablebox").replaceChildren(t);
}

function drawChart(spec, cols, rows) {
  if (chart) { chart.destroy(); chart = null; }
  $("chartbox").hidden = !spec;
  if (!spec) return;
  const data = spec.type === "line" ? rows : rows.slice(0, 30);
  let cfg;
  if (spec.type === "scatter") {
    const [xi, yi] = spec.value_indices;
    cfg = {type: "scatter", data: {datasets: [{label: `${cols[yi]} vs ${cols[xi]}`,
           data: data.map(r => ({x: r[xi], y: r[yi]}))}]}};
  } else {
    cfg = {type: spec.type, data: {
      labels: data.map(r => String(r[spec.label_index])),
      datasets: spec.value_indices.map(i => ({label: cols[i], data: data.map(r => r[i])}))}};
  }
  cfg.options = {responsive: true, plugins: {legend: {display: cfg.data.datasets.length > 1}}};
  chart = new Chart($("chart"), cfg);
}

$("go").onclick = ask;
$("q").addEventListener("keydown", e => { if (e.key === "Enter") ask(); });
$("clear").onclick = () => { history = []; $("q").value = ""; $("sql").hidden = true;
  $("tablebox").innerHTML = ""; drawChart(null); setStatus(""); };
