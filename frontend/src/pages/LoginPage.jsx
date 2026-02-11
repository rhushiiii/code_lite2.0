import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import api from "../api/axios";
import Button from "../components/Button";
import Card from "../components/Card";
import Input from "../components/Input";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const from = location.state?.from?.pathname || "/dashboard";

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const { data } = await api.post("/auth/login", form);
      login(data.access_token, data.user);
      navigate(from, { replace: true });
    } catch (apiError) {
      setError(apiError?.response?.data?.detail || "Unable to login. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-10">
      <Card className="w-full max-w-md border-fuchsia-500/20">
        <h1 className="text-2xl font-bold text-white">Welcome back</h1>
        <p className="mt-2 text-sm text-slate-300">Sign in to run AI-powered pull request reviews.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="you@company.com"
            value={form.email}
            onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="Your password"
            value={form.password}
            onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
            required
          />

          {error && <p className="text-sm text-rose-400">{error}</p>}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? (
              <>
                <Spinner />
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          New here?{" "}
          <Link to="/signup" className="font-semibold text-fuchsia-300 hover:text-fuchsia-200">
            Create account
          </Link>
        </p>
      </Card>
    </div>
  );
}

export default LoginPage;
