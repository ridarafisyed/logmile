import { useEffect, useId, useRef, useState } from "react";
import type { ChangeEvent, KeyboardEvent } from "react";

import { LOCATION_SEARCH_MIN_QUERY_LENGTH } from "../constants/location";
import {
  DETAIL_TEXT,
  FIELD_LABEL,
  INPUT_BASE,
  INPUT_INVALID,
  INPUT_LOCKED,
} from "../constants/ui";
import { useLocationSuggestions } from "../hooks/useLocationSuggestions";
import type {
  LocationFieldKey,
  LocationFieldMeta,
  LocationFieldValue,
  LocationOption,
} from "../types/trip";
import { cn } from "../utils/cn";
import { toLocationFieldValue } from "../utils/location";

export type LocationFieldName = LocationFieldKey;

interface LocationAutocompleteFieldProps {
  label: string;
  name: LocationFieldName;
  placeholder: string;
  value: LocationFieldValue;
  disabled?: boolean;
  error?: string;
  onChange: (name: LocationFieldName, value: LocationFieldValue) => void;
  onMetaChange?: (name: LocationFieldName, meta: LocationFieldMeta) => void;
}

export default function LocationAutocompleteField({
  label,
  name,
  placeholder,
  value,
  disabled = false,
  error,
  onChange,
  onMetaChange,
}: LocationAutocompleteFieldProps) {
  const listboxId = useId();
  const containerRef = useRef<HTMLLabelElement | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const trimmedText = value.text.trim();
  const hasExactSelection =
    value.selection !== null && value.selection.label === trimmedText;
  const shouldSearch =
    isOpen &&
    !hasExactSelection &&
    trimmedText.length >= LOCATION_SEARCH_MIN_QUERY_LENGTH;
  const {
    suggestions,
    loading,
    error: suggestionError,
    hasSearched,
  } = useLocationSuggestions(
    value.text,
    { enabled: shouldSearch },
  );
  const showMenu =
    shouldSearch &&
    (loading || hasSearched || suggestions.length > 0 || Boolean(suggestionError));

  useEffect(() => {
    onMetaChange?.(name, {
      hasSearched,
      suggestionCount: suggestions.length,
      suggestionError: Boolean(suggestionError),
    });
  }, [
    hasSearched,
    name,
    onMetaChange,
    suggestionError,
    suggestions.length,
  ]);

  useEffect(() => {
    if (!showMenu || suggestions.length === 0) {
      setHighlightedIndex(-1);
      return;
    }

    setHighlightedIndex(0);
  }, [showMenu, suggestions]);

  useEffect(() => {
    function handlePointerDown(event: MouseEvent) {
      if (
        containerRef.current &&
        event.target instanceof Node &&
        !containerRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
    };
  }, []);

  function handleInputChange(event: ChangeEvent<HTMLInputElement>) {
    const nextText = event.target.value;
    const nextSelection =
      value.selection && value.selection.label === nextText
        ? value.selection
        : null;

    onChange(name, toLocationFieldValue(nextText, nextSelection));
    setIsOpen(true);
  }

  function selectSuggestion(option: LocationOption) {
    onChange(name, toLocationFieldValue(option.label, option));
    setIsOpen(false);
    setHighlightedIndex(-1);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (!showMenu) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setHighlightedIndex((previousIndex) =>
        suggestions.length === 0
          ? -1
          : Math.min(previousIndex + 1, suggestions.length - 1),
      );
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setHighlightedIndex((previousIndex) =>
        suggestions.length === 0
          ? -1
          : Math.max(previousIndex - 1, 0),
      );
      return;
    }

    if (event.key === "Enter" && highlightedIndex >= 0) {
      event.preventDefault();
      selectSuggestion(suggestions[highlightedIndex]);
      return;
    }

    if (event.key === "Escape") {
      setIsOpen(false);
    }
  }

  return (
    <label className={FIELD_LABEL} ref={containerRef}>
      <span className="text-[0.94rem]">{label}</span>
      <div className="relative">
        <input
          aria-autocomplete="list"
          aria-controls={listboxId}
          aria-expanded={showMenu}
          aria-haspopup="listbox"
          aria-invalid={Boolean(error)}
          autoComplete="off"
          className={cn(
            INPUT_BASE,
            hasExactSelection && INPUT_LOCKED,
            error && INPUT_INVALID,
          )}
          disabled={disabled}
          name={name}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          role="combobox"
          value={value.text}
          required
        />

        {showMenu ? (
          <div className="absolute inset-x-0 top-[calc(100%+0.45rem)] z-20 overflow-hidden rounded-[1rem] border border-ink/10 bg-white/95 shadow-floating backdrop-blur-xl">
            <ul className="m-0 list-none p-1.5" id={listboxId} role="listbox">
              {loading ? (
                <li className={`${DETAIL_TEXT} px-3 py-3`}>
                  Looking up locations...
                </li>
              ) : null}

              {!loading && suggestionError ? (
                <li className="px-3 py-3 text-sm leading-6 text-red-700">
                  {suggestionError}
                </li>
              ) : null}

              {!loading && !suggestionError && suggestions.length === 0 ? (
                <li className={`${DETAIL_TEXT} px-3 py-3`}>
                  No matches found. You can still submit the typed location.
                </li>
              ) : null}

              {!loading &&
                !suggestionError &&
                suggestions.map((suggestion, index) => (
                  <li
                    aria-selected={index === highlightedIndex}
                    key={`${suggestion.label}-${index}`}
                    role="option"
                  >
                    <button
                      className={cn(
                        "grid w-full gap-1 rounded-[0.85rem] px-3 py-3 text-left text-ink transition",
                        index === highlightedIndex
                          ? "bg-teal-700/8"
                          : "hover:bg-teal-700/6",
                      )}
                      onMouseDown={(event) => event.preventDefault()}
                      onClick={() => selectSuggestion(suggestion)}
                      type="button"
                    >
                      <span className="text-sm font-semibold leading-6">
                        {suggestion.label}
                      </span>
                      <small className={DETAIL_TEXT}>{suggestion.query}</small>
                    </button>
                  </li>
                ))}
            </ul>
          </div>
        ) : null}
      </div>
      {error ? (
        <p className="text-sm font-medium leading-6 text-red-700">{error}</p>
      ) : null}
    </label>
  );
}
