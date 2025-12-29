import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BedDouble, Activity, HardHat, TrendingUp, ArrowUpRight, PlusCircle, HeartPulse, Stethoscope, Mic, Sparkles, Loader2, CheckCircle2 } from 'lucide-react';
import StatsCard from './StatsCard';
import { hospitalsData, getConsolidatedStats } from '../services/data';
import { generateGovernorBriefing } from '../services/geminiService';

const Dashboard: React.FC = () => {
  const stats = getConsolidatedStats();
  const [briefing, setBriefing] = useState<string | null>(null);
  const [isBriefingLoading, setIsBriefingLoading] = useState(false);

  // Extract expansion number helper
  const getExpansionNum = (str: string | undefined) => {
    if (!str) return 0;
    const nums = str.match(/\d+/g);
    return nums ? Math.max(...nums.map(n => parseInt(n))) : 0;
  };

  // Filter for top 8 hospitals by capacity
  const chartData = hospitalsData
    .filter(h => h.totalBedsCurrent > 20 && h.id !== 'hes_history')
    .map(h => ({
      name: h.acronym,
      'Atual': h.totalBedsCurrent,
      'Ampliação': getExpansionNum(h.plannedExpansion)
    }))
    .sort((a, b) => b.Atual - a.Atual);

  // Calculate total ICU and Operating Rooms from raw string data
  const totalICU = hospitalsData.reduce((acc, h) => {
    if (h.id === 'hes_history' || !h.icuBeds) return acc;
    // Extract numbers from "10 - 18" (take max) or "15" or "03 SV"
    const nums = h.icuBeds.match(/\d+/g);
    if (nums) {
       // Sum the last number found (usually the total capacity in ranges like "10-18" or just "15")
       return acc + parseInt(nums[nums.length - 1]);
    }
    return acc;
  }, 0);

  const totalOR = hospitalsData.reduce((acc, h) => acc + (h.operatingRooms || 0), 0);

  const handleGenerateBriefing = async () => {
    setIsBriefingLoading(true);
    const text = await generateGovernorBriefing();
    setBriefing(text);
    setIsBriefingLoading(false);
  };

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      <div className="flex justify-between items-center">
        <div>
           <h2 className="text-2xl font-bold text-slate-800">Painel de Controle Estratégico</h2>
           <p className="text-sm text-slate-500">Monitoramento da rede em tempo real.</p>
        </div>
        <div className="flex flex-col items-end">
             <span className="flex items-center gap-2 text-xs bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full font-bold border border-emerald-100 shadow-sm">
              <CheckCircle2 size={12} />
              Total Auditado (Real): {stats.totalBeds.toLocaleString('pt-BR')} Leitos
            </span>
             <span className="text-[10px] text-slate-400 mt-1">
              *Superior ao Quadro Resumo (1.463) devido atualizações HCA/HES
            </span>
        </div>
      </div>

      {/* Governor's Briefing Widget (Gemini 3 Pro) */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl shadow-lg p-6 text-white relative overflow-hidden border border-slate-700">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
            <Mic size={150} />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row gap-6">
            <div className="flex-shrink-0 md:w-1/3">
                <h3 className="text-xl font-bold flex items-center gap-2 mb-2">
                    <Sparkles className="text-amber-400" size={20} />
                    Briefing do Governador
                </h3>
                <p className="text-slate-300 text-sm mb-4 leading-relaxed">
                    Resumo executivo gerado por <strong>IA (Gemini 3 Pro)</strong> para utilização imediata em entrevistas, coletivas de imprensa ou rádio. Foca em dados positivos e expansão.
                </p>
                <button
                    onClick={handleGenerateBriefing}
                    disabled={isBriefingLoading}
                    className="w-full md:w-auto bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                >
                    {isBriefingLoading ? (
                        <>
                           <Loader2 className="animate-spin" size={16} />
                           Gerando Pauta...
                        </>
                    ) : (
                        <>
                           <Mic size={16} />
                           Gerar Discurso
                        </>
                    )}
                </button>
            </div>
            
            <div className="flex-1 bg-white/5 rounded-lg border border-white/10 p-4 min-h-[120px] flex items-center justify-center relative">
                {briefing ? (
                    <div className="text-left w-full animate-fade-in">
                        <div className="flex justify-between items-start mb-2">
                             <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Sugestão de Fala</span>
                             <button onClick={() => setBriefing(null)} className="text-xs text-slate-400 hover:text-white transition-colors">Limpar</button>
                        </div>
                        <p className="text-lg font-medium text-slate-100 font-serif italic leading-relaxed whitespace-pre-line">
                            "{briefing}"
                        </p>
                    </div>
                ) : (
                    <div className="text-center text-slate-400">
                        {isBriefingLoading ? (
                            <p className="animate-pulse">Consultando dados estratégicos...</p>
                        ) : (
                            <div className="flex flex-col items-center gap-2 opacity-50">
                                <Activity size={24} />
                                <p className="text-sm">Clique em "Gerar Discurso" para criar a pauta.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
      </div>

      {/* Primary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="Total de Leitos (Real)" 
          value={stats.totalBeds} 
          icon={BedDouble} 
          color="blue"
          trend="Dados Auditados (2025)"
        />
        <StatsCard 
          title="Ampliação Prevista" 
          value={stats.totalPlannedExpansion} 
          icon={ArrowUpRight} 
          color="green"
          trend="Novos Leitos em Planejamento"
        />
        <StatsCard 
          title="Leitos UTI / NED" 
          value={totalICU} 
          icon={HeartPulse} 
          color="purple"
          trend="Alta Complexidade"
        />
        <StatsCard 
          title="Salas Cirúrgicas" 
          value={totalOR} 
          icon={Stethoscope} 
          color="orange"
          trend="Capacidade Operatória"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-100">
          <div className="flex justify-between items-center mb-6">
             <h3 className="text-lg font-semibold text-slate-800">Capacidade Atual vs. Ampliação Planejada</h3>
             <TrendingUp size={20} className="text-blue-500" />
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} interval={0} fontSize={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b' }} />
                <Tooltip 
                  cursor={{ fill: '#f1f5f9' }}
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }}/>
                <Bar dataKey="Atual" fill="#3b82f6" name="Leitos Atuais" radius={[4, 4, 0, 0]} barSize={30} />
                <Bar dataKey="Ampliação" fill="#10b981" name="Ampliação (Prevista)" radius={[4, 4, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Expansions Panel */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">Maiores Expansões (Top 5)</h3>
          <div className="space-y-4 flex-1 overflow-y-auto">
            {chartData
                .filter(d => d.Ampliação > 0)
                .sort((a, b) => b.Ampliação - a.Ampliação)
                .slice(0, 5)
                .map((item, idx) => (
                    <div key={idx} className="p-4 bg-slate-50 rounded-lg border border-slate-100">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="font-bold text-slate-700">{item.name}</h4>
                                <p className="text-xs text-slate-500">Projeto de Expansão</p>
                            </div>
                            <span className="text-green-600 font-bold text-sm bg-green-100 px-2 py-1 rounded-full">+{item.Ampliação}</span>
                        </div>
                        <div className="mt-3 flex items-center text-xs text-slate-600">
                            <PlusCircle size={14} className="mr-1 text-green-500"/>
                            <span>Adição de leitos planejada</span>
                        </div>
                    </div>
                ))
            }
          </div>
        </div>
      </div>

      {/* Summary Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
          <div className="p-6 border-b border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800">Quadro Resumo de Metas (Unidades com Expansão)</h3>
          </div>
          <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 text-slate-600 font-medium">
                      <tr>
                          <th className="px-6 py-4">Unidade</th>
                          <th className="px-6 py-4 text-center">Leitos Atuais</th>
                          <th className="px-6 py-4 text-center">Ampliação</th>
                          <th className="px-6 py-4 text-center">Total Futuro</th>
                          <th className="px-6 py-4 text-center">Crescimento</th>
                      </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                      {hospitalsData
                        .filter(h => h.plannedExpansion && h.id !== 'hes_history')
                        .slice(0, 8)
                        .map((h) => {
                          const expansion = getExpansionNum(h.plannedExpansion);
                          const total = h.totalBedsCurrent + expansion;
                          // Avoid division by zero
                          const growthPercent = h.totalBedsCurrent > 0 
                            ? ((expansion / h.totalBedsCurrent) * 100).toFixed(0) 
                            : 'N/A';
                          
                          return (
                            <tr key={h.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-800">
                                    {h.name} ({h.acronym})
                                </td>
                                <td className="px-6 py-4 text-center text-slate-600">
                                    {h.totalBedsCurrent}
                                </td>
                                <td className="px-6 py-4 text-center text-green-600 font-medium">
                                    +{expansion}
                                </td>
                                <td className="px-6 py-4 text-center font-bold text-blue-600">
                                    {total}
                                </td>
                                <td className="px-6 py-4 text-center">
                                     <div className="flex items-center justify-center space-x-2">
                                        <div className="w-16 h-2 bg-slate-200 rounded-full overflow-hidden">
                                            <div className="h-full bg-green-500" style={{ width: growthPercent === 'N/A' ? '100%' : `${Math.min(parseInt(growthPercent), 100)}%` }}></div>
                                        </div>
                                        <span className="text-xs font-medium text-green-600">{growthPercent}%</span>
                                     </div>
                                </td>
                            </tr>
                          )
                      })}
                  </tbody>
              </table>
          </div>
      </div>
    </div>
  );
};

export default Dashboard;