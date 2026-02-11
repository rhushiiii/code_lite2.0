import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import DashboardPage from "./pages/DashboardPage";
import GitHubAuthSuccessPage from "./pages/GitHubAuthSuccessPage";
import LoginPage from "./pages/LoginPage";
import ReviewPage from "./pages/ReviewPage";
import SignupPage from "./pages/SignupPage";

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="relative min-h-screen overflow-x-hidden text-slate-100">
      <div className="pointer-events-none fixed inset-0 -z-20 bg-[radial-gradient(circle_at_20%_15%,rgba(192,132,252,0.18),transparent_35%),radial-gradient(circle_at_80%_8%,rgba(124,58,237,0.2),transparent_30%),linear-gradient(180deg,#020617_0%,#030712_100%)]" />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[linear-gradient(rgba(148,163,184,0.08)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.08)_1px,transparent_1px)] bg-[size:56px_56px] opacity-[0.06]" />

      <Routes>
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <SignupPage />} />
        <Route path="/auth/github/success" element={<GitHubAuthSuccessPage />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/review"
          element={
            <ProtectedRoute>
              <ReviewPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </div>
  );
}

export default App;
