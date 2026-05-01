export async function readJsonResponse<T>(
  response: Response,
): Promise<T | null> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    return null;
  }

  try {
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export function toRequestError(
  error: unknown,
  fallbackMessage: string,
): Error {
  if (error instanceof DOMException && error.name === "AbortError") {
    return error;
  }

  if (error instanceof TypeError) {
    return new Error(
      "Cannot reach the backend right now. If you are running locally, make sure Docker or the Django server is up and the frontend proxy can reach `/api`.",
    );
  }

  if (error instanceof Error) {
    return error;
  }

  return new Error(fallbackMessage);
}
