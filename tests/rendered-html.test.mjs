import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
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
  assert.match(html, /GPT IMAGE 2 INCLUDED/);
  assert.match(html, /EVERY RENDERED SLIDE VERIFIED/);
  assert.match(html, /Overview/);
  assert.match(html, /Compare Styles/);
  assert.match(html, /Workflow/);
  assert.match(html, /Visual System/);
  assert.match(html, /Metrics/);
  assert.match(html, /Example/);
  assert.match(html, /Installation/);
  assert.match(html, /mikefilsaime-groove\/stickman-vsl-director/);
  assert.match(html, /mikefilsaime-groove\/mikefilsaime-skills/);
  assert.match(html, /nv7HuwnofW0/);
});

test("publishes the visual choices and frame-accurate render promise", async () => {
  const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(source, /Simple & Cute/);
  assert.match(source, /Full-Color & Expressive/);
  assert.match(source, /FRAME-ACCURATE CFR RENDERING/);
  assert.match(source, /Every approved storyboard slide must survive the final encode/);
  assert.match(source, /start, midpoint, and end samples for every slide/);
});

test("ships both complete storyboard comparisons", async () => {
  await Promise.all([
    access(new URL("../public/storyboards/simple-cute-01.webp", import.meta.url)),
    access(new URL("../public/storyboards/simple-cute-02.webp", import.meta.url)),
    access(new URL("../public/storyboards/full-color-expressive-01.webp", import.meta.url)),
    access(new URL("../public/storyboards/full-color-expressive-02.webp", import.meta.url)),
  ]);
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
