import { useEffect, useState } from "react";
import { checkBackendPing } from "./ping";

export type BackendPingState = "loading" | "ok" | "error";

export function useBackendPing(): { state: BackendPingState } {
  const [state, setState] = useState<BackendPingState>("loading");

  useEffect(() => {
    let cancelled = false;

    checkBackendPing()
      .then(() => {
        if (!cancelled) setState("ok");
      })
      .catch(() => {
        if (!cancelled) setState("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { state };
}
