export default function StatCard({ icon, label, value, change, changeDir = 'up', color = '#6c63ff', bg = 'rgba(108,99,255,0.15)' }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ background: bg, color }}>
        {icon}
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {change && (
        <div className={`stat-change ${changeDir}`}>
          {changeDir === 'up' ? '↑' : '↓'} {change}
        </div>
      )}
    </div>
  );
}
