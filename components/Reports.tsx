import React, { useRef, useState } from 'react';
import { Download, Printer, Building2, Activity, FileType, CheckCircle2, Clock, Hammer, History, ArrowRight, FileText, TrendingUp, AlertCircle, CalendarClock } from 'lucide-react';
import { hospitalsData } from '../services/data';

const Reports: React.FC = () => {
  const currentDate = new Date().toLocaleDateString('pt-BR');
  const reportRef = useRef<HTMLDivElement>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Clean data for reporting
  const cleanUnits = hospitalsData
    .filter(h => h.id !== 'hes_history')
    .map(h => ({
      ...h,
      plannedExpansionRaw: h.plannedExpansion?.replace('?', '') || '',
      expansionVal: (() => {
         if (!h.plannedExpansion) return 0;
         const nums = h.plannedExpansion.match(/\d+/g);
         return nums ? Math.max(...nums.map(n => parseInt(n))) : 0;
      })()
    }))
    // Sort for report: Largest/Strategic first, then by expansion
    .sort((a, b) => {
        // Priority for HCAL, HCA, HES, HMML, HEOC
        const priorities = ['HCAL', 'HES', 'HCA', 'HMML', 'HEOC'];
        const pA = priorities.indexOf(a.acronym);
        const pB = priorities.indexOf(b.acronym);
        
        if (pA !== -1 && pB !== -1) return pA - pB;
        if (pA !== -1) return -1;
        if (pB !== -1) return 1;

        return b.totalBedsCurrent - a.totalBedsCurrent;
    });

  const totalBeds = cleanUnits.reduce((acc, h) => acc + h.totalBedsCurrent, 0);
  const totalBeds2023 = cleanUnits.reduce((acc, h) => acc + (h.totalBeds2023 || 0), 0);
  const totalExpansion = cleanUnits.reduce((acc, h) => acc + h.expansionVal, 0);
  
  // Logic to separate works
  const deliveredWorks = hospitalsData.flatMap(h => 
    h.works.filter(w => w.status === 'Entregue' || w.status === 'Revitalizado')
    .map(w => ({ ...w, hospitalName: h.acronym }))
  );

  const pendingWorks = hospitalsData.flatMap(h => 
    h.works.filter(w => w.status === 'Em Andamento' || w.status === 'Previsto')
    .map(w => ({ ...w, hospitalName: h.acronym }))
  );

  const handleDownloadPDF = async () => {
    if (!reportRef.current) {
        alert("Erro: Container do relatório não encontrado.");
        return;
    }
    
    // @ts-ignore
    if (typeof window.html2pdf === 'undefined') {
        alert("Biblioteca PDF ainda carregando. Tente novamente em alguns segundos.");
        return;
    }

    setIsGenerating(true);
    
    const element = reportRef.current;
    const opt = {
      margin: [10, 10, 10, 10], // top, left, bottom, right (mm)
      filename: `Parecer_Tecnico_SESA_${new Date().toISOString().split('T')[0]}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
          scale: 2, 
          useCORS: true,
          logging: false
      },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
      // @ts-ignore
      await window.html2pdf().set(opt).from(element).save();
    } catch (error) {
      console.error("PDF generation failed:", error);
      alert("Erro ao gerar PDF. Verifique o console para detalhes ou use a opção de Impressão (Ctrl+P).");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadDOCX = () => {
    if (!reportRef.current) {
        alert("Erro: Conteúdo não disponível para exportação.");
        return;
    }

    try {
        const header = `
          <html xmlns:o='urn:schemas-microsoft-com:office:office' 
                xmlns:w='urn:schemas-microsoft-com:office:word' 
                xmlns='http://www.w3.org/TR/REC-html40'>
          <head>
            <meta charset='utf-8'>
            <title>Relatório SESA</title>
            <style>
              body { font-family: 'Arial', sans-serif; font-size: 11pt; color: #000; }
              table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
              th { background-color: #f3f4f6; font-weight: bold; border: 1px solid #999; padding: 8px; text-align: left; }
              td { border: 1px solid #999; padding: 8px; }
            </style>
          </head>
          <body>
        `;
        
        const content = reportRef.current.innerHTML;
        const footer = "</body></html>";
        
        const sourceHTML = header + content + footer;

        const blob = new Blob(['\ufeff', sourceHTML], { type: 'application/msword' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Parecer_Tecnico_SESA_${new Date().toISOString().split('T')[0]}.doc`; 
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        }, 100);

    } catch (e) {
        console.error(e);
        alert("Erro ao gerar arquivo DOC.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in pb-10">
       {/* Toolbar */}
       <div className="flex justify-between items-center mb-6 no-print">
        <div>
          <h2 className="text-2xl font-bold text-slate-800">Relatórios & Pareceres</h2>
          <p className="text-slate-500 text-sm">Auditoria consolidada da rede estadual de saúde.</p>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => window.print()} 
            className="flex items-center space-x-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 text-sm transition-colors"
          >
            <Printer size={16} />
            <span className="hidden sm:inline">Imprimir</span>
          </button>
          
          <button 
            onClick={handleDownloadDOCX}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-50 border border-blue-200 text-blue-700 rounded-lg hover:bg-blue-100 text-sm transition-colors shadow-sm"
          >
            <FileType size={16} />
            <span className="hidden sm:inline">Baixar DOCX</span>
          </button>

          <button 
            onClick={handleDownloadPDF}
            disabled={isGenerating}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <span className="flex items-center gap-2">Gerando...</span>
            ) : (
              <>
                <Download size={16} />
                <span className="hidden sm:inline">Baixar PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div id="report-container" ref={reportRef} className="bg-white p-12 rounded-xl shadow-lg border border-slate-200 min-h-[1000px] relative print:shadow-none print:border-none print:p-0">
        {/* Header - Official Look */}
         <div className="border-b-2 border-slate-800 pb-6 mb-8 flex justify-between items-end">
            <div className="flex items-center gap-4">
                <div className="w-20 h-20 bg-slate-900 text-white flex items-center justify-center rounded-lg print:border print:border-slate-900">
                    <Building2 size={40} />
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 uppercase tracking-tight">Parecer Técnico Consolidado</h1>
                    <p className="text-sm font-medium text-slate-600 uppercase">Secretaria de Estado da Saúde (SESA) - Gestão de Contratos</p>
                    <p className="text-xs text-slate-500 mt-1">Referência: Quadro Geral de Obras e Leitos (2025)</p>
                </div>
            </div>
            <div className="text-right">
                <p className="text-sm font-bold text-slate-900">RELATÓRIO Nº 2025/001</p>
                <p className="text-xs text-slate-500">{currentDate}</p>
            </div>
         </div>

         {/* Sections 1-4 condensed for brevity in file updates, but structure remains */}
         <div className="mb-8">
            <h3 className="text-sm font-bold text-slate-900 uppercase border-b border-slate-200 pb-2 mb-4 flex items-center gap-2">
                1. Contextualização da Rede
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed text-justify mb-4">
                A rede auditada compõe-se de <strong>{cleanUnits.length} unidades</strong>, totalizando <strong>{totalBeds} leitos operacionais</strong>. 
                O plano de expansão prevê um incremento de aproximadamente <strong>{totalExpansion} novos leitos</strong>, com entregas substanciais programadas para o ciclo de 2026.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Note about 1463 vs 1574 */}
                <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg flex items-start gap-3 print:border-black print:bg-white">
                    <AlertCircle size={16} className="text-yellow-600 mt-0.5 print:text-black" />
                    <div>
                        <h4 className="text-xs font-bold text-yellow-800 uppercase print:text-black">Nota Técnica de Auditoria</h4>
                        <p className="text-xs text-yellow-700 print:text-black">
                            O total atual de <strong>{totalBeds} leitos</strong> supera o registro do Quadro Resumo anterior (1.463), refletindo a atualização em tempo real das entregas recentes (HCA/HES).
                        </p>
                    </div>
                </div>

                {/* Note about 2026 Deliveries */}
                <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg flex items-start gap-3 print:border-black print:bg-white">
                    <CalendarClock size={16} className="text-blue-600 mt-0.5 print:text-black" />
                    <div>
                        <h4 className="text-xs font-bold text-blue-800 uppercase print:text-black">Previsão de Entrega (2026)</h4>
                        <p className="text-xs text-blue-700 print:text-black">
                            As obras estruturantes do <strong>Novo HE</strong> e expansões do <strong>HCA/HEOC</strong> estão com cronograma confirmado para entrega no exercício de 2026.
                        </p>
                    </div>
                </div>
            </div>
         </div>

         {/* Section 5: Consolidated Table */}
         <div className="mb-8 page-break-inside-avoid">
            <h3 className="text-sm font-bold text-slate-900 uppercase border-b border-slate-200 pb-2 mb-4">
                2. Quadro Resumo Consolidado (Auditado em Tempo Real)
            </h3>
            <div className="overflow-hidden border border-slate-200 rounded-lg print:border-black">
                <table className="min-w-full text-xs">
                    <thead className="bg-slate-100 text-slate-700 font-semibold uppercase print:bg-slate-200 print:text-black">
                        <tr>
                            <th className="px-4 py-3 text-left w-1/4">Unidade</th>
                            <th className="px-4 py-3 text-center w-1/12">Tipo</th>
                            <th className="px-4 py-3 text-right bg-slate-200/50">Base 2023</th>
                            <th className="px-4 py-3 text-right font-bold text-blue-900 bg-blue-50">Leitos 2025</th>
                            <th className="px-4 py-3 text-right text-green-800 bg-green-50">Ampliação (Ciclo 2026)</th>
                            <th className="px-4 py-3 text-right w-1/4">Status Obras</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white print:divide-black">
                        {cleanUnits.map((u, idx) => (
                            <tr key={u.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50 print:bg-white'}>
                                <td className="px-4 py-2 font-medium text-slate-800">{u.name}</td>
                                <td className="px-4 py-2 text-center text-slate-500">
                                    {u.acronym.includes('HPP') ? 'HPP' : u.acronym.includes('UPA') ? 'UPA' : 'HOSPITAL'}
                                </td>
                                <td className="px-4 py-2 text-right text-slate-500 bg-slate-50/50">
                                    {u.totalBeds2023 ? u.totalBeds2023 : '-'}
                                </td>
                                <td className="px-4 py-2 text-right font-bold text-blue-700 bg-blue-50/30">
                                    {u.totalBedsCurrent}
                                    {u.totalBeds2023 && u.totalBedsCurrent > u.totalBeds2023 && (
                                        <span className="ml-1 text-[9px] text-green-600 align-top">▲</span>
                                    )}
                                </td>
                                <td className="px-4 py-2 text-right text-green-600 font-medium bg-green-50/30 print:text-black">
                                    {u.expansionVal > 0 ? `+${u.expansionVal}` : '-'}
                                </td>
                                <td className="px-4 py-2 text-right text-slate-500">
                                    {u.works.length > 0 ? (
                                        <div className="flex flex-col gap-1 items-end">
                                            {u.works.slice(0, 2).map((w, i) => (
                                                <span key={i} className="text-[10px]">
                                                    {w.status}
                                                    {w.completionDate && w.completionDate.includes('2026') && (
                                                        <span className="text-blue-600 font-bold ml-1">(2026)</span>
                                                    )}
                                                </span>
                                            ))}
                                            {u.works.length > 2 && <span className="text-[9px] italic">+{u.works.length - 2} contratos</span>}
                                        </div>
                                    ) : '-'}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot className="bg-slate-100 font-bold text-slate-800 print:bg-slate-200 print:text-black">
                        <tr>
                            <td colSpan={2} className="px-4 py-3 text-right uppercase">Total Geral da Rede</td>
                            <td className="px-4 py-3 text-right text-slate-600">{totalBeds2023}</td>
                            <td className="px-4 py-3 text-right text-blue-800">{totalBeds}</td>
                            <td className="px-4 py-3 text-right text-green-700 print:text-black">+{totalExpansion}</td>
                            <td className="px-4 py-3"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
         </div>

         {/* Section 6: Full Evolution Matrix */}
         <div className="mt-8 page-break-inside-avoid">
            <h3 className="text-sm font-bold text-slate-900 uppercase border-b border-slate-200 pb-2 mb-6 flex items-center gap-2">
                3. Matriz de Evolução Completa (Rede Integral)
            </h3>
            
            <div className="grid grid-cols-1 gap-8">
                {/* Evolution Cards for ALL Hospitals */}
                {cleanUnits.map((hospital) => {
                    return (
                        <div key={hospital.id} className="border border-slate-300 rounded-lg overflow-hidden print:border-black break-inside-avoid">
                            <div className="bg-slate-100 px-4 py-3 border-b border-slate-300 font-bold text-slate-800 flex justify-between items-center print:bg-slate-200 print:border-black">
                                <span className="text-base">{hospital.name} ({hospital.acronym})</span>
                                <span className="text-[10px] bg-white px-2 py-1 rounded text-slate-600 border border-slate-200 uppercase print:border-black">
                                    {hospital.acronym.includes('HPP') ? 'Unidade Interior' : 'Unidade Estratégica'}
                                </span>
                            </div>
                            
                            <div className="grid grid-cols-3 divide-x divide-slate-200 print:divide-black">
                                {/* Past */}
                                <div className="p-4 bg-slate-50 print:bg-white">
                                    <div className="flex items-center gap-2 mb-3 text-slate-500">
                                        <History size={16} />
                                        <span className="text-xs font-bold uppercase">Cenário Base (2023)</span>
                                    </div>
                                    <p className="text-sm font-medium text-slate-700">
                                        {hospital.totalBeds2023 ? `${hospital.totalBeds2023} Leitos Operacionais` : 'Dados não consolidados'}
                                    </p>
                                    <p className="text-xs text-slate-500 mt-2 leading-tight">
                                        {hospital.totalBeds2023 ? "Base do início da gestão atual." : "Período anterior à intervenção."}
                                    </p>
                                </div>
                                
                                {/* Present */}
                                <div className="p-4 bg-white">
                                    <div className="flex items-center gap-2 mb-3 text-blue-600">
                                        <Activity size={16} />
                                        <span className="text-xs font-bold uppercase">Situação Atual (2025)</span>
                                    </div>
                                    <div className="flex items-baseline gap-2 mb-1">
                                         <p className="text-xl font-bold text-slate-800">
                                            {hospital.totalBedsCurrent} Leitos
                                        </p>
                                        {hospital.totalBeds2023 && hospital.totalBedsCurrent > hospital.totalBeds2023 && (
                                            <span className="text-xs font-bold text-green-600 bg-green-50 px-2 rounded-full border border-green-100">
                                                +{hospital.totalBedsCurrent - hospital.totalBeds2023} Leitos
                                            </span>
                                        )}
                                    </div>
                                   
                                    <div className="mt-3">
                                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Status:</span>
                                        <ul className="text-xs text-slate-600 space-y-1 list-disc pl-3 mt-1">
                                            {hospital.works
                                                .filter(w => w.status === 'Entregue' || w.status === 'Revitalizado')
                                                .slice(0, 3)
                                                .map((w, i) => (
                                                    <li key={i}>{w.title}</li>
                                                ))}
                                            {hospital.works.filter(w => w.status === 'Entregue' || w.status === 'Revitalizado').length === 0 && (
                                                <li className="italic text-slate-400">Em plena operação.</li>
                                            )}
                                        </ul>
                                    </div>
                                </div>

                                {/* Future */}
                                <div className="p-4 bg-blue-50/30 print:bg-white">
                                    <div className="flex items-center gap-2 mb-3 text-green-600">
                                        <ArrowRight size={16} />
                                        <span className="text-xs font-bold uppercase">Projeção (Ciclo 2026)</span>
                                    </div>
                                    <p className="text-sm font-medium text-slate-700 mb-1">
                                        Meta: {hospital.totalBedsCurrent + hospital.expansionVal} Leitos
                                    </p>
                                    {hospital.expansionVal > 0 && (
                                         <span className="inline-block bg-green-100 text-green-700 text-[10px] px-2 py-0.5 rounded-full font-bold mb-3 border border-green-200">
                                            +{hospital.expansionVal} Novos Leitos
                                         </span>
                                    )}
                                    
                                    <ul className="text-xs text-slate-600 space-y-1 list-disc pl-3">
                                        {hospital.works
                                            .filter(w => w.status === 'Em Andamento' || w.status === 'Previsto')
                                            .slice(0, 3)
                                            .map((w, i) => (
                                                <li key={i}>
                                                    {w.title}
                                                    {w.completionDate && w.completionDate.includes('2026') && (
                                                        <span className="text-blue-700 font-bold ml-1">[2026]</span>
                                                    )}
                                                </li>
                                            ))}
                                         {hospital.plannedExpansionRaw && !hospital.works.some(w => w.status === 'Previsto') && (
                                            <li>Projeto de Expansão ({hospital.plannedExpansionRaw})</li>
                                         )}
                                    </ul>
                                </div>
                            </div>

                            {/* Deep Analysis Text Row */}
                            {hospital.analysis ? (
                                <div className="p-4 bg-slate-50 border-t border-slate-200 print:bg-white print:border-slate-300">
                                    <div className="flex gap-2">
                                        <FileText size={14} className="text-slate-400 mt-0.5 flex-shrink-0" />
                                        <div>
                                            <h5 className="text-[10px] font-bold uppercase text-slate-500 mb-1">Análise Técnica</h5>
                                            <p className="text-sm text-slate-700 leading-relaxed text-justify">
                                                {hospital.analysis}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ) : null}
                        </div>
                    );
                })}
            </div>
         </div>

         {/* Footer Signature */}
         <div className="mt-20 flex justify-between items-center pt-8 border-t border-slate-300 print:border-black">
             <div className="text-xs text-slate-400 print:text-black">
                 <p>Documento gerado eletronicamente.</p>
                 <p>SESA - Sistema de Gestão de Contratos</p>
             </div>
             <div className="text-center">
                 <div className="h-px w-64 bg-slate-400 mb-2 print:bg-black"></div>
                 <p className="text-xs font-bold text-slate-700 uppercase print:text-black">Responsável Técnico</p>
                 <p className="text-[10px] text-slate-500 print:text-black">Auditoria & Planejamento</p>
             </div>
         </div>
      </div>
    </div>
  );
};

export default Reports;