import { Lightbulb, Code } from 'lucide-react';

const diffColors = {
  Beginner: { bg: '#dcfce7', color: '#15803d', accent: '#10b981' },
  Intermediate: { bg: '#fef3c7', color: '#b45309', accent: '#f59e0b' },
  Advanced: { bg: '#fee2e2', color: '#b91c1c', accent: '#ef4444' },
};

export default function ProjectCards({ projects }) {
  if (!projects || projects.length === 0) return null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div className="sk-section-header">
        <div className="sk-section-icon" style={{ background: '#f3e8ff', color: '#7c3aed' }}>
          <Code size={18} />
        </div>
        Project Recommendations
      </div>
      <div className="sk-projects-grid">
        {projects.map((project, i) => {
          const dc = diffColors[project.difficulty] || diffColors.Intermediate;
          return (
            <div
              key={i}
              className="sk-project-card"
              style={{ animationDelay: `${i * 0.06}s` }}
            >
              <div style={{
                position: 'absolute', top: 0, left: 0, width: 4, height: '100%',
                background: dc.accent, borderRadius: '4px 0 0 4px',
                opacity: 0, transition: 'opacity 0.3s',
              }} className="sk-project-accent" />
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10,
                  background: dc.bg, color: dc.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <Lightbulb size={16} />
                </div>
                <div style={{ flex: 1 }}>
                  <div className="sk-project-name">{project.name}</div>
                  <span className="sk-project-difficulty" style={{ background: dc.bg, color: dc.color }}>
                    {project.difficulty} Project
                  </span>
                </div>
              </div>
              <div className="sk-project-desc">{project.description}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
