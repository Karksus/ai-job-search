import type { JobCard, JobDetail } from "./types";

export type { JobCard, JobDetail };

const USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

const BACKOFF_MS = 500;
const MAX_RETRIES = 6;
const MAX_BACKOFF_MS = 8000;

export async function fetchWithBackoff(url: string, retries = MAX_RETRIES): Promise<string> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        headers: {
          "User-Agent": USER_AGENT,
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
          "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        },
      });

      if (res.status === 404) return "";
      if (res.ok) return await res.text();

      if (res.status === 429 || res.status >= 500) {
        const delay = Math.min(BACKOFF_MS * 2 ** attempt + Math.random() * 200, MAX_BACKOFF_MS);
        await Bun.sleep(delay);
        continue;
      }

      return "";
    } catch {
      if (attempt < retries) {
        const delay = Math.min(BACKOFF_MS * 2 ** attempt + Math.random() * 200, MAX_BACKOFF_MS);
        await Bun.sleep(delay);
        continue;
      }
      return "";
    }
  }
  return "";
}

export async function fetchJson<T>(url: string, retries = MAX_RETRIES): Promise<T | null> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        headers: {
          "User-Agent": USER_AGENT,
          "Accept": "application/json",
        },
      });

      if (res.status === 404) return null;
      if (res.ok) return (await res.json()) as T;

      if (res.status === 429 || res.status >= 500) {
        const delay = Math.min(BACKOFF_MS * 2 ** attempt + Math.random() * 200, MAX_BACKOFF_MS);
        await Bun.sleep(delay);
        continue;
      }

      return null;
    } catch {
      if (attempt < retries) {
        const delay = Math.min(BACKOFF_MS * 2 ** attempt + Math.random() * 200, MAX_BACKOFF_MS);
        await Bun.sleep(delay);
        continue;
      }
      return null;
    }
  }
  return null;
}

export function parseSitemap(xml: string): string[] {
  const urls: string[] = [];
  const locRegex = /<loc>(https:\/\/www\.geekhunter\.com\.br\/[^<]+)<\/loc>/g;
  let match;
  while ((match = locRegex.exec(xml)) !== null) {
    const url = match[1];
    if (url.includes("/jobs/")) {
      urls.push(url);
    }
  }
  return urls;
}

export function parseJobPage(html: string, url: string): JobCard | null {
  try {
    const urlObj = new URL(url);
    const pathParts = urlObj.pathname.split("/").filter(Boolean);
    const companySlug = pathParts[0] || "";
    const jobSlug = pathParts.slice(2).join("/") || pathParts[1] || "";

    const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
    const title = titleMatch ? decodeHtmlEntities(titleMatch[1].trim()) : null;
    if (!title) return null;

    const company = decodeHtmlEntities(companySlug.replace(/-/g, " "));

    const locationMatch = html.match(/"location":\s*"([^"]+)"/i);
    const location = locationMatch ? decodeHtmlEntities(locationMatch[1]) : "";

    const dateMatch = html.match(/"publishedAt":\s*"([^"]+)"/i) ||
                      html.match(/"updatedAt":\s*"([^"]+)"/i);
    const date = dateMatch ? decodeHtmlEntities(dateMatch[1]) : "";

    const remoteMatch = html.match(/"remote":\s*(true|false)/i);
    const remote = remoteMatch ? remoteMatch[1] === "true" : /remoto|remote/i.test(html);

    const salaryMatch = html.match(/"salary":\s*"([^"]+)"/i);
    const salary = salaryMatch && salaryMatch[1] !== "A definir" ? salaryMatch[1] : null;

    const tagsRegex = /"skills":\s*\[([^\]]*)\]/i;
    const tagsMatch = tagsRegex.exec(html);
    const tags: string[] = [];
    if (tagsMatch) {
      const tagsStr = tagsMatch[1];
      const tagRegex = /"([^"]+)"/g;
      let tagMatch;
      while ((tagMatch = tagRegex.exec(tagsStr)) !== null) {
        tags.push(decodeHtmlEntities(tagMatch[1]));
      }
    }

    return {
      id: `${companySlug}/${jobSlug}`,
      title,
      company,
      location,
      date,
      url,
      remote,
      salary,
      tags,
    };
  } catch {
    return null;
  }
}

export function parseJobDetail(html: string, url: string): JobDetail | null {
  const card = parseJobPage(html, url);
  if (!card) return null;

  const descMatch = html.match(/"description":\s*"([^"]+(?:\\.[^"]*)*)"/i);
  let description = "";
  if (descMatch) {
    description = descMatch[1]
      .replace(/\\n/g, "\n")
      .replace(/\\t/g, "\t")
      .replace(/\\"/g, '"');
    description = decodeHtmlEntities(description);
  }

  const seniorityMatch = html.match(/"seniority":\s*"([^"]+)"/i);
  const seniority = seniorityMatch ? decodeHtmlEntities(seniorityMatch[1]) : "";

  const employmentMatch = html.match(/"contractType":\s*"([^"]+)"/i);
  const employmentType = employmentMatch ? decodeHtmlEntities(employmentMatch[1]) : "";

  return {
    ...card,
    description,
    seniority,
    employmentType,
    jobFunction: "",
    industries: [],
  };
}

function decodeHtmlEntities(str: string): string {
  return str
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(parseInt(code)));
}

function stripHtmlTags(html: string): string {
  return html
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function writeError(error: string, code: string): void {
  process.stderr.write(JSON.stringify({ error, code }) + "\n");
}

export function matchesJobAge(dateStr: string, maxDays: number): boolean {
  if (!dateStr) return true;

  const now = new Date();
  const lower = dateStr.toLowerCase();

  if (lower.includes("hora") || lower.includes("hour")) {
    const hours = parseInt(lower.match(/(\d+)/)?.[1] || "0");
    return hours <= maxDays * 24;
  }
  if (lower.includes("dia") || lower.includes("day")) {
    const days = parseInt(lower.match(/(\d+)/)?.[1] || "0");
    return days <= maxDays;
  }
  if (lower.includes("semana") || lower.includes("week")) {
    const weeks = parseInt(lower.match(/(\d+)/)?.[1] || "0");
    return weeks * 7 <= maxDays;
  }
  if (lower.includes("mes") || lower.includes("mês") || lower.includes("month")) {
    const months = parseInt(lower.match(/(\d+)/)?.[1] || "0");
    return months * 30 <= maxDays;
  }

  return true;
}

export function matchesQuery(job: JobCard, query: string): boolean {
  const q = query.toLowerCase();
  const searchable = `${job.title} ${job.company} ${job.tags.join(" ")}`.toLowerCase();
  return q.split(/\s+/).every(word => searchable.includes(word));
}

export function matchesRemote(job: JobCard, remoteFilter: boolean): boolean {
  if (!remoteFilter) return true;
  return job.remote || /remoto|remote/i.test(job.location);
}
