#!/usr/bin/env bun

import { runSearch, type SearchOpts } from "./commands/search";
import { runDetail, type DetailOpts } from "./commands/detail";
import { writeError } from "./helpers";

interface Flags {
  _: string[];
  [k: string]: string | boolean | string[];
}

function parseFlags(args: string[]): Flags {
  const flags: Flags = { _: [] };
  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    if (arg === "--") {
      flags._.push(...args.slice(i + 1));
      break;
    }
    if (arg === "-q" || arg === "--query") {
      flags.query = args[++i] ?? "";
    } else if (arg === "-n" || arg === "--limit") {
      flags.limit = args[++i] ?? "25";
    } else if (arg === "--page") {
      flags.page = args[++i] ?? "1";
    } else if (arg === "--format") {
      flags.format = args[++i] ?? "table";
    } else if (arg === "--remote") {
      flags.remote = args[i + 1] && !args[i + 1].startsWith("-") ? args[++i] : "remote";
    } else if (arg === "--jobage") {
      flags.jobage = args[++i] ?? "30";
    } else if (arg.startsWith("-")) {
      const key = arg.replace(/^-{1,2}/, "");
      flags[key] = args[++i] ?? "";
    } else {
      flags._.push(arg);
    }
    i++;
  }
  return flags;
}

const HELP = `
Usage: geekhunter-search <command> [flags]

Commands:
  search    Search for jobs
  detail    Get job details

Flags:
  -q, --query <text>     Search keyword (required for search)
  -n, --limit <num>      Max results (default: 25)
  --page <num>           Page number (default: 1)
  --format <fmt>         Output format: json, table, plain (default: table)
  --remote               Filter for remote jobs
  --jobage <days>        Filter jobs posted within N days (default: 30)

Examples:
  geekhunter-search search -q python --format json
  geekhunter-search search -q "cloud engineer" --remote --limit 10
  geekhunter-search detail ntt-data/jobs/engenheiro-de-dados--azure--hibrido---1
`.trim();

function stderrError(error: string, code: string): number {
  writeError(error, code);
  return 1;
}

async function main(): Promise<number> {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    process.stdout.write(HELP + "\n");
    return 0;
  }

  const flags = parseFlags(args);
  const cmd = flags._[0];

  if (cmd === "search") {
    const query = typeof flags.query === "string" ? flags.query : "";
    if (!query) {
      return stderrError("Missing required flag: -q/--query", "NO_QUERY");
    }

    const opts: SearchOpts = {
      query,
      limit: parseInt(typeof flags.limit === "string" ? flags.limit : "25", 10),
      page: parseInt(typeof flags.page === "string" ? flags.page : "1", 10),
      format: (typeof flags.format === "string" ? flags.format : "table") as SearchOpts["format"],
      remote: flags.remote !== undefined && flags.remote !== "false",
      jobage: parseInt(typeof flags.jobage === "string" ? flags.jobage : "30", 10),
    };

    if (isNaN(opts.limit) || opts.limit < 1) {
      return stderrError("Invalid limit: must be a positive integer", "BAD_ARG");
    }
    if (isNaN(opts.page) || opts.page < 1) {
      return stderrError("Invalid page: must be a positive integer", "BAD_ARG");
    }
    if (isNaN(opts.jobage) || opts.jobage < 1) {
      return stderrError("Invalid jobage: must be a positive integer", "BAD_ARG");
    }

    return runSearch(opts);
  }

  if (cmd === "detail") {
    const id = flags._[1];
    if (!id) {
      return stderrError("Missing required argument: job slug or URL", "NO_ID");
    }

    const opts: DetailOpts = {
      id,
      format: (typeof flags.format === "string" ? flags.format : "plain") as DetailOpts["format"],
    };

    return runDetail(opts);
  }

  return stderrError(`Unknown command: ${cmd}`, "BAD_CMD");
}

main().then((code) => process.exit(code));
