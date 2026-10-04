import { useState, useEffect, useMemo } from 'react';
import { getOpportunities } from '../api';
import {
  Trophy, Calendar, MapPin, ExternalLink, Filter, Clock,
  Search, Users, Zap, ChevronDown, Briefcase, Award,
  TrendingUp, Globe, Star
} from 'lucide-react';

const TYPE_CONFIG = {
  hackathon: { label: 'Hackathon', color: '#3b82f6', bg: '#eff6ff', border: '#bfdbfe', icon: '⚡' },
  internship: { label: 'Internship', color: '#10b981', bg: '#ecfdf5', border: '#a7f3d0', icon: '💼' },
};

const LOCATIONS = [
  { value: 'all', label: '🌍 All Locations' },
  { value: 'Bangalore', label: '📍 Bangalore & Nearby' },
  { value: 'Hyderabad', label: '📍 Hyderabad & Nearby' },
  { value: 'Chennai', label: '📍 Chennai & Nearby' },
  { value: 'Delhi NCR', label: '📍 Delhi NCR' },
  { value: 'Mumbai', label: '📍 Mumbai & Nearby' },
  { value: 'Pune', label: '📍 Pune & Nearby' },
  { value: 'Online', label: '🌐 Online Only' },
];

// Nearby city clusters — mirrors backend logic for client-side filtering
const NEARBY_CITIES = {
  Bangalore: ['Bangalore', 'Hyderabad', 'Chennai', 'Online'],
  Hyderabad: ['Hyderabad', 'Bangalore', 'Chennai', 'Online'],
  Chennai: ['Chennai', 'Bangalore', 'Hyderabad', 'Online'],
  'Delhi NCR': ['Delhi NCR', 'Noida', 'Gurgaon', 'Gurugram', 'Online'],
  Mumbai: ['Mumbai', 'Pune', 'Online'],
  Pune: ['Pune', 'Mumbai', 'Online'],
  Online: ['Online'],
};

function formatNumber(num) {
  if (!num) return '0';
  if (num >= 1000) return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(num);
}

function getDeadlineUrgency(daysLeft) {
  if (daysLeft <= 3) return { text: 'Ending Soon!', class: 'opp-urgency-critical' };
  if (daysLeft <= 7) return { text: `${daysLeft}d left`, class: 'opp-urgency-high' };
  if (daysLeft <= 14) return { text: `${daysLeft}d left`, class: 'opp-urgency-medium' };
  if (daysLeft <= 30) return { text: `${daysLeft}d left`, class: 'opp-urgency-normal' };
  return { text: `${daysLeft}d left`, class: 'opp-urgency-low' };
}

/**
 * Client-side filtering of static opportunities data.
 * Mirrors the backend agent's filtering logic exactly.
 */
function filterOpportunitiesLocally(data, filters) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return data
    .map(opp => {
      // Parse deadline
      const deadline = opp.deadline ? new Date(opp.deadline) : null;
      if (!deadline || deadline <= today) return null; // expired

      // Type filter
      if (filters.type && opp.type?.toLowerCase() !== filters.type.toLowerCase()) return null;

      // Mode filter
      if (filters.mode && opp.mode?.toLowerCase() !== filters.mode.toLowerCase()) return null;

      // Level filter
      if (filters.level) {
        const oppLevel = (opp.level || 'all').toLowerCase();
        if (oppLevel !== 'all' && oppLevel !== filters.level.toLowerCase()) return null;
      }

      // Location filter with nearby-city expansion
      if (filters.location && filters.location.toLowerCase() !== 'all') {
        const locKey = filters.location;
        const allowedSet = (NEARBY_CITIES[locKey] || [locKey, 'Online']).map(c => c.toLowerCase());
        const oppLocation = (opp.location || '').toLowerCase();
        if (!allowedSet.includes(oppLocation)) return null;
      }

      // Add computed days_left
      const daysLeft = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
      return { ...opp, days_left: daysLeft };
    })
    .filter(Boolean)
    .sort((a, b) => (a.deadline || '').localeCompare(b.deadline || ''));
}

function OrgAvatar({ name, type }) {
  const initial = (name || '?')[0].toUpperCase();
  const config = TYPE_CONFIG[type] || TYPE_CONFIG.hackathon;
  return (
    <div className="opp-org-avatar" style={{ background: config.bg, color: config.color, borderColor: config.border }}>
      {initial}
    </div>
  );
}

export default function Opportunities() {
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({ type: '', level: '', mode: '', location: '' });

  useEffect(() => { load(); }, [filters]);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      // Try the backend API first
      const params = {};
      if (filters.type) params.type = filters.type;
      if (filters.level) params.level = filters.level;
      if (filters.mode) params.mode = filters.mode;
      if (filters.location) params.location = filters.location;
      const res = await getOpportunities(params);
      const data = res.data;
      if (Array.isArray(data)) {
        setOpps(data);
      } else if (data && Array.isArray(data.opportunities)) {
        setOpps(data.opportunities);
      } else {
        setOpps([]);
      }
    } catch (err) {
      console.warn('[Opportunities] Backend unavailable, loading static dataset...', err.message);
      // Fallback: load from static JSON served from /opportunities.json
      try {
        const res = await fetch('/opportunities.json');
        const rawData = await res.json();
        const filtered = filterOpportunitiesLocally(Array.isArray(rawData) ? rawData : [], filters);
        setOpps(filtered);
      } catch (fallbackErr) {
        console.error('[Opportunities] Static fallback also failed:', fallbackErr);
        setError('Failed to load opportunities. Please check if the backend is running.');
        setOpps([]);
      }
    } finally {
      setLoading(false);
    }
  }

  const filteredOpps = useMemo(() => {
    if (!searchQuery.trim()) return opps;
    const q = searchQuery.toLowerCase();
    return opps.filter(o =>
      (o.title || '').toLowerCase().includes(q) ||
      (o.organizer || '').toLowerCase().includes(q) ||
      (o.skills || []).some(s => s.toLowerCase().includes(q))
    );
  }, [opps, searchQuery]);

  const stats = useMemo(() => ({
    total: opps.length,
    hackathons: opps.filter(o => o.type === 'hackathon').length,
    internships: opps.filter(o => o.type === 'internship').length,
    live: opps.filter(o => o.tags?.includes('live')).length,
  }), [opps]);

  return (
    <div className="opp-page">
      {/* ─── Hero Section ─── */}
      <div className="opp-hero">
        <div className="opp-hero-content">
          <div className="opp-hero-text">
            <div className="opp-hero-badge">
              <Zap size={14} /> Live Opportunities
            </div>
            <h1 className="opp-hero-title">Opportunities Hub</h1>
            <p className="opp-hero-subtitle">
              Discover top hackathons, internships & competitions — curated for you.
            </p>
          </div>
          <div className="opp-hero-stats">
            <div className="opp-stat-card">
              <div className="opp-stat-value">{stats.total}</div>
              <div className="opp-stat-label">Total</div>
            </div>
            <div className="opp-stat-card">
              <div className="opp-stat-value">{stats.hackathons}</div>
              <div className="opp-stat-label">Hackathons</div>
            </div>
            <div className="opp-stat-card">
              <div className="opp-stat-value">{stats.internships}</div>
              <div className="opp-stat-label">Internships</div>
            </div>
            {stats.live > 0 && (
              <div className="opp-stat-card opp-stat-live">
                <div className="opp-stat-value">{stats.live}</div>
                <div className="opp-stat-label">Live</div>
              </div>
            )}
          </div>
        </div>
        <div className="opp-hero-glow" />
      </div>

      {/* ─── Filter + Search Bar ─── */}
      <div className="opp-toolbar">
        <div className="opp-search-wrap">
          <Search size={18} className="opp-search-icon" />
          <input
            type="text"
            className="opp-search-input"
            placeholder="Search by title, company, or skill..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="opp-filters">
          <div className="opp-filter-group">
            <Filter size={16} />
            <span className="opp-filter-label">Filters</span>
          </div>

          <select className="opp-filter-select" value={filters.type} onChange={e => setFilters({ ...filters, type: e.target.value })}>
            <option value="">All Types</option>
            <option value="hackathon">⚡ Hackathons</option>
            <option value="internship">💼 Internships</option>
          </select>

          <select className="opp-filter-select" value={filters.location} onChange={e => setFilters({ ...filters, location: e.target.value })}>
            {LOCATIONS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
          </select>

          <select className="opp-filter-select" value={filters.mode} onChange={e => setFilters({ ...filters, mode: e.target.value })}>
            <option value="">All Modes</option>
            <option value="online">🌐 Online</option>
            <option value="offline">🏢 Offline</option>
            <option value="hybrid">🔄 Hybrid</option>
          </select>

          <select className="opp-filter-select" value={filters.level} onChange={e => setFilters({ ...filters, level: e.target.value })}>
            <option value="">All Levels</option>
            <option value="undergraduate">🎓 Undergraduate</option>
            <option value="postgraduate">🎓 Postgraduate</option>
          </select>

          <div className="opp-result-count">
            {filteredOpps.length} {filteredOpps.length === 1 ? 'result' : 'results'}
          </div>
        </div>
      </div>

      {/* ─── Error State ─── */}
      {error && (
        <div className="opp-error">
          <p>{error}</p>
        </div>
      )}

      {/* ─── Loading State ─── */}
      {loading ? (
        <div className="opp-loading">
          <div className="opp-loading-spinner" />
          <p>Fetching opportunities...</p>
        </div>
      ) : filteredOpps.length === 0 ? (
        <div className="opp-empty">
          <Trophy size={48} strokeWidth={1.5} />
          <h3>No opportunities found</h3>
          <p>Try adjusting your filters or search query</p>
        </div>
      ) : (
        <div className="opp-grid">
          {filteredOpps.map((opp, index) => {
            const config = TYPE_CONFIG[opp.type] || TYPE_CONFIG.hackathon;
            const urgency = getDeadlineUrgency(opp.days_left);
            const isLive = opp.tags?.includes('live');

            return (
              <div key={opp.id || index} className="opp-card" style={{ '--accent': config.color, '--accent-bg': config.bg, '--accent-border': config.border }}>
                {/* Rank Number */}
                <div className="opp-rank">#{String(index + 1).padStart(2, '0')}</div>

                {/* Card Header */}
                <div className="opp-card-header">
                  <OrgAvatar name={opp.organizer} type={opp.type} />
                  <div className="opp-card-header-text">
                    <h3 className="opp-card-title">{opp.title}</h3>
                    <p className="opp-card-org">{opp.organizer}</p>
                  </div>
                  <div className="opp-card-badges">
                    <span className="opp-type-badge" style={{ background: config.bg, color: config.color, borderColor: config.border }}>
                      {config.icon} {config.label}
                    </span>
                    {isLive && (
                      <span className="opp-live-badge">
                        <span className="opp-live-dot" /> LIVE
                      </span>
                    )}
                  </div>
                </div>

                {/* Description */}
                <p className="opp-card-desc">
                  {opp.description && opp.description !== "Live scraped hackathon opportunity." && opp.description !== "Live opportunity — click Apply to learn more."
                    ? opp.description
                    : "An exciting opportunity to showcase your skills and compete with top talent. Click apply to learn more."}
                </p>

                {/* Skills */}
                <div className="opp-skill-tags">
                  {(opp.skills || []).slice(0, 4).map(s => (
                    <span key={s} className="opp-skill-tag">{s}</span>
                  ))}
                  {(opp.skills || []).length > 4 && (
                    <span className="opp-skill-more">+{opp.skills.length - 4}</span>
                  )}
                </div>

                {/* Meta Info Row */}
                <div className="opp-card-meta">
                  <div className="opp-meta-item">
                    <Calendar size={14} />
                    <span>{new Date(opp.deadline).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                  </div>
                  <div className="opp-meta-item">
                    <MapPin size={14} />
                    <span>{opp.location || opp.mode}</span>
                  </div>
                  {opp.team_size && (
                    <div className="opp-meta-item">
                      <Users size={14} />
                      <span>{opp.team_size}</span>
                    </div>
                  )}
                </div>

                {/* Registrations Bar */}
                {opp.registrations && (
                  <div className="opp-reg-bar">
                    <div className="opp-reg-bar-inner">
                      <Users size={12} />
                      <span>{formatNumber(opp.registrations)} registered</span>
                    </div>
                    <div className="opp-reg-progress">
                      <div className="opp-reg-fill" style={{ width: `${Math.min(100, (opp.registrations / 500) * 100)}%` }} />
                    </div>
                  </div>
                )}

                {/* Footer */}
                <div className="opp-card-footer">
                  <div className="opp-prize">
                    <Award size={16} />
                    <span>{opp.prize === "See details" ? "Prizes Inside" : opp.prize}</span>
                  </div>
                  <div className={`opp-countdown ${urgency.class}`}>
                    <Clock size={13} />
                    <span>{urgency.text}</span>
                  </div>
                  <a href={opp.link} target="_blank" rel="noreferrer" className="opp-apply-btn">
                    Apply Now <ExternalLink size={14} />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
