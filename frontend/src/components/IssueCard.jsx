import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

import Badge from "./Badge";
import Card from "./Card";

function IssueCard({ issue, index }) {
  const [isOpen, setIsOpen] = useState(index === 0);

  return (
    <Card className="animate-fade-in-up border-slate-700/80 bg-slate-900/65">
      <button
        type="button"
        onClick={() => setIsOpen((value) => !value)}
        className="flex w-full items-start justify-between gap-4 text-left"
      >
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <Badge severity={issue.severity} />
            <span className="text-sm text-slate-300">Line</span>
            <span className="rounded-md bg-slate-800 px-2 py-0.5 font-mono text-xs text-fuchsia-300">
              {issue.line ?? "N/A"}
            </span>
          </div>
          <p className="text-base font-semibold text-slate-100">{issue.file}</p>
          <p className="text-sm text-slate-300">{issue.message}</p>
        </div>
        <span className="mt-1 text-slate-300">{isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}</span>
      </button>

      <div
        className={`grid transition-all duration-300 ${isOpen ? "mt-4 grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}
      >
        <div className="overflow-hidden space-y-4">
          {issue.code_snippet && (
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Code Snippet</p>
              <pre className="overflow-x-auto rounded-xl border border-slate-700 bg-gray-950/90 p-4 text-xs text-slate-200">
                <code>{issue.code_snippet}</code>
              </pre>
            </div>
          )}

          {issue.suggestion && (
            <div className="rounded-xl border border-fuchsia-400/30 bg-fuchsia-500/10 p-4">
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-fuchsia-300">Suggestion</p>
              <p className="text-sm text-slate-200">{issue.suggestion}</p>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

export default IssueCard;
