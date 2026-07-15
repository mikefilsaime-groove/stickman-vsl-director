import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("http://localhost/", {
      headers: { accept: "text/html", host: "stickman-vsl-director.example" },
    }),
    {
      ASSETS: {
        fetch: async () => new Response("Not found", { status: 404 }),
      },
    },
    {
      waitUntil() {},
      passThroughOnException() {},
    },
  );
}

test("server-renders the complete public portal", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Stickman VSL Director/);
  assert.match(html, /Turn any script into a/);
  assert.match(html, /timed visual storyboard/);
  assert.match(html, /GPT IMAGE 2 INCLUDED WITH YOUR CODEX SUBSCRIPTION/);
  assert.match(html, /Overview/);
  assert.match(html, /Workflow/);
  assert.match(html, /Visual System/);
  assert.match(html, /Metrics/);
  assert.match(html, /Example/);
  assert.match(html, /Installation/);
  assert.match(html, /mikefilsaime-groove\/stickman-vsl-director/);
  assert.match(html, /mikefilsaime-groove\/mikefilsaime-skills/);
  assert.match(html, /nv7HuwnofW0/);
});

test("removes the disposable starter experience", async () => {
  const response = await render();
  const html = await response.text();

  assert.doesNotMatch(html, /codex-preview/);
  assert.doesNotMatch(html, /Your site is taking shape/);
  assert.doesNotMatch(html, /react-loading-skeleton/);
  assert.doesNotMatch(html, /SkeletonPreview/);
  assert.match(html, /role="tablist"/);
  assert.match(html, /role="tabpanel"/);
  assert.match(html, /og\.png/);
});
