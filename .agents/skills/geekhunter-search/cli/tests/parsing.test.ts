import { describe, test, expect } from "bun:test";
import { parseSitemap, parseJobPage, matchesJobAge, matchesQuery } from "../src/helpers";

describe("parseSitemap", () => {
  test("extracts job URLs from sitemap XML", () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1</loc>
    <lastmod>2026-07-21</lastmod>
  </url>
  <url>
    <loc>https://www.geekhunter.com.br/about</loc>
  </url>
  <url>
    <loc>https://www.geekhunter.com.br/code-group/jobs/analista-de-sistemas-pleno-senior-3</loc>
    <lastmod>2026-07-20</lastmod>
  </url>
</urlset>`;

    const urls = parseSitemap(xml);
    expect(urls).toHaveLength(2);
    expect(urls[0]).toContain("engenheiro-de-dados");
    expect(urls[1]).toContain("analista-de-sistemas");
  });

  test("returns empty array for no job URLs", () => {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.geekhunter.com.br/about</loc>
  </url>
</urlset>`;

    const urls = parseSitemap(xml);
    expect(urls).toHaveLength(0);
  });
});

describe("parseJobPage", () => {
  test("extracts job info from HTML", () => {
    const html = `<html>
<head><title>Engenheiro de Dados</title></head>
<body>
  <h1>Engenheiro de Dados (Azure - Hibrido)</h1>
  <script type="application/json">
    {"location": "São Paulo, SP, Brasil", "publishedAt": "Atualizada há 2 dias", "skills": ["Azure", "Python"]}
  </script>
</body>
</html>`;

    const url = "https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1";
    const job = parseJobPage(html, url);

    expect(job).not.toBeNull();
    expect(job!.title).toBe("Engenheiro de Dados (Azure - Hibrido)");
    expect(job!.company).toBe("ntt data");
    expect(job!.location).toBe("São Paulo, SP, Brasil");
    expect(job!.date).toBe("Atualizada há 2 dias");
    expect(job!.tags).toContain("Azure");
    expect(job!.tags).toContain("Python");
  });

  test("returns null for missing title", () => {
    const html = "<html><body><p>No title here</p></body></html>";
    const job = parseJobPage(html, "https://example.com/test");
    expect(job).toBeNull();
  });
});

describe("matchesJobAge", () => {
  test("matches recent jobs", () => {
    expect(matchesJobAge("há 2 horas", 7)).toBe(true);
    expect(matchesJobAge("há 3 dias", 7)).toBe(true);
    expect(matchesJobAge("há 2 semanas", 30)).toBe(true);
  });

  test("rejects old jobs", () => {
    expect(matchesJobAge("há 3 meses", 7)).toBe(false);
    expect(matchesJobAge("há 10 dias", 7)).toBe(false);
  });

  test("passes through empty dates", () => {
    expect(matchesJobAge("", 7)).toBe(true);
  });
});

describe("matchesQuery", () => {
  const job = {
    id: "test",
    title: "Engenheiro de Dados",
    company: "NTT Data",
    location: "São Paulo",
    date: "2 dias",
    url: "https://example.com",
    remote: false,
    salary: null,
    tags: ["Azure", "Python"],
  };

  test("matches title", () => {
    expect(matchesQuery(job, "engenheiro")).toBe(true);
  });

  test("matches company", () => {
    expect(matchesQuery(job, "ntt")).toBe(true);
  });

  test("matches tags", () => {
    expect(matchesQuery(job, "azure")).toBe(true);
  });

  test("matches multiple words", () => {
    expect(matchesQuery(job, "engenheiro dados")).toBe(true);
  });

  test("rejects non-matching", () => {
    expect(matchesQuery(job, "bioinformatics")).toBe(false);
  });
});
