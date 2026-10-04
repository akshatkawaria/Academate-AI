import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE, timeout: 60000 });

// Very simple request cache to prevent infinite loops / redundant calls
const cache = new Map();
const CACHE_TTL = 30000; // 30 seconds

const cachedGet = async (url, config = {}) => {
  const key = url + JSON.stringify(config.params || {});
  const now = Date.now();
  if (cache.has(key)) {
    const { data, timestamp } = cache.get(key);
    if (now - timestamp < CACHE_TTL) return data;
  }
  const res = await api.get(url, config);
  cache.set(key, { data: res, timestamp: now });
  return res;
};

// Bust a specific cache key (call after any write that should invalidate a GET)
export const bustCache = (urlFragment) => {
  for (const key of cache.keys()) {
    if (key.includes(urlFragment)) cache.delete(key);
  }
};

// ── Profile ──────────────────────────────────────────
export const createProfile   = (data)     => api.post('/api/profile/', data);
export const getProfile      = (uid)      => cachedGet(`/api/profile/${uid}`);
export const updateProfile   = (uid, data)=> api.put(`/api/profile/${uid}`, data);

// ── Schedule & Planner ──────────────────────────────────
export const generateSchedule = async (uid, date) => {
  const res = await api.post(`/api/schedule/generate`, { user_id: uid, date });
  bustCache(`/api/schedule/${uid}`);
  return res;
};
export const getSchedule     = (uid, date)=> cachedGet(`/api/schedule/${uid}`, { params: { date_filter: date } });
export const updateTask      = async (sid, done) => {
  const res = await api.patch(`/api/schedule/${sid}`, { status: done ? "completed" : "pending" });
  bustCache(`/api/schedule`);
  return res;
};
export const generateAdvancedPlan = async (uid, data) => {
  const res = await api.post(`/api/planner/generate?user_id=${uid}`, data);
  bustCache(`/api/schedule/${uid}`);
  return res;
};

// ── Progress ─────────────────────────────────────────
export const logProgress     = (data)     => api.post(`/api/progress/${data.user_id}`, data);
export const getProgress     = (uid, days)=> cachedGet(`/api/progress/${uid}`, { params: { days } });
export const getAnalytics    = (uid)      => api.get(`/api/progress/analytics/${uid}`);
export const getTodayTasks   = (uid)      => api.get(`/api/progress/today-tasks/${uid}`);
export const autoLogProgress = (uid)      => api.post(`/api/progress/auto-log/${uid}`);

// ── Recommendations ───────────────────────────────────
export const getRecommendations = (uid)   => cachedGet(`/api/recommendations/${uid}`);

// ── Opportunities ─────────────────────────────────────
export const getOpportunities = (params)  => cachedGet('/api/opportunities/', { params });
export const getFeatured      = ()        => cachedGet('/api/opportunities/featured');

// ── Notifications ─────────────────────────────────────
export const getNotifications = (uid)     => cachedGet(`/api/notifications/${uid}`);
export const markRead         = (nid)     => api.patch(`/api/notifications/${nid}/read`);
export const getAdaptiveMode  = (uid)     => cachedGet(`/api/notifications/adaptive/${uid}`);

// ── Placement Agent ────────────────────────────────────
export const getSkills             = ()                => cachedGet('/api/placement/skills');
export const getSkillDetail        = (slug)            => cachedGet(`/api/placement/skills/${slug}`);
// Progress must NEVER be cached — it changes on every step toggle
export const getPlacementProgress  = (uid)             => api.get(`/api/placement/progress/${uid}`);
export const updateSkillProgress   = async (uid, slug, data) => {
  const res = await api.post(`/api/placement/progress/${uid}/${slug}`, data);
  bustCache(`/api/placement/progress/${uid}`);
  bustCache(`/api/placement/readiness/${uid}`);
  bustCache(`/api/placement/dashboard/${uid}`);
  return res;
};
export const getReadiness          = (uid)             => api.get(`/api/placement/readiness/${uid}`);
export const generateLearningPath  = (data)            => api.post('/api/placement/learning-path', data);
export const getPlacementDashboard = (uid)             => api.get(`/api/placement/dashboard/${uid}`);

// ── Dashboard Intelligence ─────────────────────────────
export const getDashboardFull          = (uid) => api.get(`/api/dashboard/full/${uid}`);
export const getDashboardNotifications = (uid) => api.get(`/api/dashboard/notifications/${uid}`);
export const getDashboardPlacement     = (uid) => api.get(`/api/dashboard/placement-summary/${uid}`);
export const getDashboardRecs          = (uid) => api.get(`/api/dashboard/recommendations/${uid}`);

export default api;
