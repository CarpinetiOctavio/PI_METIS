import type { RouteObject } from "react-router-dom";
import { RootLayout } from "./components/RootLayout";
import { EntryPage } from "./routes/entry/EntryPage";
import { ConfigPage } from "./routes/config/ConfigPage";
import { StreamPage } from "./routes/stream/StreamPage";
import { ResultsPage } from "./routes/results/ResultsPage";
import { HistoryPage } from "./routes/history/HistoryPage";
import { HistoryDetailPage } from "./routes/history/HistoryDetailPage";
import { AuthVerifyPage } from "./routes/auth-verify/AuthVerifyPage";
import { ForgotPasswordPage } from "./routes/auth-recovery/ForgotPasswordPage";
import { ResetPasswordPage } from "./routes/auth-recovery/ResetPasswordPage";
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
      { path: "/auth/forgot-password", element: <ForgotPasswordPage /> },
      { path: "/auth/reset-password", element: <ResetPasswordPage /> },
    ],
  },
];
