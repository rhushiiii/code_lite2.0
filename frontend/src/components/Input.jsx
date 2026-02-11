function Input({ label, error, className = "", ...props }) {
  return (
    <label className="block w-full">
      {label && <span className="mb-2 block text-sm font-medium text-slate-300">{label}</span>}
      <input
        className={`w-full rounded-xl border border-slate-700/70 bg-slate-900/70 px-4 py-3 text-slate-100 outline-none transition focus:border-fuchsia-400 focus:ring-2 focus:ring-fuchsia-500/25 ${className}`}
        {...props}
      />
      {error && <span className="mt-1 block text-xs text-rose-400">{error}</span>}
    </label>
  );
}

export default Input;
