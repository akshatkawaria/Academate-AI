import { useState, useEffect } from 'react';
import { getNotifications, markRead, getAdaptiveMode } from '../api';
import { Bell, CheckCircle, Zap } from 'lucide-react';

export default function Notifications({ uid, onRead }) {
  const [notifs, setNotifs] = useState([]);
  const [mode, setMode] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (uid) load(); }, [uid]);

  async function load() {
    setLoading(true);
    try {
      const [nRes, mRes] = await Promise.all([
        getNotifications(uid),
        getAdaptiveMode(uid)
      ]);
      setNotifs(nRes.data || []);
      setMode(mRes.data);
    } finally { setLoading(false); }
  }

  async function handleMarkRead(nid) {
    try {
      await markRead(nid);
      setNotifs(ns => ns.map(n => n.id === nid ? { ...n, read: true } : n));
      if (onRead) onRead();
    } catch(e) {}
  }

  return (
    <div>
      <div className="page-header">
        <h1>Alerts & Adaptation</h1>
        <p>Smart notifications and your current AI-assigned mode.</p>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        <div className="card">
          <div className="section-header">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Bell size={20}/> All Notifications</h2>
          </div>
          
          {loading ? <div className="spinner"/> : notifs.length === 0 ? (
            <div className="empty-state" style={{ padding: '40px 20px' }}>
              <Bell size={32}/>
              <h3 style={{ marginTop: 12 }}>You're all caught up!</h3>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {notifs.map(n => (
                <div key={n.id} className="notif-item" style={{ opacity: n.read ? 0.6 : 1, paddingRight: 40, position: 'relative' }}>
                  <div className={`notif-dot ${n.read ? 'read' : 'unread'}`}/>
                  <div style={{ flex: 1 }}>
                    <div className="notif-text">{n.message}</div>
                    <div className="notif-time">{n.type} · {new Date(n.created_at).toLocaleString()}</div>
                  </div>
                  {!n.read && (
                    <button 
                      onClick={() => handleMarkRead(n.id)}
                      className="btn btn-ghost" 
                      style={{ position: 'absolute', right: 12, top: 12, padding: '4px', borderRadius: '50%' }}
                      title="Mark as read"
                    >
                      <CheckCircle size={16}/>
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="section-header">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Zap size={20}/> Adaptive Mode</h2>
          </div>
          
          {loading ? <div className="spinner"/> : mode ? (
            <div>
              <div style={{ 
                padding: '24px', 
                borderRadius: '16px', 
                background: mode.assigned_mode === 'Intensive' ? 'rgba(239,68,68,0.1)' : 
                           mode.assigned_mode === 'Moderate' ? 'rgba(245,158,11,0.1)' : 
                           'rgba(16,185,129,0.1)',
                border: `1px solid ${
                           mode.assigned_mode === 'Intensive' ? 'rgba(239,68,68,0.3)' : 
                           mode.assigned_mode === 'Moderate' ? 'rgba(245,158,11,0.3)' : 
                           'rgba(16,185,129,0.3)'}`
              }}>
                <div style={{ fontSize: '.8rem', textTransform: 'uppercase', letterSpacing: '.05em', color: 'var(--text-muted)' }}>Current Mode</div>
                <div style={{ fontSize: '2rem', fontWeight: 700, margin: '4px 0 12px', color: 
                           mode.assigned_mode === 'Intensive' ? '#ef4444' : 
                           mode.assigned_mode === 'Moderate' ? '#f59e0b' : 
                           '#10b981'
                }}>{mode.assigned_mode}</div>
                <p style={{ fontSize: '.9rem', color: 'var(--text-secondary)' }}>{mode.reasoning}</p>
              </div>

              {mode.urgent_tasks && mode.urgent_tasks.length > 0 && (
                <div style={{ marginTop: 20 }}>
                  <h3 style={{ fontSize: '.9rem', fontWeight: 600, marginBottom: 12 }}>⚠️ Urgent Focus Areas</h3>
                  <ul className="rec-list">
                    {mode.urgent_tasks.map((t, i) => <li key={i}>{t}</li>)}
                  </ul>
                </div>
              )}
            </div>
          ) : (
             <div className="empty-state" style={{ padding: '40px 20px' }}>
              <p>No adaptive data available yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
