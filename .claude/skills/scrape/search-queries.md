# Search Queries for Job Scraper

## Search Sites

Primary:
- **linkedin.com/jobs** - LinkedIn job listings (global, filter by location)
- **freehire.dev** - global aggregator with ~50 ATS platforms (filter by country/region)

Secondary (company career pages via Google):
- Direct Google searches with `site:` filters for known target companies

## Query Categories

Queries are grouped by priority. Each query is combined with location terms where the portal supports it. For LinkedIn, use full location strings. For freehire, use `--country` or `--region` flags.

### Priority 1: Bioinformatics / Genomics (Brazil)

Strongest career direction in the local market.

```
"bioinformatics" São Paulo Brazil
"bioinformática" São Paulo Brasil
"genomics analyst" Brazil
"NGS analyst" Brazil
"next generation sequencing" São Paulo
"bioinformatics pipeline" Brazil
"bioinformatics engineer" Brazil
```

### Priority 2: Cloud / AWS in Life Sciences (Brazil)

Leverages AWS certification + domain expertise locally.

```
"AWS" bioinformatics Brazil
"cloud" genomics Brazil
"bioinformatics" "cloud engineer" Brazil
"solutions architect" life sciences Brazil
"data engineer" genomics São Paulo
"cloud infrastructure" bioinformatics Brazil
```

### Priority 3: Bioinformatics / Genomics (International Remote)

Remote-first international roles in the genomics/bioinformatics space.

```
"bioinformatics" remote
"genomics" "data engineer" remote
"bioinformatics engineer" remote
"NGS" "pipeline developer" remote
"precision medicine" data remote
"bioinformatics" "cloud" remote
```

### Priority 4: Cloud / AWS / Data Engineering (International Remote)

Remote international roles leveraging cloud + data skills.

```
"cloud solutions architect" remote
"AWS" "data engineer" remote
"bioinformatics" "AWS" remote
"cloud infrastructure" genomics remote
"data platform engineer" life sciences remote
"senior data engineer" remote
```

### Priority 5: Data Science in Healthcare/Genomics (Brazil + Remote)

Adjacent role combining data skills + domain knowledge.

```
"data scientist" genomics Brazil
"data scientist" healthcare São Paulo
"machine learning" bioinformatics Brazil
"data scientist" genomics remote
"precision medicine" "data scientist" remote
```

## Location Filter

When evaluating results, verify the job location meets criteria:
- **Brazil (preferred):** São Paulo capital and metro area, or fully remote within Brazil
- **International remote:** Fully remote roles that support Brazil timezones or are timezone-agnostic
- **Relocation:** International roles that explicitly offer relocation support
- **Excluded:** Roles requiring frequent travel, or on-site in cities without relocation support

## Date Filter

Only include jobs posted within the last 14 days, or with an application deadline that has not yet passed. If a posting date cannot be determined, include it but flag as "date unknown".

## Adapting Queries

If the user specifies a focus area, select queries from the matching category and also generate 2-3 custom queries for that focus. For example:
- "/scrape [focus_area]" -> relevant category queries + custom focus-specific queries
