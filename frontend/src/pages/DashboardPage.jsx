import { Link2Off, PlugZap } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api/axios";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import EmptyState from "../components/EmptyState";
import Navbar from "../components/Navbar";
import SkeletonLoader from "../components/SkeletonLoader";
import Spinner from "../components/Spinner";
import { useAuth } from "../context/AuthContext";

function DashboardPage() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [repoInsights, setRepoInsights] = useState(null);
  const [repoInsightsLoading, setRepoInsightsLoading] = useState(false);
  const [repoInsightsError, setRepoInsightsError] = useState("");
  const [isConnectingGitHub, setIsConnectingGitHub] = useState(false);
  const [isDisconnectingGitHub, setIsDisconnectingGitHub] = useState(false);
  const [githubMessage, setGithubMessage] = useState("");

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const { data } = await api.get("/reviews");
        setReviews(data);
      } catch (apiError) {
        setError(apiError?.response?.data?.detail || "Could not fetch reviews.");
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, []);

  useEffect(() => {
    const fetchReposAndPendingPrs = async () => {
      if (!user?.github_connected) {
        setRepoInsights(null);
        return;
      }

      setRepoInsightsLoading(true);
      setRepoInsightsError("");
      try {
        const { data } = await api.get("/github/repos-pending-prs", {
          params: { max_repos: 25, pulls_per_repo: 5, only_with_open: false },
        });
        setRepoInsights(data);
      } catch (apiError) {
        setRepoInsightsError(apiError?.response?.data?.detail || "Could not load repositories and pending PRs.");
      } finally {
        setRepoInsightsLoading(false);
      }
    };

    fetchReposAndPendingPrs();
  }, [user?.github_connected]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const status = params.get("github");
    if (!status) return;

    if (status === "connected") {
      setGithubMessage("GitHub connected successfully.");
      refreshUser().catch(() => {});
    } else {
      setGithubMessage("GitHub connection failed. Check OAuth app config and retry.");
    }

    params.delete("github");
    const nextQuery = params.toString();
    const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ""}`;
    window.history.replaceState({}, "", nextUrl);
  }, [refreshUser]);

  const connectGitHub = async () => {
    setGithubMessage("");
    setIsConnectingGitHub(true);
    try {
      const { data } = await api.get("/github/connect-url");
      if (data?.url) {
        window.location.href = data.url;
        return;
      }
      setGithubMessage("Unable to start GitHub OAuth flow.");
    } catch (apiError) {
      setGithubMessage(apiError?.response?.data?.detail || "Unable to start GitHub OAuth flow.");
    } finally {
      setIsConnectingGitHub(false);
    }
  };

  const disconnectGitHub = async () => {
    setGithubMessage("");
    setIsDisconnectingGitHub(true);
    try {
      await api.post("/github/disconnect");
      await refreshUser();
      setGithubMessage("GitHub disconnected.");
    } catch (apiError) {
      setGithubMessage(apiError?.response?.data?.detail || "Unable to disconnect GitHub.");
    } finally {
      setIsDisconnectingGitHub(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white">Review Dashboard</h1>
            <p className="mt-1 text-slate-300">Track and revisit your previous AI PR analyses.</p>
          </div>
          <Button onClick={() => navigate("/review")}>
            New Review
          </Button>
        </div>

        <Card className="mb-6 border-slate-700/80">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300">GitHub Connection</p>
              <p className="text-base font-semibold text-white">
                {user?.github_connected ? `Connected as ${user.github_username || "GitHub User"}` : "Not connected"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {!user?.github_connected ? (
                <Button onClick={connectGitHub} disabled={isConnectingGitHub}>
                  {isConnectingGitHub ? (
                    <>
                      <Spinner />
                      Connecting...
                    </>
                  ) : (
                    <>
                      <PlugZap size={16} />
                      Connect GitHub
                    </>
                  )}
                </Button>
              ) : (
                <Button variant="secondary" onClick={disconnectGitHub} disabled={isDisconnectingGitHub}>
                  {isDisconnectingGitHub ? (
                    <>
                      <Spinner />
                      Disconnecting...
                    </>
                  ) : (
                    <>
                      <Link2Off size={16} />
                      Disconnect
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
          {githubMessage && <p className="mt-3 text-sm text-slate-300">{githubMessage}</p>}
        </Card>

        {user?.github_connected && (
          <Card className="mb-6 border-slate-700/80">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-slate-300">GitHub Repositories</p>
                <p className="text-base font-semibold text-white">Repositories and pending pull requests</p>
              </div>
            </div>

            {repoInsightsLoading && <SkeletonLoader rows={5} />}

            {!repoInsightsLoading && repoInsightsError && (
              <p className="text-sm text-rose-300">{repoInsightsError}</p>
            )}

            {!repoInsightsLoading && !repoInsightsError && repoInsights && (
              <div className="space-y-4">
                <p className="text-sm text-slate-300">
                  Scanned {repoInsights.total_repos_scanned} repo(s).
                </p>
                <div className="space-y-3">
                  {repoInsights.repos.map((repo) => (
                    <div key={repo.full_name} className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <a
                          href={repo.html_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-sm font-semibold text-fuchsia-300 hover:text-fuchsia-200"
                        >
                          {repo.full_name}
                        </a>
                        <span className="text-xs text-slate-300">
                          {repo.pending_pr_count} pending PR{repo.pending_pr_count === 1 ? "" : "s"}
                        </span>
                      </div>

                      {repo.pending_pull_requests.length > 0 ? (
                        <div className="mt-3 space-y-2">
                          {repo.pending_pull_requests.map((pr) => (
                            <a
                              key={`${repo.full_name}-${pr.number}`}
                              href={pr.html_url}
                              target="_blank"
                              rel="noreferrer"
                              className="block rounded-lg border border-slate-700 bg-slate-800/65 px-3 py-2 text-sm transition hover:border-fuchsia-400/40"
                            >
                              <span className="font-medium text-slate-100">#{pr.number}</span>{" "}
                              <span className="text-slate-200">{pr.title}</span>
                            </a>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-3 text-xs text-slate-400">No open PRs in this repository.</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {loading && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, idx) => (
              <Card key={idx} className="border-slate-700/60">
                <SkeletonLoader rows={4} />
              </Card>
            ))}
          </div>
        )}

        {!loading && error && (
          <Card className="border-rose-500/40 bg-rose-500/10">
            <p className="text-rose-200">{error}</p>
          </Card>
        )}

        {!loading && !error && reviews.length === 0 && (
          <EmptyState
            title="No reviews yet"
            description="Run your first PR analysis to see severity summaries and issue-level guidance here."
            ctaLabel="Create First Review"
            onClick={() => navigate("/review")}
          />
        )}

        {!loading && !error && reviews.length > 0 && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {reviews.map((review) => (
              <Card
                key={review.id}
                className="group border-slate-700/70 transition hover:-translate-y-0.5 hover:border-fuchsia-400/45 hover:shadow-glow"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{review.repo_name}</h3>
                    <p className="text-sm text-slate-300">PR #{review.pr_number}</p>
                  </div>
                  <span className="text-xs text-slate-400">{new Date(review.created_at).toLocaleString()}</span>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Badge severity="high" />
                  <span className="text-sm text-slate-200">{review.severity_summary.high} high</span>
                  <Badge severity="medium" />
                  <span className="text-sm text-slate-200">{review.severity_summary.medium} medium</span>
                  <Badge severity="low" />
                  <span className="text-sm text-slate-200">{review.severity_summary.low} low</span>
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default DashboardPage;
