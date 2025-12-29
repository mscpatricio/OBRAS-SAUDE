import React from 'react';
import { LayoutDashboard, Building2, FileText, BrainCircuit, PieChart } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'hospitals', label: 'Unidades Hospitalares', icon: Building2 },
    { id: 'audit', label: 'Auditoria IA', icon: BrainCircuit },
    { id: 'reports', label: 'Relatórios & Pareceres', icon: FileText },
  ];

  return (
    <div className="w-64 bg-slate-900 text-white h-screen fixed left-0 top-0 flex flex-col shadow-xl z-10">
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
          SESA Gestão
        </h1>
        <p className="text-xs text-slate-400 mt-1">Sistema Integrado de Contratos</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' 
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center space-x-3 p-3 bg-slate-800 rounded-lg">
          <div className="w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center text-xs font-bold">
            GOV
          </div>
          <div>
            <p className="text-sm font-medium">Usuário Admin</p>
            <p className="text-xs text-slate-400">Secretaria de Saúde</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;