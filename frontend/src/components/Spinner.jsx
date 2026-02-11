function Spinner({ size = "h-5 w-5" }) {
  return (
    <span
      className={`${size} inline-block animate-spin rounded-full border-2 border-slate-400 border-t-fuchsia-400`}
      aria-label="loading"
    />
  );
}

export default Spinner;
