export default function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'w-full rounded-2xl px-4 py-3 text-sm font-semibold transition-colors duration-200';
  const styles = variant === 'danger'
    ? 'bg-red-600 hover:bg-red-700 text-white'
    : variant === 'secondary'
    ? 'bg-slate-100 hover:bg-slate-200 text-slate-900'
    : 'bg-[#667eea] hover:bg-[#5568d3] text-white';

  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
}
