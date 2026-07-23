import type { JobDetail } from "../types";
import { fetchWithBackoff, parseJobDetail, writeError } from "../helpers";

const BASE_URL = "https://www.geekhunter.com.br";

export interface DetailOpts {
  id: string;
  format: "json" | "plain";
}

export async function runDetail(opts: DetailOpts): Promise<number> {
  try {
    let url = opts.id;

    if (!url.startsWith("http")) {
      if (url.startsWith("/")) {
        url = BASE_URL + url;
      } else {
        url = `${BASE_URL}/${url}`;
      }
    }

    const html = await fetchWithBackoff(url);
    if (!html) {
      writeError(`Job not found: ${opts.id}`, "DETAIL_FAILED");
      return 1;
    }

    const job = parseJobDetail(html, url);
    if (!job) {
      writeError(`Failed to parse job: ${opts.id}`, "DETAIL_FAILED");
      return 1;
    }

    switch (opts.format) {
      case "json":
        process.stdout.write(JSON.stringify(job, null, 2) + "\n");
        break;
      case "plain":
        printPlain(job);
        break;
    }

    return 0;
  } catch (err) {
    writeError(`Detail failed: ${err}`, "DETAIL_FAILED");
    return 1;
  }
}

function printPlain(job: JobDetail): void {
  process.stdout.write(`${job.title}\n`);
  process.stdout.write(`${job.company}\n`);
  process.stdout.write(`Location: ${job.location}\n`);
  if (job.remote) process.stdout.write(`Remote: Yes\n`);
  if (job.salary) process.stdout.write(`Salary: ${job.salary}\n`);
  if (job.seniority) process.stdout.write(`Seniority: ${job.seniority}\n`);
  if (job.employmentType) process.stdout.write(`Type: ${job.employmentType}\n`);
  if (job.tags.length > 0) process.stdout.write(`Tags: ${job.tags.join(", ")}\n`);
  process.stdout.write(`\n${job.description}\n`);
  process.stdout.write(`\nURL: ${job.url}\n`);
  process.stdout.write(`ID: ${job.id}\n`);
}
