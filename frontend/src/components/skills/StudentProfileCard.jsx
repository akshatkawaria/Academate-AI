import { User, GraduationCap, Target, Clock } from 'lucide-react';

export default function StudentProfileCard({ student }) {
  if (!student) return null;

  return (
    <div className="sk-profile-card" id="student-profile-card">
      <div className="sk-profile-header">
        <div className="sk-profile-avatar">
          {student.name?.[0]?.toUpperCase() || 'S'}
        </div>
        <div>
          <div className="sk-profile-name">{student.name}</div>
          <div className="sk-profile-role">{student.target_role}</div>
        </div>
      </div>

      <div className="sk-profile-stats">
        <div className="sk-profile-stat">
          <div className="sk-profile-stat-label">Year</div>
          <div className="sk-profile-stat-value" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            <GraduationCap size={14} color="var(--primary)" />
            {student.year}
          </div>
        </div>
        <div className="sk-profile-stat">
          <div className="sk-profile-stat-label">Study Hours</div>
          <div className="sk-profile-stat-value" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            <Clock size={14} color="var(--accent)" />
            {student.daily_hours} hrs/day
          </div>
        </div>
        <div className="sk-profile-stat" style={{ gridColumn: '1 / -1' }}>
          <div className="sk-profile-stat-label">Target Role</div>
          <div className="sk-profile-stat-value" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            <Target size={14} color="var(--secondary)" />
            {student.target_role}
          </div>
        </div>
      </div>
    </div>
  );
}
