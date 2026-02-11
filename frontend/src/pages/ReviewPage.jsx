import { useMemo, useState } from "react";

import api from "../api/axios";
import Button from "../components/Button";
import Card from "../components/Card";
import Input from "../components/Input";
import IssueCard from "../components/IssueCard";
import Navbar from "../components/Navbar";
import SkeletonLoader from "../components/SkeletonLoader";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

const initialForm = {
  repo_owner: "",
  repo_name: "",
  pr_number: "",
  github_token: "",
};

function ReviewPage() {
  const { user } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const validationError = useMemo(() => {
    if (!form.repo_owner.trim()) return "Repo owner is required.";
    if (!form.repo_name.trim()) return "Repo name is required.";
    if (!form.pr_number || Number(form.pr_number) <= 0) return "PR number must be a positive integer.";
    if (!user?.github_connected) {
      const token = form.github_token.trim();
      if (!token || token.length < 20) {
        return "Connect GitHub on dashboard or provide a valid GitHub token.";
      }
    }
    return "";
  }, [form, user?.github_connected]);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setResult(null);

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const payload = {
        repo_owner: form.repo_owner,
        repo_name: form.repo_name,
        pr_number: Number(form.pr_number),
      };
      const token = form.github_token.trim();
      if (token) payload.github_token = token;
      const { data } = await api.post("/review", payload);
      setResult(data);
    } catch (apiError) {
      setError(apiError?.response?.data?.detail || "Failed to review pull request.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <Card className="border-fuchsia-500/20">
          <h1 className="text-3xl font-bold text-white">New Pull Request Review</h1>
          <p className="mt-1 text-slate-300">Submit a PR and get structured AI feedback with severity-ranked issues.</p>
          {user?.github_connected && (
            <p className="mt-2 text-sm text-emerald-300">
              GitHub connected as {user.github_username || "GitHub user"}. Token field is optional.
            </p>
          )}

          <form onSubmit={onSubmit} className="mt-6 grid gap-4 md:grid-cols-2">
            <Input
              label="Repo Owner"
              placeholder="octocat"
              value={form.repo_owner}
              onChange={(event) => setForm((prev) => ({ ...prev, repo_owner: event.target.value }))}
              required
            />
            <Input
              label="Repo Name"
              placeholder="hello-world"
              value={form.repo_name}
              onChange={(event) => setForm((prev) => ({ ...prev, repo_name: event.target.value }))}
              required
            />
            <Input
              label="PR Number"
              type="number"
              min="1"
              placeholder="123"
              value={form.pr_number}
              onChange={(event) => setForm((prev) => ({ ...prev, pr_number: event.target.value }))}
              required
            />
            <Input
              label="GitHub Token (Optional if connected)"
              type="password"
              placeholder="ghp_..."
              value={form.github_token}
              onChange={(event) => setForm((prev) => ({ ...prev, github_token: event.target.value }))}
            />

            <div className="md:col-span-2">
              {error && <p className="mb-3 text-sm text-rose-400">{error}</p>}
              <Button type="submit" disabled={loading} className="w-full md:w-auto">
                {loading ? (
                  <>
                    <Spinner />
                    Reviewing...
                  </>
                ) : (
                  "Run AI Review"
                )}
              </Button>
            </div>
          </form>
        </Card>

        {loading && (
          <Card className="mt-6">
            <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">Analyzing diff...</p>
            <SkeletonLoader rows={6} />
          </Card>
        )}

        {result && (
          <section className="mt-6 space-y-4">
            <div className="rounded-2xl border border-slate-700/70 bg-slate-900/60 px-5 py-4 backdrop-blur-xl">
              <h2 className="text-xl font-semibold text-white">Results for {result.repo_name} PR #{result.pr_number}</h2>
              <p className="mt-1 text-slate-300">
                {result.result_json?.issues?.length || 0} issue(s) found across {result.changed_files?.length || 0} file(s).
              </p>
            </div>

            {(result.result_json?.issues || []).map((issue, index) => (
              <IssueCard key={`${issue.file}-${issue.line}-${index}`} issue={issue} index={index} />
            ))}

            {(result.result_json?.issues || []).length === 0 && (
              <Card>
                <p className="text-slate-200">No issues detected in this PR.</p>
              </Card>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default ReviewPage;
