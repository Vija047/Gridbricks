import { Route, Routes } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import AccuracyPage from "./pages/AccuracyPage";
import DashboardPage from "./pages/DashboardPage";
import DecisionForecastsPage from "./pages/DecisionForecastsPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/decision" element={<DecisionForecastsPage />} />
        <Route path="/accuracy" element={<AccuracyPage />} />
      </Routes>
    </AppShell>
  );
}
