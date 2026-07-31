import type { RouteObject } from "react-router-dom";
import { RootLayout } from "./components/RootLayout";
import { EntryPage } from "./routes/entry/EntryPage";
import { ConfigPage } from "./routes/config/ConfigPage";
import { StreamPage } from "./routes/stream/StreamPage";
import { ResultsPage } from "./routes/results/ResultsPage";
import { RankingPage } from "./routes/ranking/RankingPage";
import { DesignEventsPage } from "./routes/design-events/DesignEventsPage";
import { HistoryPage } from "./routes/history/HistoryPage";
import { HistoryDetailPage } from "./routes/history/HistoryDetailPage";
import { AuthVerifyPage } from "./routes/auth-verify/AuthVerifyPage";
import { RedirectIfAuthed, RequireAuth, RequireSession } from "./auth/guards";

export const routes: RouteObject[] = [
  {
    element: <RootLayout />,
    children: [
      {
        path: "/",
        element: (
          <RedirectIfAuthed>
            <EntryPage />
          </RedirectIfAuthed>
        ),
      },
      {
        path: "/config",
        element: (
          <RequireSession>
            <ConfigPage />
          </RequireSession>
        ),
      },
      {
        path: "/stream",
        element: (
          <RequireSession>
            <StreamPage />
          </RequireSession>
        ),
      },
      {
        path: "/results",
        element: (
          <RequireSession>
            <ResultsPage />
          </RequireSession>
        ),
      },
      {
        path: "/ranking",
        element: (
          <RequireSession>
            <RankingPage />
          </RequireSession>
        ),
      },
      {
        path: "/design-events",
        element: (
          <RequireSession>
            <DesignEventsPage />
          </RequireSession>
        ),
      },
      {
        path: "/history",
        element: (
          <RequireAuth>
            <HistoryPage />
          </RequireAuth>
        ),
      },
      {
        path: "/history/:id",
        element: (
          <RequireAuth>
            <HistoryDetailPage />
          </RequireAuth>
        ),
      },
      { path: "/auth/verify", element: <AuthVerifyPage /> },
    ],
  },
];
