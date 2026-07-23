# GeekHunter URL Reference

## Base URL

- Production: `https://www.geekhunter.com.br`

## Endpoints

### Sitemap (Job Discovery)

```
GET https://www.geekhunter.com.br/sitemap.xml
```

Returns XML sitemap with all job posting URLs. Jobs are listed under `<url>` entries with `<loc>` containing the full URL.

**Response:** XML document

**Example URLs from sitemap:**
```
https://www.geekhunter.com.br/ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1
https://www.geekhunter.com.br/code-group/jobs/analista-de-sistemas-pleno-senior-3
```

### Job Detail Page

```
GET https://www.geekhunter.com.br/{company-slug}/jobs/{job-slug}
```

Server-rendered HTML page with full job details.

**Response:** HTML document

**Extractable fields from HTML:**
- Job title (from `<h1>` or main heading)
- Company name
- Location
- Work model (Remote/Hybrid/On-site)
- Salary range (if listed)
- Job description
- Requirements
- Benefits
- Skills/technologies
- Publication date

## Search Parameters

The website uses client-side filtering on `/vagas`. Since there's no public API, we use the sitemap for job discovery and filter locally by:

1. **Keyword matching** — Match query against job titles and tags
2. **Recency** — Filter by publication date (via `--jobage` flag)
3. **Remote filter** — Match "Remoto" or "Remote" in work model

## HTML Parsing Notes

### Job Cards (from sitemap discovery)
Each job URL contains:
- Company slug (first path segment)
- Job slug (after `/jobs/`)

### Job Detail Page Structure
The HTML contains structured data that can be parsed with regex:
- Title: `<h1>` tag or class containing job title
- Company: Element with company name
- Location: Element with location info
- Description: Main content area with job requirements

## Rate Limiting

- Cloudflare manages rate limits
- Recommended: 1-2 requests per second
- The CLI implements exponential backoff on 429/5xx responses

## Authentication

- No authentication required for public job pages
- Candidate registration is free
- Some features may require login (job applications)

## Data Format

GeekHunter does not provide a JSON API. All data is extracted from:
1. **Sitemap XML** — Job URL discovery
2. **HTML pages** — Job details via regex parsing

The CLI converts this to the standard portal-skill JSON format for consistency with other job search tools.
