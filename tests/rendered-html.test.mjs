import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the UNI-FLAGELLUM laboratory shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>UNI-FLAGELLUM/);
  assert.match(html, /UNI–FLAGELLUM/);
  assert.match(html, /World process/i);
  assert.match(html, /Markov boundary/i);
  assert.match(html, /Connect real instrument/);
  assert.match(html, /Physical UNI model/);
  assert.match(html, /Begin guided laboratory/);
  assert.match(html, /OBSERVED REPLAY/);
  assert.match(html, /STRUCTURAL RECONSTRUCTION/);
  assert.match(html, /UNI PHYSICAL ANALOGUE/);
  assert.match(html, /Export → re-import self-test/);
  assert.match(html, /mears-2014-run-tumble\.mp4/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/);
});
