import { Map, BookOpen } from 'lucide-react';

export default function RoadmapTimeline({ learningPlan }) {
  if (!learningPlan || learningPlan.length === 0) return null;

  const dotColors = ['#3b82f6', '#7c3aed', '#10b981', '#f59e0b', '#ec4899', '#06b6d4'];

  return (
    <div className="sk-roadmap-card" id="roadmap-timeline">
      <div className="sk-roadmap-title">
        <Map size={20} color="var(--primary)" />
        Learning Roadmap
      </div>

      <div className="sk-timeline">
        {learningPlan.map((week, i) => (
          <div key={i} className="sk-timeline-item">
            <div
              className="sk-timeline-dot"
              style={{ borderColor: dotColors[i % dotColors.length] }}
            >
              <div
                className="sk-timeline-dot-inner"
                style={{ background: dotColors[i % dotColors.length] }}
              />
            </div>

            <div className="sk-timeline-week" style={{ color: dotColors[i % dotColors.length] }}>
              Week {week.week}
            </div>
            <div className="sk-timeline-focus">{week.focus}</div>

            {week.tasks && week.tasks.length > 0 && (
              <div className="sk-timeline-tasks">
                {week.tasks.map((task, j) => (
                  <div key={j} className="sk-timeline-task">
                    <div className="sk-timeline-task-dot" />
                    {task}
                  </div>
                ))}
              </div>
            )}

            {week.resources && week.resources.length > 0 && (
              <div className="sk-timeline-resources">
                {week.resources.map((res, j) => (
                  <span key={j} className="sk-timeline-resource-tag">
                    <BookOpen size={10} />
                    {res}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
