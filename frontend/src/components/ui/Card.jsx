export default function Card({ title, children, className = '' }) {
  return (
    <div className={`rounded-3xl bg-white/95 shadow-[0_20px_45px_rgba(15,23,42,0.18)] p-6 transition-transform duration-300 hover:-translate-y-1 ${className}`}>
      {title && <h2 className="text-xl font-semibold text-slate-900 mb-4">{title}</h2>}
      {children}
    </div>
  );
}
