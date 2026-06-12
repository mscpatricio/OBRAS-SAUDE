import React, { useRef, useState } from 'react';
import {
  FileText, FileSignature, ClipboardList, Sparkles, Loader2, Download,
  Printer, FileType, Building2, Wand2, ListChecks, AlertCircle, CheckCircle2
} from 'lucide-react';
import { generateDocument, DocType, DemandInput } from '../services/documentService';
import Markdown from './Markdown';

const DOC_META: Record<DocType, { label: string; full: string; icon: React.ElementType; base: string }> = {
  DFD: { label: 'DFD', full: 'Documento de Formalização da Demanda', icon: ClipboardList, base: 'Art. 12, VII' },
  ETP: { label: 'ETP', full: 'Estudo Técnico Preliminar', icon: FileSignature, base: 'Art. 18, §1º' },
  TR: { label: 'TR', full: 'Termo de Referência', icon: FileText, base: 'Art. 6º, XXIII' },
};

const EMPTY: DemandInput = {
  orgao: 'Secretaria Estadual de Saúde',
  setor: '',
  responsavel: '',
  cargo: '',
  objeto: '',
  categoria: 'Bens',
  necessidade: '',
  quantitativo: '',
  valorEstimado: '',
  prazo: '',
  previsaoPCA: '',
  prioridade: 'Alta',
  vinculoPlanejamento: '',
  observacoes: '',
};

const CATEGORIES = [
  'Bens', 'Serviços', 'Serviços de Engenharia', 'Obras',
  'Tecnologia da Informação (TIC)', 'Insumos e Medicamentos',
  'Equipamentos Médico-Hospitalares', 'Serviços de Saúde',
];

const DocumentGenerator: React.FC = () => {
  const [data, setData] = useState<DemandInput>(EMPTY);
  const [selected, setSelected] = useState<Record<DocType, boolean>>({ DFD: true, ETP: true, TR: true });
  const [docs, setDocs] = useState<Partial<Record<DocType, string>>>({});
  const [activeDoc, setActiveDoc] = useState<DocType | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const reportRef = useRef<HTMLDivElement>(null);

  const update = (field: keyof DemandInput, value: string) =>
    setData((prev) => ({ ...prev, [field]: value }));

  const toggleDoc = (t: DocType) =>
    setSelected((prev) => ({ ...prev, [t]: !prev[t] }));

  const anySelected = Object.values(selected).some(Boolean);

  const handleGenerate = async () => {
    if (!anySelected || !data.objeto.trim()) return;
    setLoading(true);
    setDocs({});
    setActiveDoc(null);

    // Generate in the logical order: DFD -> ETP -> TR
    const order: DocType[] = (['DFD', 'ETP', 'TR'] as DocType[]).filter((t) => selected[t]);
    const generated: Partial<Record<DocType, string>> = {};

    for (const t of order) {
      setProgress(`Gerando ${DOC_META[t].label} — ${DOC_META[t].full}...`);
      const result = await generateDocument(t, data);
      generated[t] = result;
      setDocs({ ...generated });
      if (!activeDoc) setActiveDoc(t);
    }

    setActiveDoc(order[0]);
    setProgress('');
    setLoading(false);
  };

  const fileName = (ext: string) => {
    const t = activeDoc ?? 'DOC';
    const obj = (data.objeto || 'documento').slice(0, 30).replace(/[^a-zA-Z0-9]/g, '_');
    return `${t}_${obj}_${new Date().toISOString().split('T')[0]}.${ext}`;
  };

  const handleDownloadPDF = async () => {
    if (!reportRef.current) return;
    // @ts-ignore
    if (typeof window.html2pdf === 'undefined') {
      alert('Biblioteca PDF ainda carregando. Tente novamente em alguns segundos.');
      return;
    }
    setIsExporting(true);
    const opt = {
      margin: [12, 12, 12, 12],
      filename: fileName('pdf'),
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, logging: false },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
    };
    try {
      // @ts-ignore
      await window.html2pdf().set(opt).from(reportRef.current).save();
    } catch (e) {
      console.error(e);
      alert('Erro ao gerar PDF. Use a opção Imprimir (Ctrl+P).');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadDOCX = () => {
    if (!reportRef.current) return;
    const header = `<html xmlns:o='urn:schemas-microsoft-com:office:office'
      xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head><meta charset='utf-8'><title>Documento SESA</title>
      <style>
        body { font-family: 'Times New Roman', serif; font-size: 12pt; color:#000; line-height:1.5; }
        h1 { text-align:center; font-size:14pt; text-transform:uppercase; }
        h2 { font-size:12pt; text-transform:uppercase; border-bottom:1px solid #000; }
        table { border-collapse: collapse; width:100%; }
        th, td { border:1px solid #333; padding:6px; text-align:left; font-size:10pt; }
        th { background:#eee; }
      </style></head><body>`;
    const blob = new Blob(['﻿', header + reportRef.current.innerHTML + '</body></html>'], {
      type: 'application/msword',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName('doc');
    document.body.appendChild(link);
    link.click();
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);
  };

  const hasDocs = Object.keys(docs).length > 0;

  return (
    <div className="animate-fade-in pb-10">
      {/* Header */}
      <div className="mb-6 no-print">
        <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
          <Wand2 className="text-blue-600" />
          Gerador de Documentos de Contratação
        </h2>
        <p className="text-slate-500">
          Geração automatizada de ETP, DFD e TR conforme a Lei nº 14.133/2021 para a Secretaria Estadual de Saúde.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left: Form */}
        <div className="lg:col-span-2 space-y-5 no-print">
          {/* Document selector */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
              <ListChecks size={16} /> Documentos a Gerar
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {(Object.keys(DOC_META) as DocType[]).map((t) => {
                const Icon = DOC_META[t].icon;
                const on = selected[t];
                return (
                  <button
                    key={t}
                    onClick={() => toggleDoc(t)}
                    className={`flex flex-col items-center gap-1 p-3 rounded-lg border transition-all text-center ${
                      on
                        ? 'bg-blue-50 border-blue-300 text-blue-700 shadow-sm'
                        : 'bg-slate-50 border-slate-200 text-slate-400 hover:border-slate-300'
                    }`}
                  >
                    <Icon size={20} />
                    <span className="text-xs font-bold">{t}</span>
                    <span className="text-[9px] leading-tight">{DOC_META[t].base}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Demand form */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
              <ClipboardList size={16} /> Dados da Demanda
            </h3>

            <Field label="Órgão / Secretaria">
              <input className={inputCls} value={data.orgao} onChange={(e) => update('orgao', e.target.value)} />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Setor requisitante">
                <input className={inputCls} placeholder="Ex.: Dep. de Logística"
                  value={data.setor} onChange={(e) => update('setor', e.target.value)} />
              </Field>
              <Field label="Categoria">
                <select className={inputCls} value={data.categoria} onChange={(e) => update('categoria', e.target.value)}>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </Field>
            </div>

            <Field label="Objeto da contratação *">
              <input className={inputCls} placeholder="Ex.: Aquisição de equipamentos de UTI"
                value={data.objeto} onChange={(e) => update('objeto', e.target.value)} />
            </Field>

            <Field label="Descrição da necessidade / problema a resolver">
              <textarea className={`${inputCls} h-24 resize-none`}
                placeholder="Descreva a motivação, o problema e o impacto na prestação do serviço de saúde..."
                value={data.necessidade} onChange={(e) => update('necessidade', e.target.value)} />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Quantitativo estimado">
                <input className={inputCls} placeholder="Ex.: 50 unidades"
                  value={data.quantitativo} onChange={(e) => update('quantitativo', e.target.value)} />
              </Field>
              <Field label="Valor estimado (R$)">
                <input className={inputCls} placeholder="Ex.: R$ 1.200.000,00"
                  value={data.valorEstimado} onChange={(e) => update('valorEstimado', e.target.value)} />
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Prazo de execução / vigência">
                <input className={inputCls} placeholder="Ex.: 12 meses"
                  value={data.prazo} onChange={(e) => update('prazo', e.target.value)} />
              </Field>
              <Field label="Grau de prioridade">
                <select className={inputCls} value={data.prioridade} onChange={(e) => update('prioridade', e.target.value)}>
                  <option>Alta</option><option>Média</option><option>Baixa</option>
                </select>
              </Field>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Responsável pela demanda">
                <input className={inputCls} value={data.responsavel} onChange={(e) => update('responsavel', e.target.value)} />
              </Field>
              <Field label="Cargo / função">
                <input className={inputCls} value={data.cargo} onChange={(e) => update('cargo', e.target.value)} />
              </Field>
            </div>

            <Field label="Previsão no PCA (Plano de Contratações Anual)">
              <input className={inputCls} placeholder="Ex.: Item nº 045/2026 do PCA"
                value={data.previsaoPCA} onChange={(e) => update('previsaoPCA', e.target.value)} />
            </Field>

            <Field label="Vínculo ao planejamento (PPA / Plano Estadual de Saúde)">
              <input className={inputCls} placeholder="Ex.: Diretriz 3 do Plano Estadual de Saúde 2024-2027"
                value={data.vinculoPlanejamento} onChange={(e) => update('vinculoPlanejamento', e.target.value)} />
            </Field>

            <Field label="Observações adicionais">
              <textarea className={`${inputCls} h-16 resize-none`}
                value={data.observacoes} onChange={(e) => update('observacoes', e.target.value)} />
            </Field>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !anySelected || !data.objeto.trim()}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {loading ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
            {loading ? 'Gerando...' : 'Gerar Documentos com IA'}
          </button>
          {!data.objeto.trim() && (
            <p className="text-xs text-amber-600 flex items-center gap-1 -mt-3">
              <AlertCircle size={12} /> Informe ao menos o Objeto da contratação.
            </p>
          )}
        </div>

        {/* Right: Output */}
        <div className="lg:col-span-3">
          {/* Doc tabs + toolbar */}
          {hasDocs && (
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3 no-print">
              <div className="flex gap-1 bg-slate-100 p-1 rounded-lg">
                {(Object.keys(docs) as DocType[]).map((t) => (
                  <button
                    key={t}
                    onClick={() => setActiveDoc(t)}
                    className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      activeDoc === t ? 'bg-white text-blue-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button onClick={() => window.print()} className={toolbarBtn}>
                  <Printer size={15} /> <span className="hidden sm:inline">Imprimir</span>
                </button>
                <button onClick={handleDownloadDOCX} className={`${toolbarBtn} text-blue-700 bg-blue-50 border-blue-200 hover:bg-blue-100`}>
                  <FileType size={15} /> <span className="hidden sm:inline">DOCX</span>
                </button>
                <button onClick={handleDownloadPDF} disabled={isExporting}
                  className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-colors shadow-sm disabled:opacity-70">
                  {isExporting ? <Loader2 className="animate-spin" size={15} /> : <Download size={15} />}
                  <span className="hidden sm:inline">PDF</span>
                </button>
              </div>
            </div>
          )}

          {/* Document paper */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 min-h-[600px]">
            {loading && !hasDocs ? (
              <div className="h-[600px] flex flex-col items-center justify-center text-slate-400 space-y-4">
                <Loader2 className="animate-spin text-blue-500" size={44} />
                <div className="text-center">
                  <p className="text-slate-600 font-medium">{progress || 'Processando...'}</p>
                  <p className="text-xs text-slate-400 mt-1">Aplicando os requisitos da Lei nº 14.133/2021.</p>
                </div>
              </div>
            ) : activeDoc && docs[activeDoc] ? (
              <>
                {loading && (
                  <div className="bg-blue-50 border-b border-blue-100 px-6 py-2 text-xs text-blue-700 flex items-center gap-2 no-print">
                    <Loader2 className="animate-spin" size={13} /> {progress}
                  </div>
                )}
                <div id="report-container" ref={reportRef} className="p-10 print:p-0">
                  {/* Official header */}
                  <div className="flex items-center gap-4 border-b-2 border-slate-800 pb-4 mb-6">
                    <div className="w-16 h-16 bg-slate-900 text-white flex items-center justify-center rounded-lg flex-shrink-0">
                      <Building2 size={32} />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-600 uppercase">Governo do Estado</p>
                      <p className="text-sm font-bold text-slate-900 uppercase">{data.orgao || 'Secretaria Estadual de Saúde'}</p>
                      <p className="text-[10px] text-slate-500 uppercase">{DOC_META[activeDoc].full} — {DOC_META[activeDoc].base} da Lei 14.133/2021</p>
                    </div>
                  </div>
                  <Markdown content={docs[activeDoc] as string} />
                </div>
              </>
            ) : (
              <div className="h-[600px] flex flex-col items-center justify-center text-slate-300 space-y-3 p-8 text-center">
                <FileSignature size={56} className="opacity-40" />
                <p className="text-slate-500 font-medium">Nenhum documento gerado ainda</p>
                <p className="text-xs text-slate-400 max-w-sm">
                  Preencha os dados da demanda à esquerda, selecione os documentos desejados (DFD, ETP, TR) e clique em
                  <strong> Gerar Documentos com IA</strong>. Cada documento segue a estrutura exigida pela Nova Lei de Licitações.
                </p>
                <div className="flex gap-4 pt-2 text-[11px] text-slate-400">
                  <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500" /> Editável</span>
                  <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500" /> PDF / DOCX</span>
                  <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500" /> Pronto p/ SEI</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const inputCls =
  'w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition';

const toolbarBtn =
  'flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 text-sm transition-colors';

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div>
    <label className="text-xs font-medium text-slate-500 mb-1 block">{label}</label>
    {children}
  </div>
);

export default DocumentGenerator;
