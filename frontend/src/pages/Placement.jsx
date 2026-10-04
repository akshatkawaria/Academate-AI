import { useState, useEffect, useCallback } from 'react';
import {
  getSkills, getSkillDetail, getPlacementProgress,
  updateSkillProgress, getReadiness, generateLearningPath
} from '../api';
import {
  ChevronRight, ChevronLeft, ExternalLink, Check, Circle,
  BookOpen, Play, Code2, Briefcase, Star, Zap, RefreshCw
} from 'lucide-react';
import './Placement.css';

// ── localStorage helpers ───────────────────────────────────────────────────────
const LS_LAST_SKILL = 'acadmate_last_skill';
const saveLastSkill  = (slug) => { try { localStorage.setItem(LS_LAST_SKILL, slug); } catch {} };
const loadLastSkill  = ()     => { try { return localStorage.getItem(LS_LAST_SKILL); } catch { return null; } };
const clearLastSkill = ()     => { try { localStorage.removeItem(LS_LAST_SKILL); } catch {} };

// ── Readiness Card ─────────────────────────────────────────────────────────────
function ReadinessCard({ readiness, onRefresh, refreshing }) {
  if (!readiness) return null;
  const { score, status, breakdown } = readiness;
  const color = score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#ef4444';
  return (
    <div className="readiness-card">
      <div className="readiness-header">
        <div>
          <div className="readiness-title">Placement Readiness</div>
          <div className="readiness-status">{status}</div>
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:12 }}>
          <button className="refresh-btn" onClick={onRefresh} disabled={refreshing} title="Recalculate">
            <RefreshCw size={14} className={refreshing ? 'spin' : ''} />
          </button>
          <div className="readiness-score" style={{ color }}>
            <span className="score-num">{score}</span>
            <span className="score-denom">/100</span>
          </div>
        </div>
      </div>
      <div className="readiness-bar">
        <div className="readiness-fill" style={{ width: `${score}%`, background: color }} />
      </div>
      <div className="breakdown-grid">
        {Object.entries(breakdown).map(([k, v]) => (
          <div key={k} className="breakdown-item">
            <span className="breakdown-label">{k.replace(/_/g, ' ')}</span>
            <span className="breakdown-val">{v}pts</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Skill Grid ─────────────────────────────────────────────────────────────────
function SkillGrid({ skills, progress, onSelect }) {
  // Build a map from skill_id → completion_percentage for O(1) lookup
  const progMap = {};
  progress.forEach(p => { progMap[p.skill_id] = p.completion_percentage || 0; });

  return (
    <div className="skill-grid">
      {skills.map(s => {
        const pct = Math.round(progMap[s.id] || 0);
        return (
          <button key={s.slug} className="skill-card" onClick={() => onSelect(s.slug)}
            style={{ '--skill-color': s.color }}>
            <div className="skill-card-icon">{s.icon}</div>
            <div className="skill-card-name">{s.name}</div>
            <div className="skill-card-desc">{s.description}</div>
            <div className="skill-progress-bar">
              <div className="skill-progress-fill" style={{ width: `${pct}%` }} />
            </div>
            <div className="skill-card-footer">
              <span>{pct}% complete</span>
              <ChevronRight size={14} />
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ── Skill Hub ──────────────────────────────────────────────────────────────────
function SkillHub({ slug, uid, onBack, onProgressChange }) {
  const [detail, setDetail]       = useState(null);
  const [tab, setTab]             = useState('roadmap');
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [progRec, setProgRec]     = useState(null);
  const [saving, setSaving]       = useState(false);
  const [loading, setLoading]     = useState(true);
  const [lp, setLp]               = useState(null);
  const [lpLoading, setLpLoading] = useState(false);
  const [lpLevel, setLpLevel]     = useState('beginner');
  const [lpHours, setLpHours]     = useState(2);

  // Load skill detail + user progress together on mount
  useEffect(() => {
    setLoading(true);
    setCompletedSteps(new Set());
    setProgRec(null);

    Promise.allSettled([
      getSkillDetail(slug),
      getPlacementProgress(uid),
    ]).then(([dRes, pRes]) => {
      let skillDetail = null;
      if (dRes.status === 'fulfilled') {
        skillDetail = dRes.value?.data;
        setDetail(skillDetail);
      }
      if (pRes.status === 'fulfilled' && skillDetail) {
        const arr = pRes.value?.data || [];
        // Match by skill_id (UUID) — reliable, not fragile name matching
        const rec = arr.find(p => p.skill_id === skillDetail.id);
        if (rec) {
          setProgRec(rec);
          setCompletedSteps(new Set(rec.completed_steps || []));
        }
      }
      setLoading(false);
    });
  }, [slug, uid]);

  const toggleStep = useCallback(async (stepId) => {
    if (!detail || saving) return;
    const next = new Set(completedSteps);
    next.has(stepId) ? next.delete(stepId) : next.add(stepId);

    // Optimistic UI update immediately
    setCompletedSteps(new Set(next));
    const pct = Math.round((next.size / detail.roadmap.length) * 100);

    setSaving(true);
    try {
      await updateSkillProgress(uid, slug, {
        completion_percentage: pct,
        completed_steps: [...next],
        completed_courses: progRec?.completed_courses || [],
        completed_projects: progRec?.completed_projects || [],
      });
      setProgRec(prev => ({ ...(prev || {}), completed_steps: [...next], completion_percentage: pct }));
      // Notify parent to refresh readiness + skill grid
      if (onProgressChange) onProgressChange();
    } catch {
      // Rollback on failure
      setCompletedSteps(new Set(completedSteps));
    } finally {
      setSaving(false);
    }
  }, [detail, completedSteps, saving, uid, slug, progRec, onProgressChange]);

  const handleGeneratePath = async () => {
    setLpLoading(true);
    try {
      const r = await generateLearningPath({ user_id: uid, skill_slug: slug, skill_level: lpLevel, available_hours: lpHours });
      setLp(r.data);
    } catch { } finally { setLpLoading(false); }
  };

  if (loading || !detail) return (
    <div className="placement-loading">
      <div className="spinner" />
      <p>Loading {slug} hub…</p>
    </div>
  );

  const tabs = [
    { id: 'roadmap',   label: 'Roadmap',       icon: <Zap size={14}/> },
    { id: 'courses',   label: 'Courses',        icon: <BookOpen size={14}/> },
    { id: 'youtube',   label: 'YouTube',        icon: <Play size={14}/> },
    { id: 'projects',  label: 'Projects',       icon: <Code2 size={14}/> },
    { id: 'interview', label: 'Interview Prep', icon: <Briefcase size={14}/> },
    { id: 'path',      label: 'Learning Path',  icon: <Star size={14}/> },
  ];

  const completion = progRec?.completion_percentage || 0;
  const doneCount  = completedSteps.size;
  const totalSteps = detail.roadmap.length;

  return (
    <div className="skill-hub">
      {/* Header */}
      <div className="hub-header" style={{ '--skill-color': detail.color }}>
        <button className="hub-back" onClick={onBack}><ChevronLeft size={18}/>All Skills</button>
        <div className="hub-title-row">
          <span className="hub-icon">{detail.icon}</span>
          <div>
            <h1 className="hub-title">{detail.name} Learning Hub</h1>
            <p className="hub-desc">{detail.description}</p>
          </div>
        </div>
        <div className="hub-progress-row">
          <span>{doneCount}/{totalSteps} steps · {Math.round(completion)}% complete</span>
          {saving && <span className="saving-badge">Saving…</span>}
          <div className="hub-bar">
            <div className="hub-bar-fill" style={{ width: `${completion}%` }}/>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="hub-tabs">
        {tabs.map(t => (
          <button key={t.id} className={`hub-tab${tab===t.id?' active':''}`} onClick={() => setTab(t.id)}>
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="hub-content">

        {/* ── Roadmap ── */}
        {tab === 'roadmap' && (
          <div>
            <div className="roadmap-summary">
              <span className="roadmap-done">{doneCount} completed</span>
              <span className="roadmap-remaining">{totalSteps - doneCount} remaining</span>
            </div>
            <div className="roadmap-list">
              {detail.roadmap.map((step, i) => {
                const done = completedSteps.has(step.id);
                return (
                  <div key={step.id} className={`roadmap-row${done ? ' done' : ''}`}>
                    <button className="roadmap-check" onClick={() => toggleStep(step.id)} disabled={saving}>
                      {done ? <Check size={14}/> : <Circle size={14}/>}
                    </button>
                    <div className="roadmap-connector">
                      {i < detail.roadmap.length - 1 && <div className="connector-line"/>}
                    </div>
                    <div className="roadmap-info">
                      <div className="roadmap-step-name">{step.name}</div>
                      <div className="roadmap-step-desc">{step.description}</div>
                      <span className="roadmap-days">~{step.estimated_days} days</span>
                    </div>
                    {done && <span className="step-done-badge">✓ Done</span>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Courses ── */}
        {tab === 'courses' && (
          <div className="resource-section">
            {['beginner', 'intermediate', 'advanced'].map(lvl => {
              const items = (detail.resources?.course || []).filter(r => r.level === lvl);
              if (!items.length) return null;
              return (
                <div key={lvl} className="resource-group">
                  <div className="resource-group-title">{lvl.charAt(0).toUpperCase() + lvl.slice(1)}</div>
                  <div className="resource-cards">
                    {items.map(r => (
                      <a key={r.id} href={r.url} target="_blank" rel="noreferrer" className="resource-card">
                        <div className="resource-platform">{r.platform}</div>
                        <div className="resource-title">{r.title}</div>
                        <div className="resource-desc">{r.description || 'Click to explore'}</div>
                        <div className="resource-footer">
                          <span className={`res-badge ${r.is_free ? 'free' : 'paid'}`}>{r.is_free ? 'Free' : 'Paid'}</span>
                          <ExternalLink size={12}/>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              );
            })}
            {!(detail.resources?.course?.length) && <div className="empty-state">No courses listed yet.</div>}
          </div>
        )}

        {/* ── YouTube ── */}
        {tab === 'youtube' && (
          <div className="resource-cards">
            {(detail.resources?.youtube || []).map(r => (
              <a key={r.id} href={r.url} target="_blank" rel="noreferrer" className="resource-card yt-card">
                <div className="yt-thumb">▶</div>
                <div className="resource-platform">{r.platform}</div>
                <div className="resource-title">{r.title}</div>
                <div className="resource-footer">
                  <span className="res-badge free">Free</span>
                  <ExternalLink size={12}/>
                </div>
              </a>
            ))}
            {!(detail.resources?.youtube?.length) && <div className="empty-state">No YouTube resources listed.</div>}
          </div>
        )}

        {/* ── Projects ── */}
        {tab === 'projects' && (
          <div className="resource-section">
            {['beginner', 'intermediate', 'advanced'].map(lvl => {
              const items = detail.projects?.[lvl] || [];
              if (!items.length) return null;
              return (
                <div key={lvl} className="resource-group">
                  <div className="resource-group-title">{lvl.charAt(0).toUpperCase() + lvl.slice(1)}</div>
                  <div className="resource-cards">
                    {items.map(p => (
                      <div key={p.id} className="resource-card project-card">
                        <div className="resource-title">{p.title}</div>
                        <div className="project-tags">
                          {(p.skills_required || []).map(s => <span key={s} className="proj-tag">{s}</span>)}
                        </div>
                        <div className="resource-desc">{(p.learning_outcomes || []).join(' · ')}</div>
                        {p.github_url && (
                          <a href={p.github_url} target="_blank" rel="noreferrer" className="resource-footer proj-link">
                            <Code2 size={12}/> View on GitHub <ExternalLink size={11}/>
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ── Interview Prep ── */}
        {tab === 'interview' && (
          <div className="interview-section">
            <div className="interview-card">
              <h3>Interview Preparation for {detail.name}</h3>
              <p>Practice questions and concepts on top platforms.</p>
              <div className="interview-links">
                {[
                  { label: 'LeetCode',      url: 'https://leetcode.com/problemset/' },
                  { label: 'InterviewBit',  url: 'https://www.interviewbit.com/practice/' },
                  { label: 'GeeksForGeeks', url: 'https://www.geeksforgeeks.org/interview-preparation/' },
                  { label: 'Codeforces',    url: 'https://codeforces.com/' },
                  { label: 'HackerRank',    url: 'https://www.hackerrank.com/dashboard' },
                ].map(l => (
                  <a key={l.label} href={l.url} target="_blank" rel="noreferrer" className="interview-link-btn">
                    {l.label} <ExternalLink size={12}/>
                  </a>
                ))}
              </div>
            </div>
            {(detail.resources?.practice || []).map(r => (
              <a key={r.id} href={r.url} target="_blank" rel="noreferrer" className="resource-card">
                <div className="resource-platform">{r.platform}</div>
                <div className="resource-title">{r.title}</div>
                <div className="resource-footer"><ExternalLink size={12}/></div>
              </a>
            ))}
          </div>
        )}

        {/* ── Learning Path ── */}
        {tab === 'path' && (
          <div className="lp-section">
            <div className="lp-controls">
              <label>Level:
                <select value={lpLevel} onChange={e => setLpLevel(e.target.value)}>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </label>
              <label>Hours/Day:
                <input type="number" min={1} max={12} value={lpHours}
                  onChange={e => setLpHours(+e.target.value)} style={{ width: 60 }}/>
              </label>
              <button className="btn btn-primary" onClick={handleGeneratePath} disabled={lpLoading}>
                {lpLoading ? 'Generating…' : lp ? '↺ Regenerate' : '✨ Generate My Path'}
              </button>
            </div>
            {lp && (
              <div className="lp-weeks">
                {Object.values(lp.path).map((week, i) => (
                  <div key={i} className={`lp-week${week.week === lp.current_week ? ' current' : ''}`}>
                    <div className="lp-week-num">Week {week.week}</div>
                    <div className="lp-week-topic">{week.topic}</div>
                    <div className="lp-week-focus">{week.focus}</div>
                    <div className="lp-week-goal">🎯 {week.goal}</div>
                    <div className="lp-week-hours">⏱ {week.daily_hours}h/day</div>
                  </div>
                ))}
              </div>
            )}
            {!lp && !lpLoading && (
              <div className="empty-state">Generate a personalised weekly learning path using AI.</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main Placement Page ────────────────────────────────────────────────────────
export default function Placement({ uid }) {
  const [skills,    setSkills]    = useState([]);
  const [progress,  setProgress]  = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [selected,  setSelected]  = useState(() => loadLastSkill());
  const [loading,   setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadAll = useCallback(async () => {
    if (!uid) return;
    const [sR, pR, rR] = await Promise.allSettled([
      getSkills(),
      getPlacementProgress(uid),
      getReadiness(uid),
    ]);
    if (sR.status === 'fulfilled') setSkills(sR.value?.data || []);
    if (pR.status === 'fulfilled') setProgress(pR.value?.data || []);
    if (rR.status === 'fulfilled') setReadiness(rR.value?.data || null);
  }, [uid]);

  useEffect(() => {
    loadAll().finally(() => setLoading(false));
  }, [loadAll]);

  // Called by SkillHub whenever a step is toggled → refresh readiness + progress grid
  const handleProgressChange = useCallback(async () => {
    const [pR, rR] = await Promise.allSettled([
      getPlacementProgress(uid),
      getReadiness(uid),
    ]);
    if (pR.status === 'fulfilled') setProgress(pR.value?.data || []);
    if (rR.status === 'fulfilled') setReadiness(rR.value?.data || null);
  }, [uid]);

  const handleRefreshReadiness = async () => {
    setRefreshing(true);
    try {
      const r = await getReadiness(uid);
      setReadiness(r.data || null);
    } finally { setRefreshing(false); }
  };

  const handleSelectSkill = (slug) => {
    saveLastSkill(slug);
    setSelected(slug);
  };

  const handleBack = async () => {
    clearLastSkill();
    setSelected(null);
    // Refresh grid when returning to skill explorer
    const [pR, rR] = await Promise.allSettled([
      getPlacementProgress(uid),
      getReadiness(uid),
    ]);
    if (pR.status === 'fulfilled') setProgress(pR.value?.data || []);
    if (rR.status === 'fulfilled') setReadiness(rR.value?.data || null);
  };

  if (loading) return (
    <div className="placement-loading">
      <div className="spinner"/>
      <p>Loading Placement Agent…</p>
    </div>
  );

  if (selected) return (
    <SkillHub
      slug={selected}
      uid={uid}
      onBack={handleBack}
      onProgressChange={handleProgressChange}
    />
  );

  return (
    <div className="placement-page">
      <div className="placement-hero">
        <div className="placement-hero-glow"/>
        <div className="placement-hero-content">
          <div>
            <div className="placement-hero-badge">🚀 Career Development Hub</div>
            <h1 className="placement-hero-title">Placement Agent</h1>
            <p className="placement-hero-sub">Your AI-powered career mentor. Master skills, build projects, and land your dream job.</p>
          </div>
        </div>
      </div>

      <ReadinessCard
        readiness={readiness}
        onRefresh={handleRefreshReadiness}
        refreshing={refreshing}
      />

      <div className="section-heading">
        <span className="section-icon">🎯</span>
        <h2>Skill Explorer</h2>
        <span className="section-sub">Click any skill to open its full Learning Hub</span>
      </div>

      <SkillGrid skills={skills} progress={progress} onSelect={handleSelectSkill} />
    </div>
  );
}
