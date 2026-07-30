import { Outlet } from "react-router-dom";
import { TopBar } from "./TopBar";

export function RootLayout() {
  return (
    <div className="app-shell">
      <TopBar />
      <main style={{ padding: "20px" }}>
        <Outlet />
      </main>
    </div>
  );
}
