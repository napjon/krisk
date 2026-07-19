(() => {
  "use strict";
  const body = document.body;
  const liveUrl = body?.dataset.liveUrl;
  const staticTab = document.getElementById("static-tab");
  const liveTab = document.getElementById("live-tab");
  const staticPanel = document.getElementById("static-panel");
  const livePanel = document.getElementById("live-panel");
  const status = document.getElementById("live-status");
  const claims = document.getElementById("claim-status");
  let chart;

  function select(mode) {
    const live = mode === "live";
    staticTab?.setAttribute("aria-selected", String(!live));
    liveTab?.setAttribute("aria-selected", String(live));
    if (staticPanel) staticPanel.hidden = live;
    if (livePanel) livePanel.hidden = !live;
    if (live) refresh();
  }

  async function refresh() {
    if (!liveUrl || !status) return;
    status.textContent = "Loading current data…";
    try {
      const response = await fetch(liveUrl, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`Server returned ${response.status}`);
      const payload = await response.json();
      const element = document.getElementById("live-chart");
      if (!element || typeof echarts === "undefined") throw new Error("Chart renderer unavailable");
      chart ||= echarts.init(element);
      chart.setOption(payload.option, true);
      chart.resize();
      status.textContent = `Current as of ${payload.refreshed_at}`;
      if (claims && payload.claims) {
        claims.innerHTML = payload.claims.map((claim) =>
          `<p><strong>${escapeHtml(claim.status.toUpperCase())}</strong> — ${escapeHtml(claim.label)}: ${escapeHtml(claim.message)}</p>`
        ).join("");
      }
    } catch (error) {
      status.textContent = `Live data unavailable. The saved snapshot is unchanged. ${error.message}`;
    }
  }

  function escapeHtml(value) {
    const node = document.createElement("span");
    node.textContent = String(value ?? "");
    return node.innerHTML;
  }

  staticTab?.addEventListener("click", () => select("static"));
  liveTab?.addEventListener("click", () => select("live"));
  document.getElementById("refresh-live")?.addEventListener("click", refresh);
  window.addEventListener("resize", () => chart?.resize());
})();
