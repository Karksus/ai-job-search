import { describe, test, expect, mock, beforeEach } from "bun:test";
import { runSearch } from "../src/commands/search";
import { runDetail } from "../src/commands/detail";

const mockSitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1</loc>
  </url>
  <url>
    <loc>https://www.geekhunter.com.br/code-group/jobs/analista-de-sistemas-pleno-senior-3</loc>
  </url>
</urlset>`;

const mockJobHtml = `<html>
<head><title>Engenheiro de Dados</title></head>
<body>
  <h1>Engenheiro de Dados (Azure - Hibrido)</h1>
  <span>NTT Data</span>
  <div class="location">São Paulo, SP, Brasil</div>
  <div class="date">Atualizada há 2 dias</div>
  <div class="tag">Azure</div>
  <div class="tag">Python</div>
</body>
</html>`;

const originalFetch = globalThis.fetch;

beforeEach(() => {
  globalThis.fetch = mock(() =>
    Promise.resolve(new Response("", { status: 404 }))
  ) as typeof fetch;
});

describe("runSearch", () => {
  test.skip("returns error on fetch failure", async () => {
    globalThis.fetch = mock(() =>
      Promise.resolve(new Response("", { status: 500 }))
    ) as typeof fetch;

    const opts = {
      query: "python",
      limit: 10,
      page: 1,
      format: "json" as const,
      remote: false,
      jobage: 30,
    };

    const result = await runSearch(opts);
    expect(result).toBe(1);
  });
});

describe("runDetail", () => {
  test.skip("returns error on 404", async () => {
    globalThis.fetch = mock(() =>
      Promise.resolve(new Response("", { status: 404 }))
    ) as typeof fetch;

    const opts = {
      id: "ntt-data/jobs/nonexistent",
      format: "json" as const,
    };

    const result = await runDetail(opts);
    expect(result).toBe(1);
  });
});
