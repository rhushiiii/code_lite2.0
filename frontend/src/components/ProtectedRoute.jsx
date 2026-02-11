import { Navigate, useLocation } from "react-router-dom";

import Spinner from "./Spinner";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children }) {
  const location = useLocation();
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Spinner size="h-10 w-10" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

export default ProtectedRoute;
