import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export type DocType = "DFD" | "ETP" | "TR";

export interface DemandInput {
  orgao: string;            // Órgão / Secretaria
  setor: string;            // Setor / Unidade requisitante
  responsavel: string;      // Responsável pela demanda
  cargo: string;            // Cargo do responsável
  objeto: string;           // Objeto da contratação
  categoria: string;        // Bens, Serviços, Serviços de Engenharia, Obras, TIC, Saúde
  necessidade: string;      // Descrição da necessidade / problema a resolver
  quantitativo: string;     // Quantitativo estimado
  valorEstimado: string;    // Valor estimado
  prazo: string;            // Prazo de execução / vigência
  previsaoPCA: string;      // Previsão no Plano de Contratações Anual
  prioridade: string;       // Grau de prioridade (Alta / Média / Baixa)
  vinculoPlanejamento: string; // Vínculo ao PPA / Plano Estadual de Saúde
  observacoes?: string;     // Observações adicionais
}

const DOC_TITLES: Record<DocType, string> = {
  DFD: "DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA (DFD)",
  ETP: "ESTUDO TÉCNICO PRELIMINAR (ETP)",
  TR: "TERMO DE REFERÊNCIA (TR)",
};

const BASE_INSTRUCTION = `
Você é um Assessor Técnico Sênior de Licitações e Contratos da Secretaria Estadual de Saúde, especialista na Lei nº 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos) e na Instrução Normativa SEGES/ME nº 81/2022 e nº 58/2022.

DIRETRIZES OBRIGATÓRIAS:
- Redija em português formal, técnico e impessoal, no padrão da Administração Pública direta estadual.
- Fundamente o documento estritamente na Lei nº 14.133/2021, citando os dispositivos legais pertinentes (ex.: art. 18, §1º para ETP; art. 6º, XXIII para TR; art. 12, VII para DFD).
- Use a saída em MARKDOWN: títulos de seção com "##", subtítulos com "###", listas com "-" ou numeração, e tabelas quando apropriado.
- Não invente dados que não foram fornecidos: quando faltar informação, insira o marcador "[A PREENCHER PELA ÁREA REQUISITANTE]".
- Seja completo e adequado para juntada em processo administrativo eletrônico (SEI).
- Não inclua comentários fora do documento, nem texto introdutório como "aqui está". Comece diretamente pelo cabeçalho do documento.
`;

const STRUCTURE: Record<DocType, string> = {
  DFD: `
ESTRUTURA OBRIGATÓRIA DO DFD (conforme art. 12, VII da Lei 14.133/2021 e IN SEGES 81/2022):
## 1. Identificação do Documento (nº do DFD, data, setor requisitante, responsável)
## 2. Identificação do Objeto da Contratação
## 3. Justificativa da Necessidade da Contratação (descrição do problema/demanda, vínculo ao planejamento)
## 4. Quantitativo e Estimativa Preliminar de Valor
## 5. Previsão no Plano de Contratações Anual (PCA)
## 6. Grau de Prioridade da Demanda
## 7. Data Pretendida para a Contratação
## 8. Indicação do(s) Servidor(es) Responsável(is) / Integrantes da Equipe de Planejamento
## 9. Aprovação da Autoridade Competente (campo de assinatura)
`,
  ETP: `
ESTRUTURA OBRIGATÓRIA DO ETP (conforme art. 18, §1º da Lei 14.133/2021). Inclua TODOS os incisos:
## 1. Descrição da Necessidade da Contratação (inciso I)
## 2. Demonstração da Previsão no Plano de Contratações Anual (inciso II, quando houver)
## 3. Requisitos da Contratação (inciso III)
## 4. Estimativas das Quantidades, com memória de cálculo (inciso IV)
## 5. Levantamento de Mercado e Análise de Soluções Possíveis (inciso V)
## 6. Estimativa do Valor da Contratação, com planilhas e ampla pesquisa (inciso VI)
## 7. Descrição da Solução como um Todo (inciso VII)
## 8. Justificativa para o Parcelamento ou não da Solução (inciso VIII)
## 9. Demonstração das Contratações Correlatas e/ou Interdependentes (inciso IX)
## 10. Demonstração do Alinhamento com o Planejamento do Órgão (inciso X)
## 11. Resultados Pretendidos (inciso XI)
## 12. Providências Prévias à Celebração do Contrato (inciso XII)
## 13. Possíveis Impactos Ambientais e Medidas Mitigadoras (inciso XIII)
## 14. Posicionamento Conclusivo sobre a Viabilidade e Razoabilidade da Contratação (§ 2º)
`,
  TR: `
ESTRUTURA OBRIGATÓRIA DO TERMO DE REFERÊNCIA (conforme art. 6º, XXIII da Lei 14.133/2021). Inclua TODAS as alíneas:
## 1. Definição do Objeto (alínea "a")
## 2. Fundamentação da Contratação (alínea "b") — referência ao ETP/DFD
## 3. Descrição da Solução como um Todo (alínea "c")
## 4. Requisitos da Contratação (alínea "d")
## 5. Modelo de Execução do Objeto (alínea "e")
## 6. Modelo de Gestão do Contrato (alínea "f")
## 7. Critérios de Medição e de Pagamento (alínea "g")
## 8. Forma e Critérios de Seleção do Fornecedor (alínea "h")
## 9. Estimativas do Valor da Contratação (alínea "i")
## 10. Adequação Orçamentária (alínea "j")
## 11. Obrigações da Contratada e da Contratante
## 12. Sanções Administrativas
`,
};

const buildContext = (data: DemandInput): string => `
DADOS FORNECIDOS PELA ÁREA REQUISITANTE:
- Órgão/Secretaria: ${data.orgao || "Secretaria Estadual de Saúde"}
- Setor/Unidade requisitante: ${data.setor || "[A PREENCHER]"}
- Responsável pela demanda: ${data.responsavel || "[A PREENCHER]"}
- Cargo do responsável: ${data.cargo || "[A PREENCHER]"}
- Objeto da contratação: ${data.objeto || "[A PREENCHER]"}
- Categoria: ${data.categoria || "[A PREENCHER]"}
- Descrição da necessidade: ${data.necessidade || "[A PREENCHER]"}
- Quantitativo estimado: ${data.quantitativo || "[A PREENCHER]"}
- Valor estimado: ${data.valorEstimado || "[A PREENCHER]"}
- Prazo de execução/vigência: ${data.prazo || "[A PREENCHER]"}
- Previsão no PCA: ${data.previsaoPCA || "[A PREENCHER]"}
- Grau de prioridade: ${data.prioridade || "[A PREENCHER]"}
- Vínculo ao planejamento (PPA / Plano Estadual de Saúde): ${data.vinculoPlanejamento || "[A PREENCHER]"}
- Observações adicionais: ${data.observacoes || "Nenhuma"}
- Data de referência: ${new Date().toLocaleDateString("pt-BR")}
`;

export const generateDocument = async (
  type: DocType,
  data: DemandInput
): Promise<string> => {
  try {
    const prompt = `
${buildContext(data)}

TAREFA: Elabore um(a) ${DOC_TITLES[type]} completo(a), pronto(a) para juntada em processo administrativo, com base nos dados acima.

${STRUCTURE[type]}

Inicie o documento com um cabeçalho contendo o brasão textual do órgão, o nome do documento e o objeto. Ao final, inclua local, data e campos de assinatura dos responsáveis.
`;

    const response = await ai.models.generateContent({
      model: "gemini-3-pro-preview",
      contents: prompt,
      config: {
        systemInstruction: BASE_INSTRUCTION,
        temperature: 0.3,
      },
    });

    return (
      response.text ||
      `Não foi possível gerar o ${type} no momento. Tente novamente.`
    );
  } catch (error) {
    console.error(`Erro ao gerar ${type}:`, error);
    return `Erro de conexão com o módulo de geração documental (${type}). Verifique a chave de API (GEMINI_API_KEY).`;
  }
};
