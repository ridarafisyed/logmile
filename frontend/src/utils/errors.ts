export function formatApiError(errorPayload: unknown): string {
  if (typeof errorPayload === "string") {
    return errorPayload;
  }

  if (Array.isArray(errorPayload)) {
    return errorPayload.map(formatApiError).filter(Boolean).join(", ");
  }

  if (errorPayload && typeof errorPayload === "object") {
    return Object.entries(errorPayload)
      .map(([field, value]) => `${field}: ${formatApiError(value)}`)
      .filter(Boolean)
      .join(" | ");
  }

  return "";
}
