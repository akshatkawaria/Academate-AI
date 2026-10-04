import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Schedule from './pages/Schedule';
import Progress from './pages/Progress';
import Recommendations from './pages/Recommendations';
import Opportunities from './pages/Opportunities';
import Notifications from './pages/Notifications';
import Setup from './pages/Setup';
import Planner from './pages/Planner';
import Skills from './pages/Skills';
import Placement from './pages/Placement';
import { getProfile, getNotifications } from './api';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  const [uid, setUid] = useState(() => localStorage.getItem('acadmate_uid'));
  const [profile, setProfile] = useState(null);
  const [notifCount, setNotifCount] = useState(0);

  useEffect(() => {
    if (!uid) return;
    getProfile(uid).then(r => setProfile(r.data)).catch(() => {});
    getNotifications(uid).then(r => {
      setNotifCount(r.data.filter(n => !n.read).length);
    }).catch(() => {});
  }, [uid]);

  function handleSetupComplete(newUid) {
    localStorage.setItem('acadmate_uid', newUid);
    setUid(newUid);
  }

  if (!uid) {
    return (
      <>
        <div className="bg-blobs"><div className="blob blob-1"/><div className="blob blob-2"/></div>
        <BrowserRouter>
          <Routes>
            <Route path="*" element={<Setup onComplete={handleSetupComplete}/>}/>
          </Routes>
        </BrowserRouter>
      </>
    );
  }

  return (
    <BrowserRouter>
      <div className="bg-blobs"><div className="blob blob-1"/><div className="blob blob-2"/></div>
      <div className="app-shell">
        <Sidebar profile={profile} notifCount={notifCount}/>
        <main className="main-content">
          <Routes>
            <Route path="/"                element={<ErrorBoundary><Dashboard uid={uid} profile={profile}/></ErrorBoundary>}/>
            <Route path="/schedule"        element={<ErrorBoundary><Schedule uid={uid}/></ErrorBoundary>}/>
            <Route path="/planner"         element={<ErrorBoundary><Planner uid={uid}/></ErrorBoundary>}/>
            <Route path="/placement"        element={<ErrorBoundary><Placement uid={uid}/></ErrorBoundary>}/>
            <Route path="/progress"        element={<ErrorBoundary><Progress uid={uid}/></ErrorBoundary>}/>
            <Route path="/recommendations" element={<ErrorBoundary><Recommendations uid={uid}/></ErrorBoundary>}/>
            <Route path="/opportunities"   element={<ErrorBoundary><Opportunities/></ErrorBoundary>}/>
            <Route path="/skills"           element={<ErrorBoundary><Skills/></ErrorBoundary>}/>
            <Route path="/notifications"   element={<ErrorBoundary><Notifications uid={uid} onRead={() => setNotifCount(c => Math.max(0, c-1))}/></ErrorBoundary>}/>
            <Route path="/setup"           element={<ErrorBoundary><Setup onComplete={handleSetupComplete}/></ErrorBoundary>}/>
            <Route path="*"                element={<Navigate to="/" replace/>}/>
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
