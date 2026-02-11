function Card({ children, className = "" }) {
  return (
    <div
      className={`rounded-2xl border border-slate-700/60 bg-slate-900/55 p-5 backdrop-blur-xl shadow-xl shadow-slate-950/20 transition-all duration-300 ${className}`}
    >
      {children}
    </div>
  );
}

export default Card;
