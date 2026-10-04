import { useState } from 'react';
import { generateAdvancedPlan } from '../api';
import { Sparkles, BookOpen, Briefcase, Brain, Heart, Clock, Calendar, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';

const getLocalDateString = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

const INITIAL_FORM = {
  date: getLocalDateString(),
  // Academic
  semester: '5th',
  subjects: 'OS, DBMS, CN',
  weak_subjects: 'DBMS',
  upcoming_exams: '',
  exam_dates: '',
  assignment_deadlines: '',
  target_cgpa: '8.5',
  // Placement
  placement_goal: 'Product Company SDE',
  interested_domain: 'DSA / Backend',
  current_skill_level: 'Intermediate',
  placement_priority: 'medium',
  projects_completed: '2',
  resume_status: 'Needs update',
  // Productivity
  available_study_hours: '5',
  preferred_study_time: 'Morning',
  wake_up_time: '07:00 AM',
  sleep_time: '11:00 PM',
  focus_capacity: '60 mins',
  burnout_level: 'low',
  // Behavioral
  consistency_level: 'medium',
  procrastination_level: 'medium',
  biggest_distraction: 'Social Media',
  // Emotional
  stress_level: 'medium',
  confidence_level: 'medium',
  motivation_goal: 'Land a high-paying tech job',
};

function Section({ icon, title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden', marginBottom: 16 }}>
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        style={{ width: '100%', background: 'var(--bg-card)', padding: '14px 20px', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-primary)', fontWeight: 600 }}
      >
        {icon} {title}
        <span style={{ marginLeft: 'auto' }}>{open ? <ChevronUp size={16}/> : <ChevronDown size={16}/>}</span>
      </button>
      {open && (
        <div style={{ padding: '16px 20px 20px', background: 'var(--bg-secondary)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          {children}
        </div>
      )}
    </div>
  );
}

function Field({ label, children, full }) {
  return (
    <div style={full ? { gridColumn: '1 / -1' } : {}}>
      <label style={{ display: 'block', fontSize: '.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '.5px' }}>{label}</label>
      {children}
    </div>
  );
}

const inp = { className: 'form-input', style: { width: '100%' } };
const sel = { className: 'form-input', style: { width: '100%' } };

export default function Planner({ uid }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const payload = {
        ...form,
        subjects: form.subjects.split(',').map(s => s.trim()).filter(Boolean),
        weak_subjects: form.weak_subjects.split(',').map(s => s.trim()).filter(Boolean),
        upcoming_exams: form.upcoming_exams.split(',').map(s => s.trim()).filter(Boolean),
        target_cgpa: parseFloat(form.target_cgpa) || 8.0,
        projects_completed: parseInt(form.projects_completed) || 0,
        available_study_hours: parseInt(form.available_study_hours) || 4,
      };
      const res = await generateAdvancedPlan(uid, payload);
      setResult(res.data);
    } catch (err) {
      setError('Failed to generate plan. Make sure the backend is running and your API key is set.');
    } finally {
      setLoading(false);
    }
  };

  const typeColors = { academic: '#4f46e5', placement: '#7c3aed', break: '#db2777' };
  const priorityBadge = { high: '#dc2626', medium: '#d97706', low: '#16a34a' };

  return (
    <div>
      <div className="page-header">
        <h1 style={{ display: 'flex', alignItems: 'center', gap: 10 }}><Sparkles size={28} color="var(--primary)" /> AI Mentor Planner</h1>
        <p>Tell your mentor everything. Get a personalized, realistic daily strategy — not just a timetable.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.1fr', gap: 28, alignItems: 'start' }}>

        {/* ─── INPUT PANEL ──────────────────────────────────── */}
        <form onSubmit={handleSubmit}>

          <Section icon={<BookOpen size={16}/>} title="Academic Profile">
            <Field label="Semester"><input {...inp} value={form.semester} onChange={e => set('semester', e.target.value)} /></Field>
            <Field label="Target CGPA"><input {...inp} type="number" step="0.1" min="0" max="10" value={form.target_cgpa} onChange={e => set('target_cgpa', e.target.value)} /></Field>
            <Field label="Subjects (comma separated)" full><input {...inp} value={form.subjects} onChange={e => set('subjects', e.target.value)} /></Field>
            <Field label="Weak Subjects (comma separated)" full><input {...inp} value={form.weak_subjects} onChange={e => set('weak_subjects', e.target.value)} /></Field>
            <Field label="Upcoming Exams (comma separated)" full><input {...inp} value={form.upcoming_exams} onChange={e => set('upcoming_exams', e.target.value)} placeholder="e.g. DBMS, OS" /></Field>
            <Field label="Exam Dates (YYYY-MM-DD, first date)" full><input {...inp} type="text" value={form.exam_dates} onChange={e => set('exam_dates', e.target.value)} placeholder="e.g. 2026-05-15" /></Field>
            <Field label="Assignment Deadlines" full><input {...inp} value={form.assignment_deadlines} onChange={e => set('assignment_deadlines', e.target.value)} placeholder="e.g. CN assignment due May 12" /></Field>
          </Section>

          <Section icon={<Briefcase size={16}/>} title="Placement Profile">
            <Field label="Placement Goal" full><input {...inp} value={form.placement_goal} onChange={e => set('placement_goal', e.target.value)} /></Field>
            <Field label="Domain Interest"><input {...inp} value={form.interested_domain} onChange={e => set('interested_domain', e.target.value)} /></Field>
            <Field label="Skill Level">
              <select {...sel} value={form.current_skill_level} onChange={e => set('current_skill_level', e.target.value)}>
                <option>Beginner</option><option>Intermediate</option><option>Advanced</option>
              </select>
            </Field>
            <Field label="Placement Priority">
              <select {...sel} value={form.placement_priority} onChange={e => set('placement_priority', e.target.value)}>
                <option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
              </select>
            </Field>
            <Field label="Projects Completed"><input {...inp} type="number" min="0" value={form.projects_completed} onChange={e => set('projects_completed', e.target.value)} /></Field>
            <Field label="Resume Status" full><input {...inp} value={form.resume_status} onChange={e => set('resume_status', e.target.value)} placeholder="e.g. Ready / Needs update / Not started" /></Field>
          </Section>

          <Section icon={<Clock size={16}/>} title="Productivity & Schedule">
            <Field label="Study Hours Available"><input {...inp} type="number" min="1" max="16" value={form.available_study_hours} onChange={e => set('available_study_hours', e.target.value)} /></Field>
            <Field label="Preferred Study Time">
              <select {...sel} value={form.preferred_study_time} onChange={e => set('preferred_study_time', e.target.value)}>
                <option>Morning</option><option>Afternoon</option><option>Evening</option><option>Night</option>
              </select>
            </Field>
            <Field label="Wake-Up Time"><input {...inp} value={form.wake_up_time} onChange={e => set('wake_up_time', e.target.value)} placeholder="07:00 AM" /></Field>
            <Field label="Sleep Time"><input {...inp} value={form.sleep_time} onChange={e => set('sleep_time', e.target.value)} placeholder="11:00 PM" /></Field>
            <Field label="Focus Capacity">
              <select {...sel} value={form.focus_capacity} onChange={e => set('focus_capacity', e.target.value)}>
                <option>30 mins</option><option>45 mins</option><option>60 mins</option><option>90 mins</option>
              </select>
            </Field>
            <Field label="Burnout Level">
              <select {...sel} value={form.burnout_level} onChange={e => set('burnout_level', e.target.value)}>
                <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
              </select>
            </Field>
            <Field label="Target Date" full><input {...inp} type="date" value={form.date} onChange={e => set('date', e.target.value)} required /></Field>
          </Section>

          <Section icon={<Brain size={16}/>} title="Behavior & Emotions" defaultOpen={false}>
            <Field label="Consistency Level">
              <select {...sel} value={form.consistency_level} onChange={e => set('consistency_level', e.target.value)}>
                <option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
              </select>
            </Field>
            <Field label="Procrastination Level">
              <select {...sel} value={form.procrastination_level} onChange={e => set('procrastination_level', e.target.value)}>
                <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
              </select>
            </Field>
            <Field label="Stress Level">
              <select {...sel} value={form.stress_level} onChange={e => set('stress_level', e.target.value)}>
                <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
              </select>
            </Field>
            <Field label="Confidence Level">
              <select {...sel} value={form.confidence_level} onChange={e => set('confidence_level', e.target.value)}>
                <option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option>
              </select>
            </Field>
            <Field label="Biggest Distraction" full><input {...inp} value={form.biggest_distraction} onChange={e => set('biggest_distraction', e.target.value)} /></Field>
            <Field label="Motivation Goal" full><input {...inp} value={form.motivation_goal} onChange={e => set('motivation_goal', e.target.value)} /></Field>
          </Section>

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '12px 16px', color: '#b91c1c', fontSize: '.9rem', marginBottom: 16 }}>
              ⚠️ {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '14px', fontSize: '1rem', gap: 10, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
            disabled={loading}
          >
            {loading
              ? <><span className="spinner" style={{ width: 18, height: 18, margin: 0 }} /> Generating your strategy...</>
              : <><Sparkles size={18} /> Generate AI Strategy</>}
          </button>
        </form>

        {/* ─── RESULTS PANEL ────────────────────────────────── */}
        <div style={{ position: 'sticky', top: 24 }}>
          {result ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

              {/* Workload Balance & Adaptive Insights */}
              <div className="card" style={{ background: 'linear-gradient(135deg, #4f46e5, #7c3aed)', color: 'white' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14, fontWeight: 700, fontSize: '1rem' }}>
                  <AlertCircle size={18} /> Today's Strategy
                </div>
                <p style={{ fontSize: '.95rem', lineHeight: 1.7, marginBottom: 18, opacity: 0.95 }}>
                  {result.plan_summary?.reason}
                </p>
                
                {result.adaptive_insights && result.adaptive_insights.length > 0 && (
                  <div style={{ marginTop: 16, marginBottom: 18, padding: 16, backgroundColor: 'rgba(255, 255, 255, 0.15)', borderRadius: 10, borderLeft: '4px solid #fff' }}>
                    <h3 style={{ fontSize: '.9rem', color: '#fff', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}><Brain size={16}/> How your planner evolved today:</h3>
                    <ul style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {result.adaptive_insights.map((insight, idx) => (
                        <li key={idx} style={{ color: '#fff', fontSize: '.9rem', opacity: 0.95 }}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <div style={{ display: 'flex', gap: 12 }}>
                  <div style={{ flex: 1, background: 'rgba(255,255,255,.15)', borderRadius: 10, padding: '12px 16px' }}>
                    <div style={{ fontSize: '.75rem', textTransform: 'uppercase', opacity: 0.8, marginBottom: 4 }}>Academic</div>
                    <div style={{ fontSize: '2rem', fontWeight: 800 }}>{result.plan_summary?.academic_focus}%</div>
                  </div>
                  <div style={{ flex: 1, background: 'rgba(255,255,255,.15)', borderRadius: 10, padding: '12px 16px' }}>
                    <div style={{ fontSize: '.75rem', textTransform: 'uppercase', opacity: 0.8, marginBottom: 4 }}>Placement</div>
                    <div style={{ fontSize: '2rem', fontWeight: 800 }}>{result.plan_summary?.placement_focus}%</div>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700, marginBottom: 20 }}>
                  <Calendar size={18} /> Schedule Timeline
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {Array.isArray(result.schedule) && result.schedule.map((task, i) => (
                    <div key={i} style={{ display: 'flex', gap: 14 }}>
                      {/* Time column */}
                      <div style={{ width: 90, flexShrink: 0, textAlign: 'right' }}>
                        <div style={{ fontSize: '.8rem', fontWeight: 700, color: 'var(--text-primary)' }}>{task.start_time}</div>
                        <div style={{ fontSize: '.75rem', color: 'var(--text-muted)' }}>→ {task.end_time}</div>
                      </div>
                      {/* Connector dot */}
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        <div style={{ width: 12, height: 12, borderRadius: '50%', background: typeColors[task.task_type] || '#999', marginTop: 3, flexShrink: 0 }} />
                        {i < result.schedule.length - 1 && <div style={{ width: 2, flex: 1, background: 'var(--border)', marginTop: 4 }} />}
                      </div>
                      {/* Task card */}
                      <div style={{ flex: 1, background: 'var(--bg-secondary)', borderRadius: 10, padding: '12px 14px', border: `1px solid var(--border)` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 6 }}>
                          <span style={{ fontWeight: 600, fontSize: '.95rem', color: 'var(--text-primary)' }}>{task.task_name}</span>
                          <span style={{ fontSize: '.72rem', background: priorityBadge[task.priority] || '#888', color: 'white', borderRadius: 4, padding: '2px 8px', flexShrink: 0 }}>
                            {task.priority}
                          </span>
                        </div>
                        <p style={{ fontSize: '.82rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>{task.reason}</p>
                        <div style={{ marginTop: 8 }}>
                          <span style={{ fontSize: '.72rem', background: typeColors[task.task_type] || '#888', color: 'white', borderRadius: 4, padding: '2px 8px' }}>
                            {task.task_type}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Productivity Advice */}
              {Array.isArray(result.productivity_advice) && result.productivity_advice.length > 0 && (
                <div className="card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700, marginBottom: 16 }}>
                    <Heart size={18} color="#e11d48" /> Mentor Advice
                  </div>
                  <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {result.productivity_advice.map((tip, i) => (
                      <li key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', fontSize: '.9rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                        <span style={{ color: '#4f46e5', fontWeight: 800, marginTop: 1 }}>→</span> {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: '60px 24px', color: 'var(--text-muted)', textAlign: 'center' }}>
              <Sparkles size={48} opacity={0.2} />
              <p style={{ maxWidth: 280 }}>Complete your profile and click <strong>Generate AI Strategy</strong> to get a fully personalized daily plan.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
