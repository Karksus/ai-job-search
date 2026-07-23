import { describe, test, expect } from "bun:test";
import { runCLI, parseJSON } from "./helpers";

describe("CLI flag validation", () => {
  test("shows help when no args", async () => {
    const result = await runCLI([]);
    expect(result.exitCode).toBe(0);
    expect(result.stdout).toContain("Usage:");
  });

  test("search requires query flag", async () => {
    const result = await runCLI(["search"]);
    expect(result.exitCode).toBe(1);
    const err = parseJSON<{ error: string; code: string }>({ ...result, stdout: result.stderr });
    expect(err.code).toBe("NO_QUERY");
  });

  test("detail requires id argument", async () => {
    const result = await runCLI(["detail"]);
    expect(result.exitCode).toBe(1);
    const err = parseJSON<{ error: string; code: string }>({ ...result, stdout: result.stderr });
    expect(err.code).toBe("NO_ID");
  });

  test("rejects unknown command", async () => {
    const result = await runCLI(["unknown"]);
    expect(result.exitCode).toBe(1);
    const err = parseJSON<{ error: string; code: string }>({ ...result, stdout: result.stderr });
    expect(err.code).toBe("BAD_CMD");
  });

  test("rejects non-numeric limit", async () => {
    const result = await runCLI(["search", "-q", "python", "-n", "abc"]);
    expect(result.exitCode).toBe(1);
    const err = parseJSON<{ error: string; code: string }>({ ...result, stdout: result.stderr });
    expect(err.code).toBe("BAD_ARG");
  });

  test("rejects non-numeric jobage", async () => {
    const result = await runCLI(["search", "-q", "python", "--jobage", "abc"]);
    expect(result.exitCode).toBe(1);
    const err = parseJSON<{ error: string; code: string }>({ ...result, stdout: result.stderr });
    expect(err.code).toBe("BAD_ARG");
  });
});
