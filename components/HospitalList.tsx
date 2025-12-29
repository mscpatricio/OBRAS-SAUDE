import React, { useState } from 'react';
import { hospitalsData } from '../services/data';
import { ChevronDown, ChevronUp, Bed, Hammer, Activity, HeartPulse, ArrowUpRight } from 'lucide-react';

const HospitalList: React.FC = () => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  // Calculate totals dynamically from data
  const totalBeds = hospitalsData.reduce((acc, h) => acc + h.totalBedsCurrent, 0);
  const totalOR = hospitalsData.reduce((acc, h) => acc + (h.operatingRooms || 0), 0);
  
  const totalICU = hospitalsData.reduce((acc, h) => {
    if (!h.icuBeds) return acc;
    const nums = h.icuBeds.match(/\d+/g);
    // Take the last number in string (e.g. "10-18" -> 18)
    return nums ? acc + parseInt(nums[nums.length - 1]) : acc;
  }, 0);

  const totalExpansion = hospitalsData.reduce((acc, h) => {
    if (!h.plannedExpansion) return acc;
    const nums = h.plannedExpansion.match(/\d+/g);
    return nums ? acc + Math.max(...nums.map(n => parseInt(n))) : acc;
  }, 0);

  return (
    <div className="space-y-6 animate-fade-in">
       <div className="flex justify-between items-center">
        <div>
            <h2 className="text-2xl font-bold text-slate-800">Rede Hospitalar</h2>
            <p className="text-sm text-slate-500">Listagem oficial conforme quadro de leitos e ampliação.</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors shadow-sm">
          + Inserir Unidade
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Table Header for Desktop */}
        <div className="hidden md:grid grid-cols-12 gap-4 p-4 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <div className="col-span-4">Unidade Hospitalar</div>
            <div className="col-span-2 text-center">Leitos Totais</div>
            <div className="col-span-2 text-center">UTI / NED</div>
            <div className="col-span-2 text-center">Salas Cir.</div>
            <div className="col-span-2 text-center">Ampliação</div>
        </div>

        <div className="divide-y divide-slate-100">
        {hospitalsData.map((hospital) => (
          <div key={hospital.id} className="hover:bg-slate-50 transition-colors group">
            <div 
              className="p-4 grid grid-cols-1 md:grid-cols-12 gap-4 items-center cursor-pointer"
              onClick={() => toggleExpand(hospital.id)}
            >
              {/* Name Column */}
              <div className="col-span-1 md:col-span-4 flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center text-blue-700 font-bold text-xs flex-shrink-0">
                  {hospital.acronym}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-800 truncate">{hospital.name}</h3>
                  <div className="md:hidden flex space-x-2 text-xs text-slate-500 mt-1">
                     <span>{hospital.totalBedsCurrent} Leitos</span>
                     {hospital.plannedExpansion && <span className="text-green-600">+{hospital.plannedExpansion} Prev.</span>}
                  </div>
                </div>
              </div>

              {/* Data Columns */}
              <div className="hidden md:block col-span-2 text-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                    <Bed size={12} className="mr-1"/> {hospital.totalBedsCurrent}
                  </span>
              </div>
              
              <div className="hidden md:block col-span-2 text-center text-sm text-slate-600">
                  {hospital.icuBeds ? (
                      <span className="flex items-center justify-center text-red-600 bg-red-50 px-2 py-0.5 rounded-full text-xs font-medium">
                          <HeartPulse size={12} className="mr-1"/> {hospital.icuBeds}
                      </span>
                  ) : <span className="text-slate-300">-</span>}
              </div>

              <div className="hidden md:block col-span-2 text-center text-sm text-slate-600">
                  {hospital.operatingRooms ? (
                      <span className="flex items-center justify-center text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full text-xs font-medium">
                          <Activity size={12} className="mr-1"/> {hospital.operatingRooms}
                      </span>
                  ) : <span className="text-slate-300">-</span>}
              </div>

              <div className="hidden md:block col-span-2 text-center">
                  {hospital.plannedExpansion ? (
                      <span className="flex items-center justify-center text-green-700 bg-green-50 px-2 py-0.5 rounded-full text-xs font-bold border border-green-100">
                          <ArrowUpRight size={12} className="mr-1"/> {hospital.plannedExpansion}
                      </span>
                  ) : <span className="text-slate-300">-</span>}
              </div>
            </div>

            {/* Expanded Details */}
            {expandedId === hospital.id && (
              <div className="px-4 pb-4 md:px-14 bg-slate-50 border-t border-slate-100">
                <div className="py-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Detalhes da Unidade</h4>
                        <div className="bg-white p-3 rounded border border-slate-200 space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-500">ID do Sistema:</span>
                                <span className="font-mono text-slate-700">{hospital.id}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-500">Leitos de UTI/NED:</span>
                                <span className="font-medium text-slate-800">{hospital.icuBeds || 'Não informado'}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-500">Salas Cirúrgicas:</span>
                                <span className="font-medium text-slate-800">{hospital.operatingRooms || 0}</span>
                            </div>
                            {hospital.notes && (
                                <div className="mt-2 pt-2 border-t border-slate-100">
                                    <span className="text-xs text-slate-400 italic block">Nota: {hospital.notes}</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div>
                        <h4 className="text-xs font-bold text-slate-500 uppercase mb-2">Contratos e Obras ({hospital.works.length})</h4>
                        {hospital.works.length > 0 ? (
                            <div className="space-y-2">
                                {hospital.works.map((work) => (
                                    <div key={work.id} className="bg-white p-2 rounded border border-slate-200 flex justify-between items-center">
                                        <div className="flex items-center space-x-2">
                                            <Hammer size={14} className="text-slate-400"/>
                                            <span className="text-sm text-slate-700">{work.title}</span>
                                        </div>
                                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                                            work.status === 'Entregue' ? 'bg-green-100 text-green-700' :
                                            work.status === 'Em Andamento' ? 'bg-orange-100 text-orange-700' :
                                            work.status === 'Previsto' ? 'bg-blue-50 text-blue-600' :
                                            'bg-slate-100 text-slate-600'
                                        }`}>
                                            {work.status}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-4 bg-white rounded border border-slate-200 border-dashed">
                                <span className="text-xs text-slate-400">Nenhum contrato ativo vinculado nesta visualização.</span>
                            </div>
                        )}
                    </div>
                </div>
              </div>
            )}
          </div>
        ))}
        </div>
      </div>
      
      <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg flex items-start gap-3">
          <Activity className="text-yellow-600 mt-0.5" size={18} />
          <div>
              <h4 className="text-sm font-bold text-yellow-800">Totalização do Sistema (Calculada)</h4>
              <p className="text-xs text-yellow-700 mt-1">
                  <strong>Total Leitos:</strong> {totalBeds.toLocaleString('pt-BR')} | 
                  <strong> UTI/NED:</strong> {totalICU} | 
                  <strong> Salas Cirúrgicas:</strong> {totalOR} | 
                  <strong> Ampliação Prevista:</strong> +{totalExpansion}
              </p>
          </div>
      </div>
    </div>
  );
};

export default HospitalList;