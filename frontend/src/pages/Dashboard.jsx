import { useState, useEffect, useRef } from 'react';
import { getSchedule, getAnalytics, generateSchedule, getDashboardFull, autoLogProgress } from '../api';
import { Bell, Search, MoreHorizontal, ChevronRight, Calendar, ExternalLink, TrendingUp, AlertTriangle, Info, CheckCircle, Zap } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

function today() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export default function Dashboard({ uid, profile }) {
  const [schedule,   setSchedule]   = useState([]);
  const [analytics,  setAnalytics]  = useState(null);
  const [dashIntel,  setDashIntel]  = useState(null);  // { notifications, placement_summary, recommendations }
  const [loading,    setLoading]    = useState(true);
  const loadedRef = useRef(false);
  const navigate  = useNavigate();

  useEffect(() => {
    if (!uid || loadedRef.current) return;
    loadedRef.current = true;
    load();
  }, [uid]);

  async function load() {
    setLoading(true);
    try {
      const [sRes, aRes, dRes] = await Promise.allSettled([
        getSchedule(uid, today()),
        getAnalytics(uid),
        getDashboardFull(uid),
      ]);
      if (sRes.status === 'fulfilled') {
        const s = sRes.value?.data;
        setSchedule(Array.isArray(s) ? s : []);
      }
      if (aRes.status === 'fulfilled') setAnalytics(aRes.value?.data ?? null);
      if (dRes.status === 'fulfilled') setDashIntel(dRes.value?.data ?? null);
    } finally { setLoading(false); }
  }

  // ── Header ────────────────────────────────────────────────────────────────
  const now       = new Date();
  const dateStr   = now.toLocaleDateString('en-GB', { weekday:'long', day:'numeric', month:'long', year:'numeric' });
  const timeStr   = now.toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit' });
  const firstName = profile?.name ? profile.name.split(' ')[0] : 'Student';

  // ── Progress chart data ───────────────────────────────────────────────────
  const compTasks = analytics?.total_completed_tasks || 0;
  const totTasks  = compTasks + (analytics?.total_missed_tasks || 0) || 1;
  const pct       = Math.round((compTasks / totTasks) * 100);
  const pieData   = [
    { name:'Completed', value: pct,       color:'#4f46e5' },
    { name:'Remaining', value: 100 - pct, color:'#e5e7eb' },
  ];
  const barData = [
    { day:'M', value:60 },{ day:'T', value:80 },{ day:'W', value:40 },
    { day:'T', value:90 },{ day:'F', value:70 },{ day:'S', value:100 },{ day:'S', value:80 },
  ];

  // ── Destructure dashboard intelligence ───────────────────────────────────
  const notifications    = dashIntel?.notifications    || [];
  const placementSummary = dashIntel?.placement_summary || null;
  const recommendations  = dashIntel?.recommendations  || [];

  return (
    <div>
      {/* ── Header ── */}
      <div className="top-header">
        <div className="header-title-area">
          <div className="header-title">Welcome back, {firstName}! 👋</div>
          <div className="header-date">{dateStr} | {timeStr}</div>
        </div>
        <div className="header-actions">
          <div className="search-bar">
            <Search size={16} color="var(--text-muted)"/>
            <input type="text" placeholder="Search" />
          </div>
          <button className="icon-btn"><Bell size={18}/></button>
          <img src="https://i.pravatar.cc/100?img=11" alt="Avatar" className="user-avatar" style={{width:40,height:40}}/>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* ── Left Column ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:24 }}>

          {/* Daily Schedule */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Daily Schedule Planner</div>
                <div className="card-subtitle">Today's Schedule ({now.toLocaleDateString('en-US',{month:'short',day:'numeric'})})</div>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                <button className="card-action-btn secondary"><Bell size={14}/></button>
                <button className="card-action-btn secondary"><MoreHorizontal size={14}/></button>
              </div>
            </div>
            <div className="timeline">
              {schedule.length > 0 ? schedule.slice(0,5).map((t,i) => {
                const colors = ['bg-blue','bg-purple','bg-green','bg-pink'];
                const c = colors[i % colors.length];
                return (
                  <div key={t.id ?? i} className="timeline-item">
                    <div className="time-label">{t.duration_hours ?? '?'}h</div>
                    <div className={`timeline-block ${c}`}>
                      <span style={{fontWeight:600}}>{t.task_type ?? 'Task'}</span>: {t.task_name ?? 'Unnamed'}
                    </div>
                  </div>
                );
              }) : (
                <div className="timeline-item">
                  <div className="time-label">All Day</div>
                  <div className="timeline-block bg-blue" style={{ justifyContent:'space-between' }}>
                    No tasks yet.
                    <button className="btn btn-primary btn-sm"
                      onClick={() => generateSchedule(uid, today()).then(() => autoLogProgress(uid).catch(() => {})).then(load)}>
                      Generate Plan
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ── Live Placement Preparation ── */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Placement Preparation</div>
                <div className="card-subtitle">
                  {placementSummary
                    ? `${placementSummary.active_skill} Roadmap · ${placementSummary.completion_percentage}% done`
                    : 'Roadmap Progress'}
                </div>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                <button className="card-action-btn secondary" onClick={() => navigate('/placement')}>
                  <ChevronRight size={14}/>
                </button>
              </div>
            </div>

            {placementSummary ? (
              <>
                {/* Readiness row */}
                <div style={{ display:'flex', gap:12, marginBottom:12 }}>
                  <div className="placement-stat-pill">
                    <span>🎯 Readiness</span>
                    <strong style={{ color:'var(--primary)' }}>{placementSummary.readiness_score}%</strong>
                  </div>
                  <div className="placement-stat-pill">
                    <span>📚 Roadmap</span>
                    <strong style={{ color:'#10b981' }}>{placementSummary.completion_percentage}%</strong>
                  </div>
                </div>

                {/* Roadmap visual */}
                <div className="roadmap-container">
                  {(placementSummary.roadmap_visual || []).map(v => (
                    <div key={v.state}
                      className={`roadmap-step ${v.state === 'completed' ? 'step-completed' : v.state === 'current' ? 'step-current' : 'step-upcoming'}`}>
                      {v.label}<br/>
                      <span style={{fontWeight:400,fontSize:'.75rem'}}>{v.items.join(', ')}</span>
                    </div>
                  ))}
                </div>

                {/* Recommended problems */}
                {(placementSummary.recommended_problems || []).map((p, i) => (
                  <a key={i} href={p.url} target="_blank" rel="noreferrer"
                    className="list-item" style={{ textDecoration:'none', color:'inherit' }}>
                    <div className="list-content">
                      <div className="list-title">{p.title}</div>
                    </div>
                    <span className={`diff-badge ${p.difficulty?.toLowerCase()}`}>{p.difficulty}</span>
                    <button className="btn btn-primary btn-sm" style={{borderRadius:4}}>Solve</button>
                  </a>
                ))}

                <button className="btn-outline" style={{ marginTop:8, width:'100%', textAlign:'center' }}
                  onClick={() => navigate('/placement')}>
                  Open Full Placement Hub →
                </button>
              </>
            ) : (
              <>
                {/* fallback static roadmap */}
                <div className="roadmap-container">
                  <div className="roadmap-step step-completed">Completed<br/><span style={{fontWeight:400,fontSize:'.75rem'}}>Arrays, Strings</span></div>
                  <div className="roadmap-step step-current">Current<br/><span style={{fontWeight:400,fontSize:'.75rem'}}>Linked List</span></div>
                  <div className="roadmap-step step-upcoming">Upcoming<br/><span style={{fontWeight:400,fontSize:'.75rem'}}>Stacks, Trees</span></div>
                </div>
                <div className="list-item">
                  <div className="list-content"><div className="list-title">Start your placement journey</div></div>
                  <button className="btn btn-primary btn-sm" onClick={() => navigate('/placement')}>Open Hub</button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* ── Right Column ── */}
        <div style={{ display:'flex', flexDirection:'column', gap:24 }}>

          {/* Progress Tracker */}
          <div className="card">
            <div className="card-header">
              <div>
                <div className="card-title">Progress Tracker</div>
                <div className="card-subtitle">Study Progress &amp; Goals</div>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                <button className="card-action-btn secondary"><TrendingUp size={14}/></button>
                <button className="card-action-btn secondary"><MoreHorizontal size={14}/></button>
              </div>
            </div>
            <div className="progress-container">
              <div style={{ textAlign:'center' }}>
                <div className="progress-circle-wrap">
                  <ResponsiveContainer width={140} height={140}>
                    <PieChart>
                      <Pie data={pieData} innerRadius={45} outerRadius={55} dataKey="value"
                        startAngle={90} endAngle={-270} stroke="none">
                        {pieData.map((entry, i) => <Cell key={`cell-${i}`} fill={entry.color}/>)}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="progress-circle-text">{pct}%</div>
                </div>
                <div style={{ fontSize:'.8rem', marginTop:8, color:'var(--text-secondary)' }}>
                  {compTasks} / {totTasks} tasks done
                </div>
              </div>
              <div style={{ flex:1, height:120 }}>
                <ResponsiveContainer width="100%" height={120}>
                  <BarChart data={barData} margin={{ top:0, right:0, left:0, bottom:0 }}>
                    <Bar dataKey="value" fill="#93c5fd" radius={[4,4,4,4]} barSize={12}/>
                  </BarChart>
                </ResponsiveContainer>
                <div style={{ fontSize:'.8rem', marginTop:8, textAlign:'center', color:'var(--text-secondary)' }}>
                  Weekly task completion
                </div>
              </div>
            </div>
          </div>

          {/* ── Live Learning Recommendations ── */}
          <div className="card" style={{ flex:1 }}>
            <div className="card-header">
              <div>
                <div className="card-title">Learning Recommendations</div>
                <div className="card-subtitle">
                  {placementSummary
                    ? `Based on your ${placementSummary.active_skill} roadmap stage`
                    : 'Suggested Resources'}
                </div>
              </div>
              <button className="card-action-btn secondary" onClick={() => navigate('/placement')}>
                <ChevronRight size={14}/>
              </button>
            </div>

            <div className="rec-cards">
              {recommendations.length > 0 ? recommendations.slice(0,2).map(r => (
                <a key={r.id} href={r.url} target="_blank" rel="noreferrer"
                  className="micro-card" style={{ textDecoration:'none', color:'inherit' }}>
                  <div className="micro-title" style={{ display:'flex', gap:8, alignItems:'center' }}>
                    <div className="micro-icon"
                      style={{ background: r.skill_color + '22', color: r.skill_color, margin:0, width:24, height:24 }}>
                      {r.skill_icon}
                    </div>
                    {r.title}
                  </div>
                  <div className="micro-desc" style={{ marginTop:8 }}>{r.description}</div>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginTop:8 }}>
                    <span className={`res-lvl-badge ${r.level}`}>{r.level}</span>
                    <span className="btn-outline" style={{ fontSize:'.75rem', padding:'3px 8px' }}>
                      Open <ExternalLink size={10} style={{ marginLeft:3 }}/>
                    </span>
                  </div>
                </a>
              )) : (
                <>
                  <div className="micro-card">
                    <div className="micro-title">Striver A2Z DSA Sheet</div>
                    <div className="micro-desc">Structured DSA preparation — most comprehensive roadmap.</div>
                    <a href="https://takeuforward.org/strivers-a2z-dsa-course/" target="_blank" rel="noreferrer" className="btn-outline">View/Start</a>
                  </div>
                  <div className="micro-card">
                    <div className="micro-title">NeetCode 150</div>
                    <div className="micro-desc">Top 150 LeetCode patterns for placement interviews.</div>
                    <a href="https://neetcode.io/practice" target="_blank" rel="noreferrer" className="btn-outline">View/Start</a>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Bottom Row ── */}
      <div className="dashboard-grid-bottom">

        {/* ── Live Notifications ── */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Notifications &amp; Reminders</div>
              <div className="card-subtitle">
                {notifications.length > 0
                  ? `${notifications.filter(n => n.priority === 'high').length} high priority`
                  : 'Live Alerts'}
              </div>
            </div>
            <button className="card-action-btn secondary"><Bell size={14}/></button>
          </div>
          <div>
            {notifications.length > 0 ? notifications.slice(0,5).map((n, i) => {
              const priorityColor = n.priority === 'high' ? '#ef4444' : n.priority === 'medium' ? '#f59e0b' : '#10b981';
              const IconComp = n.priority === 'high' ? AlertTriangle : n.priority === 'medium' ? Zap : CheckCircle;
              return (
                <div key={i} className="list-item" style={{ borderLeft:`3px solid ${priorityColor}`, paddingLeft:10 }}>
                  <div className="list-icon">{n.icon}</div>
                  <div className="list-content">
                    <div className="list-title">{n.title}</div>
                    <div className="list-sub" style={{ marginTop:2 }}>{n.message}</div>
                  </div>
                  <span className="notif-priority-badge" style={{ background: priorityColor + '22', color: priorityColor }}>
                    {n.priority}
                  </span>
                </div>
              );
            }) : (
              <>
                <div className="list-item">
                  <div className="list-icon">🔔</div>
                  <div className="list-content"><div className="list-title">Start DSA Session now!</div></div>
                </div>
                <div className="list-item">
                  <div className="list-icon">⏰</div>
                  <div className="list-content"><div className="list-title">Exam in 2 Days (OS Concepts)</div></div>
                </div>
                <div className="list-item">
                  <div className="list-icon">📚</div>
                  <div className="list-content"><div className="list-title">New Resource: System Design</div></div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Upcoming Hackathons — kept as is (already live via Opportunity Agent) */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Upcoming Hackathons &amp; Events</div>
              <div className="card-subtitle">Opportunities</div>
            </div>
            <button className="card-action-btn secondary" onClick={() => navigate('/opportunities')}>
              <ChevronRight size={14}/>
            </button>
          </div>
          <div>
            <div className="list-item">
              <div className="list-icon">🏆</div>
              <div className="list-content">
                <div className="list-title">Smart India Hackathon</div>
                <div className="list-sub">Major national hackathon</div>
              </div>
              <div style={{ display:'flex', gap:12, alignItems:'center' }}>
                <div className="list-sub"><Calendar size={12}/> Ongoing</div>
                <a href="https://www.sih.gov.in/" target="_blank" rel="noreferrer"
                  className="btn-outline" style={{ border:'none', color:'var(--primary)', padding:0 }}>View</a>
              </div>
            </div>
            <div className="list-item">
              <div className="list-icon">💡</div>
              <div className="list-content">
                <div className="list-title">View All Opportunities</div>
                <div className="list-sub">Hackathons, internships, events</div>
              </div>
              <button className="btn btn-primary btn-sm" onClick={() => navigate('/opportunities')}>Explore</button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
