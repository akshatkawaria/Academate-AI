import { useState, useEffect, useRef } from 'react';
import { getSchedule, generateSchedule, updateTask, autoLogProgress } from '../api';
import { CalendarDays, Zap, Clock, CheckCircle } from 'lucide-react';

function getDates() {
  const dates = [];
  for (let i = -3; i <= 7; i++) {
    const d = new Date();
    d.setDate(d.getDate() + i);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    dates.push(`${year}-${month}-${day}`);
  }
  return dates;
}

export default function Schedule({ uid }) {
  const dates = getDates();
  const [selectedDate, setSelectedDate] = useState(dates[3]); // Today
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [genLoading, setGenLoading] = useState(false);

  const loadedRef = useRef('');
  useEffect(() => {
    const key = `${uid}:${selectedDate}`;
    if (!uid || loadedRef.current === key) return;
    loadedRef.current = key;
    load();
  }, [uid, selectedDate]);

  async function load() {
    setLoading(true);
    try {
      const res = await getSchedule(uid, selectedDate);
      setSchedule(res.data || []);
    } finally { setLoading(false); }
  }

  async function handleGenerate() {
    setGenLoading(true);
    try {
      await generateSchedule(uid, selectedDate);
      if (selectedDate === dates[3]) await autoLogProgress(uid).catch(() => {});
      await load();
    } catch (e) { alert('Failed to generate schedule.'); }
    finally { setGenLoading(false); }
  }

  async function toggleTask(task) {
    const done = task.status !== 'completed';
    await updateTask(task.id, done).catch(() => {});
    if (selectedDate === dates[3]) await autoLogProgress(uid).catch(() => {});
    setSchedule(s => s.map(t => t.id === task.id ? { ...t, status: done ? 'completed' : 'pending' } : t));
  }

  const isToday = selectedDate === dates[3];

  return (
    <div>
      <div className="page-header">
        <h1>Schedule planner</h1>
        <p>AI-generated daily plans customized for your goals.</p>
      </div>

      <div className="card" style={{ marginBottom: 24, padding: 12 }}>
        <div style={{ display: 'flex', overflowX: 'auto', gap: 8, paddingBottom: 4 }}>
          {dates.map(date => {
            const d = new Date(date);
            const isSel = selectedDate === date;
            return (
              <button
                key={date}
                onClick={() => setSelectedDate(date)}
                className={`btn ${isSel ? 'btn-primary' : 'btn-ghost'}`}
                style={{ flexShrink: 0, flexDirection: 'column', padding: '10px 16px', borderRadius: 12, minWidth: 80 }}
              >
                <span style={{ fontSize: '.7rem', textTransform: 'uppercase', opacity: isSel ? .8 : .5 }}>
                  {d.toLocaleDateString('en-US', { weekday: 'short' })}
                </span>
                <span style={{ fontSize: '1.2rem', fontWeight: 700 }}>{d.getDate()}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="card">
        <div className="section-header">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <CalendarDays size={20}/> Tasks for {new Date(selectedDate).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}
          </h2>
          <button className="btn btn-primary btn-sm" onClick={handleGenerate} disabled={genLoading}>
            <Zap size={14}/> {genLoading ? 'Generating...' : 'Generate AI Plan'}
          </button>
        </div>

        {loading ? <div className="spinner"/> : schedule.length === 0 ? (
          <div className="empty-state">
            <CalendarDays size={40}/>
            <h3>No tasks scheduled</h3>
            <p>Generate a new AI plan for this day to get started.</p>
          </div>
        ) : (
          <div>
            {schedule.map(task => {
              const isDone = task.status === 'completed';
              return (
                <div key={task.id} className={`task-item${isDone ? ' done' : ''}`} style={{ padding: '16px' }}>
                  <div className={`task-checkbox${isDone ? ' checked' : ''}`} onClick={() => toggleTask(task)} style={{ width: 24, height: 24 }}>
                    {isDone && <span style={{ color: '#fff', fontSize: '.8rem' }}>✓</span>}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="task-title" style={{ fontSize: '1rem', marginBottom: 4 }}>{task.task_name}</div>
                    <div className="task-meta">
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={12}/> {task.duration_hours}h</span>
                      <span className="badge badge-muted">{task.task_type}</span>
                      {task.notes && <span className="badge badge-cyan">{task.notes}</span>}
                    </div>
                  </div>
                  {task.priority === 'high' && <span className="badge badge-danger">High Priority</span>}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
