import { BookOpen, ExternalLink, FileText, Video, Globe } from 'lucide-react';

const typeIcons = {
  Documentation: <FileText size={18} />,
  Video: <Video size={18} />,
  Tutorial: <Globe size={18} />,
  Course: <BookOpen size={18} />,
};

const typeColors = {
  Documentation: { bg: '#eff6ff', color: '#2563eb' },
  Video: { bg: '#fef3c7', color: '#b45309' },
  Tutorial: { bg: '#f0fdf4', color: '#16a34a' },
  Course: { bg: '#fce7f3', color: '#be185d' },
};

const diffColors = {
  Beginner: { bg: '#dcfce7', color: '#15803d' },
  Intermediate: { bg: '#fef3c7', color: '#b45309' },
  Advanced: { bg: '#fee2e2', color: '#b91c1c' },
};

export default function ResourceCards({ resources }) {
  if (!resources || resources.length === 0) return null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div className="sk-section-header">
        <div className="sk-section-icon" style={{ background: '#eff6ff', color: '#2563eb' }}>
          <BookOpen size={18} />
        </div>
        Recommended Resources
      </div>
      <div className="sk-resources-grid">
        {resources.map((res, i) => {
          const tc = typeColors[res.type] || typeColors.Tutorial;
          const dc = diffColors[res.difficulty] || diffColors.Intermediate;
          return (
            <div key={i} className="sk-resource-card" style={{ animationDelay: `${i * 0.05}s` }}>
              <div className="sk-resource-icon" style={{ background: tc.bg, color: tc.color }}>
                {typeIcons[res.type] || <BookOpen size={18} />}
              </div>
              <div className="sk-resource-title">{res.title}</div>
              <div className="sk-resource-meta">
                <span className="sk-resource-type">{res.type}</span>
                <span className="sk-resource-difficulty" style={{ background: dc.bg, color: dc.color }}>
                  {res.difficulty}
                </span>
              </div>
              <a
                href={res.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="sk-resource-open-btn"
              >
                <ExternalLink size={14} />
                Open Resource
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
