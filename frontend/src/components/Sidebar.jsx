import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  TrendingUp,
  Briefcase,
  Award,
  Settings,
  LogOut,
  Brain,
  Rocket
} from 'lucide-react';

const NAV = [
  { to: '/', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
  { to: '/schedule', icon: <Calendar size={20} />, label: 'Schedule' },
  { to: '/planner', icon: <Settings size={20} />, label: 'AI Planner' },
  { to: '/progress', icon: <TrendingUp size={20} />, label: 'Progress' },

  { to: '/placement', icon: <Rocket size={20} />, label: 'Placement Agent' },

  { to: '/recommendations', icon: <Briefcase size={20} />, label: 'Recommendations' },

  { to: '/opportunities', icon: <Award size={20} />, label: 'Opportunities' },

  { to: '/skills', icon: <Brain size={20} />, label: 'Skills' },
];

export default function Sidebar({ profile }) {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('acadmate_uid');
    navigate('/setup');
    window.location.reload();
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">
          <div className="logo-icon">🌟</div>
          <div className="logo-text">AcadMate AI</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            {profile?.name ? profile.name[0].toUpperCase() : 'S'}
          </div>
          <div className="user-info">
            <div className="user-name">{profile?.name || 'Student Name'}</div>
            <div className="user-sub">Student ID: AM21045</div>
          </div>
          <button onClick={handleLogout} title="Logout" style={{background:'none',border:'none',color:'var(--text-muted)',cursor:'pointer'}}>
            <LogOut size={16}/>
          </button>
        </div>
      </div>
    </aside>
  );
}
