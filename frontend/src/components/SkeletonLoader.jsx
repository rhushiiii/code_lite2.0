function SkeletonLoader({ rows = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, index) => (
        <div
          key={index}
          className="h-4 animate-pulse rounded-lg bg-slate-700/60"
          style={{ width: `${100 - index * 12}%` }}
        />
      ))}
    </div>
  );
}

export default SkeletonLoader;
