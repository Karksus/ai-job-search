---
name: geekhunter-search
version: 1.0.0
description: >
  Search live tech job listings from GeekHunter (Brazilian tech job board) via
  the public website. Scrapes the sitemap for job discovery and individual job
  pages for details. Supports keyword search, location filtering, and multiple
  output formats. Trigger phrases: find a tech job in Brazil, search GeekHunter,
  look up this GeekHunter posting, Brazilian developer jobs, remote tech jobs Brazil.
context: fork
allowed-tools: Bash(bun run .agents/skills/geekhunter-search/cli/src/cli.ts *)
---

# GeekHunter Search CLI

Search tech job listings from GeekHunter (geekhunter.com.br), a Brazilian tech-focused job board.

## Commands

### `search` — Search for jobs

```bash
bun run src/cli.ts search -q <query> [flags]
```

**Required flags:**
- `-q, --query <text>` — Search keyword (e.g., "python", "bioinformatics", "cloud engineer")

**Optional flags:**
- `-n, --limit <num>` — Max results to return (default: 25)
- `--page <num>` — Page number for pagination (default: 1)
- `--format <json|table|plain>` — Output format (default: table)
- `--remote` — Filter for remote jobs only
- `--jobage <days>` — Filter jobs posted within N days (default: 30)

**Examples:**
```bash
# Search for Python developer jobs
bun run src/cli.ts search -q python --format json

# Search for remote cloud engineer jobs
bun run src/cli.ts search -q "cloud engineer" --remote --limit 10

# Search for bioinformatics jobs posted in last 7 days
bun run src/cli.ts search -q bioinformatics --jobage 7 --format plain
```

### `detail` — Get job details

```bash
bun run src/cli.ts detail <job-slug-or-url> [--format json|plain]
```

**Examples:**
```bash
# Get job details by slug
bun run src/cli.ts detail ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1

# Get job details by full URL
bun run src/cli.ts detail https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1 --format json
```

## Output Formats

### JSON
```json
{
  "meta": { "count": 25, "page": 1, "total": 150 },
  "results": [
    {
      "id": "ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1",
      "title": "Engenheiro de Dados (Azure - Hibrido)",
      "company": "NTT Data",
      "location": "Sao Paulo, SP, Brasil",
      "date": "2 dias atras",
      "url": "https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1",
      "remote": false,
      "salary": null,
      "tags": ["Azure", "Python", "Apache Spark"]
    }
  ]
}
```

### Table
```
ID                                          TITLE                                    COMPANY     LOCATION              DATE
ntt-data/jobs/engenheiro...                 Engenheiro de Dados (Azure - Hibrido)    NTT Data    Sao Paulo, SP         2 dias atras
```

### Plain
```
Engenheiro de Dados (Azure - Hibrido)
NTT Data | Sao Paulo, SP, Brasil | 2 dias atras
ID: ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1
URL: https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1
---
```

## Error Handling

All errors are written to stderr as JSON:
```json
{"error": "Search failed: ...", "code": "SEARCH_FAILED"}
```

Exit codes:
- `0` — Success
- `1` — Error (see stderr JSON)

## Notes

- GeekHunter is a tech-focused job board (software engineers, data scientists, DevOps, etc.)
- No public API — uses sitemap-based discovery and HTML scraping
- Cloudflare protection may block aggressive scraping; the CLI respects rate limits
- Job URLs follow the pattern: `/{company-slug}/jobs/{job-slug}`
