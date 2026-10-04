import { Clock, BarChart3, BookOpen, Award } from 'lucide-react';

const difficultyClass = {
  Beginner: 'sk-diff-beginner',
  Intermediate: 'sk-diff-intermediate',
  Advanced: 'sk-diff-advanced',
};

export default function SkillOverviewCard({ skill }) {
  if (!skill) return null;

  const prereqs = typeof skill.prerequisites === 'string'
    ? skill.prerequisites.split(',').map(s => s.trim()).filter(Boolean)
    : Array.isArray(skill.prerequisites) ? skill.prerequisites : [];

  return (
    <div className="sk-overview-card" id="skill-overview-card">
      <div className="sk-overview-header">
        <div>
          <div className="sk-overview-skill-name">{skill.skill_name}</div>
          <div className="sk-overview-category">Category: {skill.category || 'AI / Tech'}</div>
        </div>
        <span className={`sk-overview-difficulty ${difficultyClass[skill.difficulty] || 'sk-diff-intermediate'}`}>
          <BarChart3 size={12} />
          {skill.difficulty}
        </span>
      </div>

      <div className="sk-overview-meta">
        <div className="sk-meta-item">
          <div className="sk-meta-icon" style={{ background: '#eff6ff', color: '#2563eb' }}>
            <Clock size={16} />
          </div>
          <div>
            <div className="sk-meta-label">Duration</div>
            <div className="sk-meta-value">{skill.estimated_duration}</div>
          </div>
        </div>
        <div className="sk-meta-item">
          <div className="sk-meta-icon" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            <Award size={16} />
          </div>
          <div>
            <div className="sk-meta-label">Difficulty</div>
            <div className="sk-meta-value">{skill.difficulty}</div>
          </div>
        </div>
      </div>

      {prereqs.length > 0 && (
        <>
          <div className="sk-overview-prereqs-title">Prerequisites</div>
          <div className="sk-prereq-tags">
            {prereqs.map((p, i) => (
              <span key={i} className="sk-prereq-tag">{p}</span>
            ))}
          </div>
        </>
      )}

      {skill.career_benefits && (
        <>
          <div className="sk-overview-benefits-title">Career Benefits</div>
          <div className="sk-benefits-text">{skill.career_benefits}</div>
        </>
      )}
    </div>
  );
}
