import { useState } from "react";

import { planTrip } from "./api/tripApi";
import EldLogSheet from "./components/EldLogSheet";
import MetricSummary from "./components/MetricSummary";
import RouteMap from "./components/RouteMap";
import TripForm from "./components/TripForm";
import TripSummaryPanel from "./components/TripSummaryPanel";
import EmptyPanel from "./components/common/EmptyPanel";
import ToastViewport from "./components/common/ToastViewport";
import { BODY_COPY, EYE_BROW } from "./constants/ui";
import { useToasts } from "./hooks/useToasts";
import type { TripFormValues, TripPlanResponse } from "./types/trip";
import { toTripPlanPayload } from "./utils/trip";

export default function App() {
  const [tripData, setTripData] = useState<TripPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const { toasts, pushToast, dismissToast } = useToasts();

  function handleValidationError(message: string) {
    pushToast({
      tone: "error",
      title: "Please fix the form",
      message,
    });
  }

  async function handlePlanTrip(formValues: TripFormValues) {
    setLoading(true);
    setPlanError(null);

    try {
      const data = await planTrip(toTripPlanPayload(formValues));
      setTripData(data);
      setPlanError(null);
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "Failed to plan trip.";
      setPlanError(message);
      pushToast({
        tone: "error",
        title: "Trip planning failed",
        message,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(217,119,6,0.18),transparent_28%),radial-gradient(circle_at_85%_10%,rgba(13,148,136,0.14),transparent_24%),linear-gradient(180deg,#f4efe7_0%,#f7f5f1_42%,#faf8f4_100%)]">
      <div className="pointer-events-none absolute left-[-12rem] top-[-10rem] h-[32rem] w-[32rem] rounded-full bg-amber-500/30 blur-[70px]" />
      <div className="pointer-events-none absolute right-[-12rem] top-48 h-[32rem] w-[32rem] rounded-full bg-teal-700/20 blur-[70px]" />
      <ToastViewport onDismiss={dismissToast} toasts={toasts} />

      <main className="relative z-10 mx-auto w-full max-w-[1240px] px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr] xl:items-start">
          <div className="pt-2 sm:pt-4 lg:pt-8">
            <span className={EYE_BROW}>LogMile</span>
            <h1 className="mt-4 max-w-[11ch] text-[clamp(2.8rem,5vw,4.8rem)] font-semibold leading-[0.96] tracking-[-0.05em] text-ink">
              Plan HOS-compliant routes with confidence.
            </h1>
            <p className={`${BODY_COPY} mt-5 max-w-[42rem]`}>
              Enter the driver’s current location, pickup, drop-off, cycle hours, 
              and start time. The planner calculates a legal trip schedule, adds 
              required break/rest stops, shows the route on the map, and generates 
              daily ELD log sheets.
            </p>
          </div>

          <TripForm
            loading={loading}
            onSubmit={handlePlanTrip}
            onValidationError={handleValidationError}
          />
        </section>

        <MetricSummary
          errorMessage={planError}
          loading={loading}
          summary={tripData?.hos_plan.summary}
        />

        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <RouteMap route={tripData?.route} stops={tripData?.hos_plan.stops || []} />
          <TripSummaryPanel hosPlan={tripData?.hos_plan} />
        </div>

        <section className="mt-7 grid gap-5">
          {tripData?.hos_plan.daily_logs.length ? (
            tripData.hos_plan.daily_logs.map((log) => (
              <EldLogSheet key={`${log.date}-${log.day}`} log={log} />
            ))
          ) : (
            <EmptyPanel
              description="Each trip day will render as a full 24-hour grid with duty-status lines, connectors, and remarks once the backend produces a legal schedule."
              eyebrow="ELD Logs"
              title="Daily log sheets appear here after the planner runs."
              variant="logs"
            />
          )}
        </section>
      </main>
    </div>
  );
}
