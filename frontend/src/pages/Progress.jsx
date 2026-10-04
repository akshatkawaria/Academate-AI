import { useState, useEffect, useRef, useCallback } from 'react';
import { getAnalytics, getProgress, getTodayTasks, updateTask, autoLogProgress } from '../api';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, RadialBarChart, RadialBar
} from 'recharts';
import StatCard from '../components/StatCard';
import {
  TrendingUp, Clock, Target, Activity, Flame, GraduationCap, Briefcase,
  Zap, Lightbulb, Brain, CheckCircle2, Circle, RefreshCw, AlertTriangle,
  TrendingDown, Minus, ChevronRight, BookOpen, Code2
} from 'lucide-react';

// ─── Score Ring ──────────────────────────────────────────────────────────────
function ScoreRing({ score, label, color, size = 100 }) {
  const r = (size / 2) - 10;
  const circ = 2 * Math.PI * r;
  const filled = circ * (score / 100);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={8} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth={8}
          strokeDasharray={`${filled} ${circ - filled}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: 'stroke-dasharray .6s ease' }}
        />
        <text x={size / 2} y={size / 2 + 6} textAnchor="middle" fill={color} fontSize={size * 0.22} fontWeight={800}>
          {score}
        </text>
      </svg>
      <span style={{ fontSize: '.8rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.5px', textAlign: 'center' }}>{label}</span>
    </div>
  );
}

// ─── Insight Card ─────────────────────────────────────────────────────────────
function InsightCard({ type, title, message }) {
  const cfg = {
    success: { bg: 'rgba(16,185,129,.1)', border: '#10b981', color: '#059669' },
    warning: { bg: 'rgba(245,158,11,.1)', border: '#f59e0b', color: '#d97706' },
    danger:  { bg: 'rgba(239,68,68,.1)',  border: '#ef4444', color: '#dc2626' },
    info:    { bg: 'rgba(99,102,241,.1)', border: '#6366f1', color: '#4f46e5' },
  }[type] || { bg: 'var(--bg-secondary)', border: 'var(--border)', color: 'var(--text-primary)' };

  return (
    <div style={{ padding: '14px 18px', borderRadius: 10, background: cfg.bg, borderLeft: `4px solid ${cfg.border}` }}>
      <div style={{ fontWeight: 700, color: cfg.color, marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: '.88rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{message}</div>
    </div>
  );
}

// ─── Burnout Meter ────────────────────────────────────────────────────────────
function BurnoutMeter({ risk, signals }) {
  const levels = { none: 0, low: 25, medium: 55, high: 90 };
  const colors = { none: '#10b981', low: '#84cc16', medium: '#f59e0b', high: '#ef4444' };
  const val = levels[risk] || 0;
  const color = colors[risk] || '#10b981';

  return (
    <div className="card" style={{ height: '100%' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '1rem', fontWeight: 700 }}>
        <Flame size={18} color={color} /> Burnout Meter
      </h3>
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>Risk Level</span>
          <span style={{ fontWeight: 700, color, textTransform: 'capitalize' }}>{risk}</span>
        </div>
        <div style={{ height: 10, borderRadius: 5, background: 'var(--bg-secondary)', overflow: 'hidden' }}>
          <div style={{ width: `${val}%`, height: '100%', borderRadius: 5, background: color, transition: 'width .6s ease' }} />
        </div>
      </div>
      {signals?.length > 0 && (
        <ul style={{ margin: 0, paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 6 }}>
          {signals.map((s, i) => (
            <li key={i} style={{ fontSize: '.83rem', color: 'var(--text-secondary)' }}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── Task Priority Badge ──────────────────────────────────────────────────────
const PRIORITY_COLOR = { high: '#dc2626', medium: '#d97706', low: '#16a34a' };
const TYPE_ICON = {
  academic:  <BookOpen size={14} />,
  placement: <Code2 size={14} />,
  break:     <Flame size={14} />,
};

// ─── Main Component ───────────────────────────────────────────────────────────
export default function Progress({ uid }) {
  const [analytics, setAnalytics]   = useState(null);
  const [history, setHistory]       = useState([]);
  const [tasks, setTasks]           = useState([]);
  const [syncing, setSyncing]       = useState(false);
  const [loading, setLoading]       = useState(true);
  const loadedRef = useRef(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [aRes, hRes, tRes] = await Promise.all([
        getAnalytics(uid),
        getProgress(uid, 14),
        getTodayTasks(uid),
      ]);
      setAnalytics(aRes.data);
      setHistory((Array.isArray(hRes.data) ? hRes.data : []).reverse().map(h => ({
        ...h,
        date: new Date(h.date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }),
      })));
      setTasks(Array.isArray(tRes.data) ? tRes.data : []);
    } catch (err) {
      console.error('[Progress] Load error:', err);
    } finally {
      setLoading(false);
    }
  }, [uid]);

  useEffect(() => {
    if (!uid || loadedRef.current) return;
    loadedRef.current = true;
    load();
  }, [uid, load]);

  // Toggle task status and auto-sync analytics
  async function toggleTask(task) {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: newStatus } : t));
    try {
      await updateTask(task.id, newStatus === 'completed');
      // auto-sync progress record silently
      await autoLogProgress(uid);
      // refresh analytics quietly (no spinner)
      const [aRes, hRes] = await Promise.all([getAnalytics(uid), getProgress(uid, 14)]);
      setAnalytics(aRes.data);
      setHistory((Array.isArray(hRes.data) ? hRes.data : []).reverse().map(h => ({
        ...h,
        date: new Date(h.date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' }),
      })));
    } catch (err) {
      // rollback optimistic update
      setTasks(prev => prev.map(t => t.id === task.id ? { ...t, status: task.status } : t));
    }
  }

  async function handleSync() {
    setSyncing(true);
    try {
      await autoLogProgress(uid);
      loadedRef.current = false;
      await load();
    } finally {
      setSyncing(false);
    }
  }

  if (loading) return <div className="spinner" style={{ margin: '100px auto' }} />;
  if (!analytics) return (
    <div style={{ padding: 60, textAlign: 'center', color: 'var(--text-secondary)' }}>
      Could not load analytics — make sure the backend is running.
    </div>
  );

  const b    = analytics.behavior || {};
  const bo   = analytics.burnout  || {};
  const ins  = analytics.insights || [];
  const adapt = analytics.planner_adaptation || {};
  const sa   = analytics.subject_analytics   || {};
  const pa   = analytics.placement_analytics || {};

  const completedToday = tasks.filter(t => t.status === 'completed').length;
  const totalToday     = tasks.length;
  const completionPct  = totalToday > 0 ? Math.round((completedToday / totalToday) * 100) : 0;

  const trendIcon = b.trend === 'improving' ? <TrendingUp size={16} color="#10b981" />
    : b.trend === 'declining' ? <TrendingDown size={16} color="#ef4444" />
    : <Minus size={16} color="#6b7280" />;

  return (
    <div style={{ paddingBottom: 60 }}>

      {/* ── Page Header ────────────────────────────────────────────────── */}
      <div className="page-header" style={{ marginBottom: 32 }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Brain size={28} color="var(--primary)" /> Progress Intelligence
        </h1>
        <p>Adaptive analytics powered by your daily AI-generated schedule. Checks update automatically as you complete tasks.</p>
      </div>

      {/* ── SECTION 1: Today's AI Tasks ─────────────────────────────────── */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <CheckCircle2 size={20} color="var(--primary)" /> Today's AI Tasks
          </h2>
          <button
            className="btn btn-ghost btn-sm"
            onClick={handleSync}
            disabled={syncing}
            style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, fontSize: '.8rem' }}
          >
            <RefreshCw size={14} className={syncing ? 'spin' : ''} />
            {syncing ? 'Syncing…' : 'Sync Progress'}
          </button>
        </div>

        {tasks.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '40px 24px', color: 'var(--text-secondary)' }}>
            <Target size={40} opacity={0.2} style={{ margin: '0 auto 16px' }} />
            <p>No AI tasks for today yet.</p>
            <p style={{ fontSize: '.9rem' }}>Generate a plan from the <strong>AI Planner</strong> tab — tasks will appear here automatically.</p>
          </div>
        ) : (
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            {/* progress bar header */}
            <div style={{ padding: '20px 24px 16px', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontWeight: 600, fontSize: '.95rem' }}>{completedToday}/{totalToday} completed</span>
                <span style={{
                  fontSize: '1.4rem', fontWeight: 800,
                  color: completionPct >= 80 ? '#10b981' : completionPct >= 50 ? '#f59e0b' : '#ef4444'
                }}>{completionPct}%</span>
              </div>
              <div style={{ height: 8, borderRadius: 4, background: 'var(--bg-secondary)', overflow: 'hidden' }}>
                <div style={{
                  width: `${completionPct}%`, height: '100%', borderRadius: 4,
                  background: completionPct >= 80 ? '#10b981' : completionPct >= 50 ? '#f59e0b' : '#4f46e5',
                  transition: 'width .5s ease'
                }} />
              </div>
            </div>
            {/* task list */}
            <div>
              {tasks.map((task, i) => {
                const done = task.status === 'completed';
                return (
                  <div
                    key={task.id}
                    onClick={() => toggleTask(task)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 14, padding: '14px 24px',
                      cursor: 'pointer', borderBottom: i < tasks.length - 1 ? '1px solid var(--border)' : 'none',
                      background: done ? 'rgba(16,185,129,.04)' : 'transparent',
                      transition: 'background .2s',
                      userSelect: 'none',
                    }}
                  >
                    {done
                      ? <CheckCircle2 size={22} color="#10b981" style={{ flexShrink: 0 }} />
                      : <Circle size={22} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                    }
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontWeight: 600, fontSize: '.95rem',
                        color: done ? 'var(--text-muted)' : 'var(--text-primary)',
                        textDecoration: done ? 'line-through' : 'none',
                      }}>{task.task_name}</div>
                      <div style={{ display: 'flex', gap: 8, marginTop: 4, alignItems: 'center' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 3, fontSize: '.75rem', color: 'var(--text-muted)' }}>
                          {TYPE_ICON[task.task_type]} {task.task_type}
                        </span>
                        <span style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>•</span>
                        <span style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>
                          <Clock size={11} style={{ verticalAlign: 'middle' }} /> {task.duration_hours}h
                        </span>
                        {task.notes && (
                          <>
                            <span style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>•</span>
                            <span style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>{task.notes}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <span style={{
                      fontSize: '.72rem', fontWeight: 700, padding: '3px 9px', borderRadius: 20,
                      color: 'white', background: PRIORITY_COLOR[task.priority] || '#888'
                    }}>{task.priority}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* ── SECTION 2: Score Rings ──────────────────────────────────────── */}
      <div className="card" style={{ marginBottom: 32 }}>
        <h2 style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Zap size={20} color="#4f46e5" /> Intelligence Scores
        </h2>
        <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 24 }}>
          <ScoreRing score={analytics.productivity_score || 0}   label="Productivity"        color="#4f46e5" size={110} />
          <ScoreRing score={analytics.exam_readiness_score || 0}  label="Exam Readiness"      color="#059669" size={110} />
          <ScoreRing score={analytics.placement_readiness_score || 0} label="Placement Ready" color="#ea580c" size={110} />
          <ScoreRing score={Math.min(100, (b.avg_daily_hours || 0) / 8 * 100 | 0)} label="Study Intensity" color="#7c3aed" size={110} />
        </div>
      </div>

      {/* ── SECTION 3: Stat Row ──────────────────────────────────────────── */}
      <div className="stat-grid" style={{ marginBottom: 32 }}>
        <StatCard icon={<Clock size={20} />}     label="Total Study Hours"  value={`${analytics.total_study_hours}h`}   color="#06b6d4" bg="rgba(6,182,212,.15)" />
        <StatCard icon={<Target size={20} />}    label="Tasks Completed"    value={analytics.total_completed_tasks}     color="#10b981" bg="rgba(16,185,129,.15)" />
        <StatCard icon={<Activity size={20} />}  label="Avg Daily Hours"    value={`${b.avg_daily_hours || 0}h`}        color="#8b5cf6" bg="rgba(139,92,246,.15)" />
        <StatCard icon={<Flame size={20} />}     label="Current Streak"     value={`${analytics.current_streak} days`} color="#f59e0b" bg="rgba(245,158,11,.15)" />
      </div>

      {/* ── SECTION 4: AI Insights + Burnout ────────────────────────────── */}
      <div className="grid-2" style={{ marginBottom: 32, gap: 24 }}>
        <div className="card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '1.1rem' }}>
            <Lightbulb size={20} color="#eab308" /> AI Behavioral Insights
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {ins.map((item, i) => (
              <InsightCard key={i} type={item.type} title={item.title} message={item.message} />
            ))}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <BurnoutMeter risk={bo.risk || 'none'} signals={bo.signals} />
          <div className="card">
            <h3 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, fontSize: '1rem', fontWeight: 700 }}>
              <TrendingUp size={18} color="#3b82f6" /> Productivity Trend
              <span style={{ marginLeft: 4 }}>{trendIcon}</span>
            </h3>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {[
                { label: 'Best Day',  val: b.strongest_day || '—', color: '#10b981' },
                { label: 'Worst Day', val: b.weakest_day   || '—', color: '#ef4444' },
                { label: 'Days Logged', val: b.total_days_logged || 0, color: '#4f46e5' },
              ].map(({ label, val, color }) => (
                <div key={label} style={{ flex: 1, minWidth: 90, padding: '12px 14px', background: 'var(--bg-secondary)', borderRadius: 8 }}>
                  <div style={{ fontSize: '.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 4 }}>{label}</div>
                  <div style={{ fontWeight: 700, color }}>{val}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── SECTION 5: Charts ────────────────────────────────────────────── */}
      <div className="grid-2" style={{ marginBottom: 32, gap: 24 }}>
        <div className="card">
          <h2 style={{ marginBottom: 16 }}>Productivity Score (14 Days)</h2>
          <div style={{ height: 230 }}>
            {history.length > 0 ? (
              <ResponsiveContainer>
                <AreaChart data={history} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="gProd" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#4f46e5" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}   />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }} />
                  <Area type="monotone" dataKey="productivity_score" stroke="#4f46e5" strokeWidth={3} fillOpacity={1} fill="url(#gProd)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : <div className="empty-state"><p>Log data to see trend.</p></div>}
          </div>
        </div>

        <div className="card">
          <h2 style={{ marginBottom: 16 }}>Study Hours & Tasks</h2>
          <div style={{ height: 230 }}>
            {history.length > 0 ? (
              <ResponsiveContainer>
                <BarChart data={history} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip cursor={{ fill: 'var(--bg-elevated)' }} contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }} />
                  <Bar dataKey="study_hours"     fill="#06b6d4" radius={[4,4,0,0]} name="Study Hours" />
                  <Bar dataKey="completed_tasks" fill="#10b981" radius={[4,4,0,0]} name="Tasks Done"  />
                </BarChart>
              </ResponsiveContainer>
            ) : <div className="empty-state"><p>Log data to see chart.</p></div>}
          </div>
        </div>
      </div>

      {/* ── SECTION 6: Subject & Placement Analytics ─────────────────────── */}
      <div className="grid-2" style={{ marginBottom: 32, gap: 24 }}>
        <div className="card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '1.1rem' }}>
            <GraduationCap size={20} color="#059669" /> Subject Analytics
          </h2>
          {sa.weakest_subject && sa.weakest_subject !== 'Not enough data' ? (
            <div style={{ display: 'flex', gap: 12 }}>
              <div style={{ flex: 1, padding: '14px 16px', background: 'rgba(5,150,105,.1)', borderRadius: 10, borderLeft: '3px solid #059669' }}>
                <div style={{ fontSize: '.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 4 }}>Strongest</div>
                <div style={{ fontWeight: 700, color: '#059669', fontSize: '1.1rem' }}>{sa.strongest_subject}</div>
              </div>
              <div style={{ flex: 1, padding: '14px 16px', background: 'rgba(220,38,38,.1)', borderRadius: 10, borderLeft: '3px solid #dc2626' }}>
                <div style={{ fontSize: '.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 4 }}>Weakest</div>
                <div style={{ fontWeight: 700, color: '#dc2626', fontSize: '1.1rem' }}>{sa.weakest_subject}</div>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '.9rem' }}>Complete more academic tasks to activate subject tracking.</p>
          )}
        </div>

        <div className="card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '1.1rem' }}>
            <Briefcase size={20} color="#ea580c" /> Placement Analytics
          </h2>
          {pa.most_avoided && pa.most_avoided !== 'Not enough data' ? (
            <div style={{ padding: '14px 16px', background: 'rgba(234,88,12,.1)', borderRadius: 10, borderLeft: '3px solid #ea580c' }}>
              <div style={{ fontSize: '.75rem', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 4 }}>Most Avoided Topic</div>
              <div style={{ fontWeight: 700, color: '#ea580c', fontSize: '1.1rem', marginBottom: 6 }}>{pa.most_avoided}</div>
              <div style={{ fontSize: '.82rem', color: 'var(--text-secondary)' }}>Planner will automatically prioritize this topic next session.</div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '.9rem' }}>Complete more placement tasks to activate placement tracking.</p>
          )}
        </div>
      </div>

      {/* ── SECTION 7: Planner Evolution ─────────────────────────────────── */}
      <div className="card">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '1.1rem' }}>
          <Activity size={20} color="#3b82f6" /> Planner Evolution Log
        </h2>
        <p style={{ fontSize: '.9rem', color: 'var(--text-secondary)', marginBottom: 16 }}>
          Real-time adaptations the AI has made to your schedule based on your behavior:
        </p>
        {(adapt.adaptations || []).length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {(adapt.adaptations || []).map((ad, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '12px 16px', background: 'rgba(59,130,246,.07)', borderRadius: 8, borderLeft: '3px solid #3b82f6' }}>
                <ChevronRight size={16} color="#3b82f6" style={{ marginTop: 2, flexShrink: 0 }} />
                <span style={{ fontSize: '.92rem', color: 'var(--text-primary)' }}>{ad}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)', fontSize: '.9rem' }}>
            No planner adaptations yet. Complete tasks and generate more AI plans to activate the evolution log.
          </div>
        )}
      </div>

    </div>
  );
}
