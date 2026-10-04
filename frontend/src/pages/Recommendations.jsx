import { useState, useEffect } from 'react';
import { getRecommendations } from '../api';
import { Lightbulb, Code, BookOpen, Briefcase, FileText } from 'lucide-react';

export default function Recommendations({ uid }) {
  const [recs, setRecs] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (uid) load(); }, [uid]);

  async function load() {
    setLoading(true);
    try {
      const res = await getRecommendations(uid);
      setRecs(res.data);
    } finally { setLoading(false); }
  }

  return (
    <div>
      <div className="page-header">
        <h1>AI Career Roadmap</h1>
        <p>Personalized guidance for skill development and placements based on your profile.</p>
      </div>

      {loading ? <div className="spinner"/> : !recs ? (
        <div className="empty-state">
          <Lightbulb size={40}/>
          <h3>No recommendations yet</h3>
          <p>Complete your profile to get personalized AI roadmaps.</p>
        </div>
      ) : (
        <div className="grid-2">
          {/* DSA Roadmap */}
          {recs.dsa_roadmap && (
            <div className="rec-card" style={{ gridColumn: '1 / -1' }}>
              <h3><Code size={18} color="var(--primary)"/> DSA Preparation Roadmap</h3>
              <div className="divider"/>
              <ul className="rec-list">
                {recs.dsa_roadmap.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}

          {/* Projects */}
          {recs.projects && (
            <div className="rec-card">
              <h3><Briefcase size={18} color="var(--secondary)"/> Suggested Projects</h3>
              <div className="divider"/>
              <ul className="rec-list">
                {recs.projects.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}

          {/* Resume Tips */}
          {recs.resume_tips && (
            <div className="rec-card">
              <h3><FileText size={18} color="var(--success)"/> Resume & Profile Tips</h3>
              <div className="divider"/>
              <ul className="rec-list">
                {recs.resume_tips.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}

          {/* Resources */}
          {recs.resources && (
            <div className="rec-card" style={{ gridColumn: '1 / -1' }}>
              <h3><BookOpen size={18} color="var(--warning)"/> Recommended Learning Resources</h3>
              <div className="divider"/>
              <ul className="rec-list">
                {recs.resources.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
