import React, { useState } from 'react';
import { generateAuditReport } from '../services/geminiService';
import { Bot, Send, FileOutput, Loader2, BarChart3 } from 'lucide-react';

const AIAudit: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const predefinedQueries = [
    "Análise aprofundada: Evolução do HES (2023 vs Atual)",
    "Relatório de eficiência: Novos leitos entregues por unidade",
    "Quais obras do HES ainda estão em andamento?",
    "Resumo executivo para o Governador (Todas as unidades)"
  ];

  const handleAudit = async (query: string = prompt) => {
    if (!query.trim()) return;
    
    setLoading(true);
    setResponse(null);
    setPrompt(query);
    
    const result = await generateAuditReport(query);
    setResponse(result);
    setLoading(false);
  };

  return (
    <div className="h-[calc(100vh-2rem)] flex flex-col animate-fade-in">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Bot className="text-blue-600" />
          Auditoria Inteligente (IA)
        </h2>
        <p className="text-slate-500">Módulo de inteligência artificial para análise de conformidade e evolução contratual.</p>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0">
        {/* Left Panel: Chat/Input */}
        <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col p-4">
           <div className="flex-1 overflow-y-auto mb-4">
             <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <BarChart3 size={16} />
                Consultas Estratégicas
             </h3>
             <div className="space-y-2">
               {predefinedQueries.map((q, idx) => (
                 <button 
                  key={idx}
                  onClick={() => handleAudit(q)}
                  className="w-full text-left p-3 text-sm bg-slate-50 hover:bg-blue-50 text-slate-700 hover:text-blue-700 rounded-lg transition-colors border border-slate-100 hover:border-blue-200"
                 >
                   {q}
                 </button>
               ))}
             </div>
           </div>
           
           <div className="mt-auto">
             <label className="text-xs font-semibold text-slate-500 mb-2 block">Consulta Específica</label>
             <div className="relative">
               <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none h-32"
                placeholder="Ex: Compare o crescimento do HES com o HMML..."
               />
               <button 
                onClick={() => handleAudit()}
                disabled={loading || !prompt}
                className="absolute bottom-3 right-3 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
               >
                 {loading ? <Loader2 className="animate-spin" size={16} /> : <Send size={16} />}
               </button>
             </div>
           </div>
        </div>

        {/* Right Panel: Output */}
        <div className="lg:col-span-2 bg-slate-900 rounded-xl shadow-lg flex flex-col overflow-hidden text-slate-100">
          <div className="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center">
            <h3 className="font-semibold flex items-center gap-2 text-blue-400">
              <FileOutput size={18} />
              Parecer Técnico Gerado
            </h3>
            {response && (
                <button className="text-xs bg-slate-700 hover:bg-slate-600 px-3 py-1 rounded text-slate-300 transition-colors">
                    Copiar Parecer
                </button>
            )}
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto font-mono text-sm leading-relaxed scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-800">
            {loading ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4">
                <Loader2 className="animate-spin text-blue-500" size={40} />
                <div className="text-center">
                    <p className="text-slate-300 font-medium">Processando Auditoria...</p>
                    <p className="text-xs text-slate-500 mt-1">Comparando base 2023 (110 leitos HES) com dados atuais.</p>
                </div>
              </div>
            ) : response ? (
              <div className="whitespace-pre-wrap">{response}</div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-3">
                <Bot size={48} className="text-slate-700 mb-2 opacity-50"/>
                <p>O sistema aguarda sua solicitação de análise.</p>
                <p className="text-xs text-slate-700 max-w-xs text-center">
                    Utilize os botões ao lado para gerar relatórios imediatos sobre a evolução da rede hospitalar.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAudit;