import { useDeferredValue, useEffect, useState } from "react";

import { searchLocations } from "../api/locationApi";
import {
  LOCATION_SEARCH_DEBOUNCE_MS,
  LOCATION_SEARCH_MIN_QUERY_LENGTH,
} from "../constants/location";
import type { LocationOption } from "../types/trip";

interface UseLocationSuggestionsOptions {
  enabled: boolean;
}

interface LocationSuggestionsState {
  suggestions: LocationOption[];
  loading: boolean;
  error: string;
  hasSearched: boolean;
}

const EMPTY_STATE: LocationSuggestionsState = {
  suggestions: [],
  loading: false,
  error: "",
  hasSearched: false,
};

export function useLocationSuggestions(
  query: string,
  { enabled }: UseLocationSuggestionsOptions,
): LocationSuggestionsState {
  const deferredQuery = useDeferredValue(query.trim());
  const [state, setState] = useState<LocationSuggestionsState>(EMPTY_STATE);

  useEffect(() => {
    if (
      !enabled ||
      deferredQuery.length < LOCATION_SEARCH_MIN_QUERY_LENGTH
    ) {
      setState(EMPTY_STATE);
      return undefined;
    }

    const controller = new AbortController();
    const timeoutId = window.setTimeout(async () => {
      setState((previousState) => ({
        ...previousState,
        loading: true,
        error: "",
      }));

      try {
        const suggestions = await searchLocations(
          deferredQuery,
          controller.signal,
        );
        setState({
          suggestions,
          loading: false,
          error: "",
          hasSearched: true,
        });
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setState({
          suggestions: [],
          loading: false,
          error:
            error instanceof Error
              ? error.message
              : "Failed to load location suggestions.",
          hasSearched: true,
        });
      }
    }, LOCATION_SEARCH_DEBOUNCE_MS);

    return () => {
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [deferredQuery, enabled]);

  return state;
}
