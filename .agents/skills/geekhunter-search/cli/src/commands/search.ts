import type { JobCard } from "../types";
import {
  fetchWithBackoff,
  parseSitemap,
  parseJobPage,
  matchesJobAge,
  matchesQuery,
  matchesRemote,
  writeError,
} from "../helpers";

const BASE_URL = "https://www.geekhunter.com.br";

export interface SearchOpts {
  query: string;
  limit: number;
  page: number;
  format: "json" | "table" | "plain";
  remote: boolean;
  jobage: number;
}

export async function runSearch(opts: SearchOpts): Promise<number> {
  try {
    const sitemapXml = await fetchWithBackoff(`${BASE_URL}/sitemap.xml`);
    if (!sitemapXml) {
      writeError("Failed to fetch sitemap", "SEARCH_FAILED");
      return 1;
    }

    const jobUrls = parseSitemap(sitemapXml);

    const jobs: JobCard[] = [];
    const batchSize = 5;

    for (let i = 0; i < jobUrls.length && jobs.length < opts.limit * 2; i += batchSize) {
      const batch = jobUrls.slice(i, i + batchSize);
      const results = await Promise.all(
        batch.map(async (url) => {
          const html = await fetchWithBackoff(url);
          if (!html) return null;
          return parseJobPage(html, url);
        })
      );

      for (const job of results) {
        if (!job) continue;
        if (!matchesQuery(job, opts.query)) continue;
        if (!matchesRemote(job, opts.remote)) continue;
        if (!matchesJobAge(job.date, opts.jobage)) continue;
        jobs.push(job);
        if (jobs.length >= opts.limit * 2) break;
      }

      if (i + batchSize < jobUrls.length && jobs.length < opts.limit) {
        await Bun.sleep(200);
      }
    }

    const total = jobs.length;
    const start = (opts.page - 1) * opts.limit;
    const paged = jobs.slice(start, start + opts.limit);

    const envelope = {
      meta: { count: paged.length, page: opts.page, total },
      results: paged,
    };

    switch (opts.format) {
      case "json":
        process.stdout.write(JSON.stringify(envelope, null, 2) + "\n");
        break;
      case "table":
        printTable(paged);
        break;
      case "plain":
        printPlain(paged);
        break;
    }

    return 0;
  } catch (err) {
    writeError(`Search failed: ${err}`, "SEARCH_FAILED");
    return 1;
  }
}

function printTable(jobs: JobCard[]): void {
  if (jobs.length === 0) {
    process.stdout.write("No jobs found.\n");
    return;
  }

  const idW = 40;
  const titleW = 45;
  const companyW = 20;
  const locationW = 25;
  const dateW = 15;

  const header =
    "ID".padEnd(idW) +
    "TITLE".padEnd(titleW) +
    "COMPANY".padEnd(companyW) +
    "LOCATION".padEnd(locationW) +
    "DATE".padEnd(dateW);

  process.stdout.write(header + "\n");
  process.stdout.write("-".repeat(header.length) + "\n");

  for (const job of jobs) {
    const row =
      truncate(job.id, idW).padEnd(idW) +
      truncate(job.title, titleW).padEnd(titleW) +
      truncate(job.company, companyW).padEnd(companyW) +
      truncate(job.location, locationW).padEnd(locationW) +
      truncate(job.date, dateW).padEnd(dateW);
    process.stdout.write(row + "\n");
  }
}

function printPlain(jobs: JobCard[]): void {
  if (jobs.length === 0) {
    process.stdout.write("No jobs found.\n");
    return;
  }

  for (const job of jobs) {
    process.stdout.write(`${job.title}\n`);
    process.stdout.write(`${job.company} | ${job.location} | ${job.date}\n`);
    if (job.salary) process.stdout.write(`Salary: ${job.salary}\n`);
    if (job.tags.length > 0) process.stdout.write(`Tags: ${job.tags.join(", ")}\n`);
    process.stdout.write(`ID: ${job.id}\n`);
    process.stdout.write(`URL: ${job.url}\n`);
    process.stdout.write("---\n");
  }
}

function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max - 3) + "..." : str;
}
