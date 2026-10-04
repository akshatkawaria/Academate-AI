import { useState } from 'react';
import { createProfile } from '../api';

const BRANCHES = ['CSE','IT','ECE','EEE','ME','CE','AIDS','AIML','Cyber Security','Other'];
const YEARS = ['1st Year','2nd Year','3rd Year','4th Year'];
const GOALS = ['Placement at MNC','Startup Career','Higher Studies','Freelancing','Research'];

export default function Setup({ onComplete }) {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({
    name: '', email: '', branch: '', year: '', cgpa: '',
    placement_goal: '', target_companies: '', skills: '',
    daily_study_hours: '6', weekly_off_days: '1',
  });

  const steps = [
    { title: 'Welcome to AcadMate AI 👋', sub: 'Your intelligent academic co-pilot' },
    { title: 'Personal Details',           sub: 'Tell us about yourself' },
    { title: 'Academic Profile',           sub: 'Your academic background' },
    { title: 'Career Goals',              sub: 'What are you aiming for?' },
  ];

  function set(k, v) { setForm(f => ({ ...f, [k]: v })); }

  function canNext() {
    if (step === 0) return true;
    if (step === 1) return form.name.trim() && form.email.trim();
    if (step === 2) return form.branch && form.year && form.cgpa;
    if (step === 3) return form.placement_goal;
    return true;
  }

  async function handleFinish() {
    setLoading(true); setError('');
    try {
      const payload = {
        name: form.name,
        email: form.email,
        branch: form.branch,
        year: parseInt(form.year) || 1,
        cgpa: parseFloat(form.cgpa) || 0,
        placement_goal: form.placement_goal,
        available_hours: parseFloat(form.daily_study_hours) || 4.0,
        target_companies: form.target_companies.split(',').map(s => s.trim()).filter(Boolean),
        skills: form.skills.split(',').map(s => s.trim()).filter(Boolean),
      };
      const res = await createProfile(payload);
      onComplete(res.data.id);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to create profile. Is the backend running?');
    } finally { setLoading(false); }
  }

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-card">
        {/* Step dots */}
        <div className="step-dots">
          {steps.map((_, i) => (
            <div key={i} className={`step-dot${i <= step ? ' active' : ''}`}/>
          ))}
        </div>

        <h2 style={{ fontFamily: "'Space Grotesk',sans-serif", fontSize: '1.4rem', fontWeight: 700, marginBottom: 6 }}>
          {steps[step].title}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '.9rem', marginBottom: 28 }}>
          {steps[step].sub}
        </p>

        {/* Step 0 — Welcome */}
        {step === 0 && (
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ fontSize: '4rem', marginBottom: 20 }}>🎓</div>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, fontSize: '.95rem' }}>
              AcadMate AI uses <strong style={{ color: 'var(--primary-light)' }}>multi-agent AI</strong> to build
              personalized schedules, track your progress, and guide your placement journey — all in one place.
            </p>
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 28, flexWrap: 'wrap' }}>
              {['📅 Smart Schedules','📊 Progress Analytics','💡 AI Roadmaps','🏆 Opportunities'].map(f => (
                <span key={f} className="badge badge-primary" style={{ fontSize: '.8rem', padding: '6px 14px' }}>{f}</span>
              ))}
            </div>
          </div>
        )}

        {/* Step 1 — Personal */}
        {step === 1 && (
          <>
            <div className="form-group">
              <label className="form-label">Full Name *</label>
              <input className="form-input" placeholder="e.g. Arjun Sharma" value={form.name} onChange={e => set('name', e.target.value)}/>
            </div>
            <div className="form-group">
              <label className="form-label">Email Address *</label>
              <input className="form-input" type="email" placeholder="you@college.edu" value={form.email} onChange={e => set('email', e.target.value)}/>
            </div>
          </>
        )}

        {/* Step 2 — Academic */}
        {step === 2 && (
          <>
            <div className="form-group">
              <label className="form-label">Branch *</label>
              <select className="form-select" value={form.branch} onChange={e => set('branch', e.target.value)}>
                <option value="">Select branch</option>
                {BRANCHES.map(b => <option key={b}>{b}</option>)}
              </select>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Year *</label>
                <select className="form-select" value={form.year} onChange={e => set('year', e.target.value)}>
                  <option value="">Select year</option>
                  {YEARS.map(y => <option key={y}>{y}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Current CGPA *</label>
                <input className="form-input" type="number" min="0" max="10" step="0.1" placeholder="8.5" value={form.cgpa} onChange={e => set('cgpa', e.target.value)}/>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label className="form-label">Study hrs/day</label>
                <input className="form-input" type="number" min="1" max="16" value={form.daily_study_hours} onChange={e => set('daily_study_hours', e.target.value)}/>
              </div>
              <div className="form-group">
                <label className="form-label">Off days/week</label>
                <input className="form-input" type="number" min="0" max="3" value={form.weekly_off_days} onChange={e => set('weekly_off_days', e.target.value)}/>
              </div>
            </div>
          </>
        )}

        {/* Step 3 — Career */}
        {step === 3 && (
          <>
            <div className="form-group">
              <label className="form-label">Primary Goal *</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 4 }}>
                {GOALS.map(g => (
                  <button
                    key={g}
                    onClick={() => set('placement_goal', g)}
                    className={`btn btn-sm ${form.placement_goal === g ? 'btn-primary' : 'btn-ghost'}`}
                  >{g}</button>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Target Companies (comma-separated)</label>
              <input className="form-input" placeholder="Google, Microsoft, Infosys" value={form.target_companies} onChange={e => set('target_companies', e.target.value)}/>
            </div>
            <div className="form-group">
              <label className="form-label">Current Skills (comma-separated)</label>
              <input className="form-input" placeholder="Python, DSA, React" value={form.skills} onChange={e => set('skills', e.target.value)}/>
            </div>
          </>
        )}

        {error && <div className="alert alert-danger" style={{ marginTop: 12 }}>⚠️ {error}</div>}

        <div style={{ display: 'flex', gap: 12, marginTop: 28, justifyContent: 'flex-end' }}>
          {step > 0 && (
            <button className="btn btn-ghost" onClick={() => setStep(s => s - 1)}>← Back</button>
          )}
          {step < steps.length - 1 ? (
            <button className="btn btn-primary" disabled={!canNext()} onClick={() => setStep(s => s + 1)}>
              Continue →
            </button>
          ) : (
            <button className="btn btn-primary" disabled={!canNext() || loading} onClick={handleFinish}>
              {loading ? 'Setting up…' : '🚀 Launch AcadMate'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
