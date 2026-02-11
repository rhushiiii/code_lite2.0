import { Sparkles } from "lucide-react";

import Button from "./Button";

function EmptyState({ title, description, ctaLabel, onClick }) {
  return (
    <div className="mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-dashed border-slate-600 bg-slate-900/55 px-8 py-14 text-center backdrop-blur-xl">
      <div className="mb-4 rounded-full border border-fuchsia-400/40 bg-fuchsia-500/15 p-4 text-fuchsia-300">
        <Sparkles size={24} />
      </div>
      <h3 className="mb-2 text-xl font-semibold text-white">{title}</h3>
      <p className="mb-6 text-slate-300">{description}</p>
      <Button onClick={onClick}>{ctaLabel}</Button>
    </div>
  );
}

export default EmptyState;
