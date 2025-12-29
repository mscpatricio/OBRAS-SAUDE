import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import HospitalList from './components/HospitalList';
import AIAudit from './components/AIAudit';
import Reports from './components/Reports';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'hospitals':
        return <HospitalList />;
      case 'audit':
        return <AIAudit />;
      case 'reports':
        return <Reports />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 ml-64 p-8 overflow-y-auto h-screen">
        {renderContent()}
      </main>
    </div>
  );
};

export default App;