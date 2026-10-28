import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewAuditPage } from './pages/NewAuditPage';
import { AuditProgressPage } from './pages/AuditProgressPage';
import { AuditResultsPage } from './pages/AuditResultsPage';
import { CrawledPagesPage } from './pages/CrawledPagesPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-slate-50 font-sans antialiased text-slate-900">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/audits/new" element={<NewAuditPage />} />
            <Route path="/audits/:id/progress" element={<AuditProgressPage />} />
            <Route path="/audits/:id" element={<AuditResultsPage />} />
            <Route path="/audits/:id/pages" element={<CrawledPagesPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
