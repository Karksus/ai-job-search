# GeekHunter Search CLI

Search tech job listings from [GeekHunter](https://www.geekhunter.com.br), a Brazilian tech-focused job board.

## Setup

```bash
bun install
```

## Usage

### Search for jobs

```bash
# Search for Python developer jobs
bun run src/cli.ts search -q python --format json

# Search for remote cloud engineer jobs
bun run src/cli.ts search -q "cloud engineer" --remote --limit 10

# Search for bioinformatics jobs posted in last 7 days
bun run src/cli.ts search -q bioinformatics --jobage 7 --format plain
```

### Get job details

```bash
# Get job details by slug
bun run src/cli.ts detail ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1

# Get job details by full URL
bun run src/cli.ts detail https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1 --format json
```

## Output Formats

- `json` — Full JSON with metadata
- `table` — Fixed-width table
- `plain` — Human-readable blocks

## How It Works

1. Fetches the GeekHunter sitemap to discover job URLs
2. Fetches individual job pages and parses the HTML
3. Filters results by query, recency, and remote status
4. Returns results in the standard portal-skill format

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
