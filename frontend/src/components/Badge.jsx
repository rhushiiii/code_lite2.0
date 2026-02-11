const tone = {
  low: "bg-emerald-500/15 text-emerald-300 border border-emerald-400/30",
  medium: "bg-amber-500/15 text-amber-300 border border-amber-300/40",
  high: "bg-rose-500/15 text-rose-300 border border-rose-300/40",
};

function Badge({ severity = "low" }) {
  const normalized = String(severity).toLowerCase();
  const style = tone[normalized] || tone.low;

  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${style}`}>
      {normalized}
    </span>
  );
}

export default Badge;
