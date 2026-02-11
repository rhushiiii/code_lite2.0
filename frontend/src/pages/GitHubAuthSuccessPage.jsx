import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/axios";
import Card from "../components/Card";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

function GitHubAuthSuccessPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [message, setMessage] = useState("Finalizing GitHub sign-in...");

  useEffect(() => {
    const completeGitHubAuth = async () => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");

      if (!token) {
        setMessage("GitHub sign-in failed. Please try again.");
        setTimeout(() => navigate("/login", { replace: true }), 1400);
        return;
      }

      try {
        const { data } = await api.get("/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        login(token, data);
        navigate("/dashboard", { replace: true });
      } catch (_error) {
        setMessage("Unable to complete sign-in. Please retry.");
        setTimeout(() => navigate("/login", { replace: true }), 1400);
      }
    };

    completeGitHubAuth();
  }, [login, navigate]);

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-10">
      <Card className="w-full max-w-md border-fuchsia-500/20 text-center">
        <div className="mb-4 flex justify-center">
          <Spinner size="h-8 w-8" />
        </div>
        <p className="text-sm text-slate-200">{message}</p>
      </Card>
    </div>
  );
}

export default GitHubAuthSuccessPage;
