const files = ["summary", "models", "capabilities", "evolution", "system"];
const money = value => value === null || value === undefined ? "Unknown" : `$${Number(value).toFixed(4)}`;
const text = (id, value) => { document.getElementById(id).textContent = value; };

function table(headers, rows) {
  const root = document.createElement("table");
  const head = root.createTHead().insertRow();
  headers.forEach(label => { const cell = document.createElement("th"); cell.textContent = label; head.append(cell); });
  const body = root.createTBody();
  rows.forEach(row => {
    const line = body.insertRow();
    row.forEach(value => { const cell = line.insertCell(); cell.textContent = value; });
  });
  return root;
}

function renderCosts(summary) {
  const costs = summary.cost_usd || {};
  const entries = ["build", "evaluation", "execution"].map(name => [name, Number(costs[name] || 0)]);
  const maximum = Math.max(...entries.map(([, value]) => value), 0.000001);
  const root = document.getElementById("cost-bars");
  entries.forEach(([name, value]) => {
    const row = document.createElement("div"); row.className = "bar-row";
    const label = document.createElement("span"); label.textContent = name.toUpperCase();
    const track = document.createElement("div"); track.className = "bar-track";
    const fill = document.createElement("div"); fill.className = "bar-fill"; fill.style.width = `${100 * value / maximum}%`; track.append(fill);
    const amount = document.createElement("span"); amount.className = "bar-value"; amount.textContent = money(value);
    row.append(label, track, amount); root.append(row);
  });
}

function render(data) {
  const summary = data.summary;
  text("total-cost", money(summary.total_known_cost_usd));
  text("execution-cost", money(summary.cost_usd?.execution));
  text("build-cost", money(summary.cost_usd?.build));
  text("capability-count", summary.installed_capabilities ?? 0);
  text("task-count", summary.completed_tasks ?? 0);
  text("unknown-cost", summary.unknown_cost_events ?? 0);
  text("freshness", `Last reported: ${new Date(summary.generated_at).toLocaleString()}`);
  renderCosts(summary);

  const modelRows = (data.models.models || []).map(item => [item.provider, item.model, item.requests, money(item.cost_usd), item.input_tokens, item.output_tokens]);
  document.getElementById("models").append(table(["Provider", "Model", "Calls", "Cost", "Input", "Output"], modelRows));
  const capabilityRows = (data.capabilities.capabilities || []).map(item => [item.id, item.version, item.invocations, item.successes, item.failures]);
  document.getElementById("capabilities").append(table(["Capability", "Version", "Runs", "Success", "Failure"], capabilityRows));

  const events = data.evolution.events || [];
  document.getElementById("events-empty").hidden = events.length > 0;
  events.forEach(event => {
    const item = document.createElement("li");
    const time = document.createElement("time"); time.textContent = new Date(event.timestamp).toLocaleString();
    const type = document.createElement("span"); type.textContent = event.type.replaceAll("_", " ");
    const capability = document.createElement("small"); capability.textContent = event.capability_id ? `${event.capability_id}@${event.capability_version}` : "";
    item.append(time, type, capability); document.getElementById("events").append(item);
  });

  const samples = data.system.samples || [];
  document.getElementById("system-empty").hidden = samples.length > 0;
  if (samples.length) {
    const latest = samples.at(-1);
    Object.entries(latest).forEach(([label, value]) => {
      const wrapper = document.createElement("div");
      const term = document.createElement("dt"); term.textContent = label.replaceAll("_", " ");
      const detail = document.createElement("dd"); detail.textContent = value;
      wrapper.append(term, detail); document.getElementById("system").append(wrapper);
    });
  }

  const age = Date.now() - new Date(summary.generated_at).getTime();
  const stale = age > 20 * 60 * 1000;
  document.getElementById("status-dot").className = stale ? "stale" : "ok";
  text("status-text", stale ? "Telemetry stale" : "Telemetry current");
}

Promise.all(files.map(async name => {
  const response = await fetch(`data/${name}.json`, { cache: "no-store" });
  if (!response.ok) throw new Error(`Unable to load ${name}`);
  return [name, await response.json()];
})).then(entries => render(Object.fromEntries(entries))).catch(() => {
  document.getElementById("status-dot").className = "stale";
  text("status-text", "Telemetry unavailable");
});
