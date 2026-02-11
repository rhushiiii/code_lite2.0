function Button({
  children,
  type = "button",
  variant = "primary",
  disabled = false,
  className = "",
  ...props
}) {
  const styles = {
    primary:
      "bg-gradient-to-r from-fuchsia-500 to-violet-500 text-white shadow-lg shadow-fuchsia-900/30 hover:from-fuchsia-400 hover:to-violet-400",
    secondary:
      "border border-slate-600 bg-slate-800/70 text-slate-100 hover:border-fuchsia-400/70 hover:text-white",
    ghost: "text-slate-300 hover:bg-slate-800/70 hover:text-white",
  };

  return (
    <button
      type={type}
      disabled={disabled}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-60 ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
