import { readFileSync } from "node:fs";
import { describe, expect, test } from "bun:test";
import { Window } from "happy-dom";

const source = readFileSync("krisk/static/krisk-live.js", "utf8");

function makeWindow() {
  const window = new Window({ url: "http://127.0.0.1:8060/charts/example" });
  window.document.body.dataset.liveUrl = "/api/v1/charts/example/current";
  window.document.body.innerHTML = `
    <button id="static-tab" aria-selected="true">Snapshot</button>
    <button id="live-tab" aria-selected="false">Live</button>
    <section id="static-panel"></section>
    <section id="live-panel" hidden>
      <div id="live-chart"></div>
      <button id="refresh-live">Refresh</button>
      <p id="live-status"></p>
      <div id="claim-status"></div>
    </section>`;
  return window;
}

describe("living chart controls", () => {
  test("switches to live data, renders claims, and escapes server text", async () => {
    const window = makeWindow();
    let option;
    window.echarts = {
      init: () => ({
        resize: () => {},
        setOption: (value) => {
          option = value;
        },
      }),
    };
    window.fetch = async () => ({
      ok: true,
      json: async () => ({
        option: { series: [{ data: [1, 2] }] },
        refreshed_at: "2026-07-19T00:00:00Z",
        claims: [
          {
            status: "pass",
            label: "<img src=x onerror=alert(1)>",
            message: "still true",
          },
        ],
      }),
    });

    const runScript = new Function("window", "document", "fetch", "echarts", source);
    runScript(window, window.document, window.fetch, window.echarts);
    window.document.getElementById("live-tab").click();
    await window.happyDOM.waitUntilComplete();

    expect(window.document.getElementById("live-panel").hidden).toBe(false);
    expect(window.document.getElementById("static-panel").hidden).toBe(true);
    expect(option.series[0].data).toEqual([1, 2]);
    expect(window.document.getElementById("live-status").textContent).toContain("Current as of");
    expect(window.document.querySelector("#claim-status img")).toBeNull();
    expect(window.document.getElementById("claim-status").textContent).toContain(
      "<img src=x onerror=alert(1)>",
    );
  });
});
