import { Target, Check } from 'lucide-react';

export default function PlacementTips({ tips }) {
  if (!tips || tips.length === 0) return null;

  return (
    <div className="sk-tips-card" id="placement-tips">
      <div className="sk-tips-title">
        <Target size={20} color="var(--accent)" />
        Placement Tips
      </div>
      <div className="sk-tips-list">
        {tips.map((tip, i) => (
          <div key={i} className="sk-tip-item">
            <div className="sk-tip-check">
              <Check size={12} strokeWidth={3} />
            </div>
            <div className="sk-tip-text">{tip}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
