export interface CLIResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runCLI(args: string[], env?: Record<string, string>): Promise<CLIResult> {
  const proc = Bun.spawn(
    ["bun", "run", "src/cli.ts", ...args],
    {
      cwd: import.meta.dir + "/..",
      stdout: "pipe",
      stderr: "pipe",
      env: { ...process.env, ...env },
    }
  );

  const stdout = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  const exitCode = await proc.exited;

  return { stdout, stderr, exitCode };
}

export function parseJSON<T>(result: CLIResult): T {
  return JSON.parse(result.stdout) as T;
}
