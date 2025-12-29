import { GoogleGenAI } from "@google/genai";
import { hospitalsData } from "./data";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const GOVERNOR_QUESTIONS = `
O Governador tem 4 perguntas chave que DEVEM ser respondidas no Briefing se possível:
1. Quantos novos leitos já entregamos? (Base: HCA +102, HES +18, etc)
2. Quantos leitos revitalizamos? (Base: HELAJA 13, HMML 2 Enfermarias)
3. Quantos leitos vamos entregar em 2026? (Base: Novo HE, Bloco Pediátrico HCA, HEOC)
4. Ampliamos a rede em quantos por cento? (Dado de referência: 4,28% até 2025, com projeção maior para 2026)

Solicitação Extra: COMPARATIVO "Como Recebeu vs Como Está vs O que Será Entregue".
ATENÇÃO AO NÚMERO TOTAL: O "Quadro Resumo" antigo mostra 1463, mas a SOMA REAL dos dados auditados é 1574.
ATENÇÃO AO CRONOGRAMA 2026: Destaque as entregas do Novo HE, HCA (Bloco Pediátrico) e HEOC para o próximo ano.
`;

const SYSTEM_INSTRUCTION = `
Você é o Auditor Sênior de Infraestrutura Hospitalar da SESA (Secretaria de Estado da Saúde) e Estrategista do Governador.

SEUS DADOS (FONTE DA VERDADE):
Use o JSON fornecido e as seguintes notas de chat recentes:
- HES (Novo HE): Recebido com 110 leitos (2023). Hoje tem 128 (2025). Futuro (2026): Entrega do Centro Obstétrico e Novas Alas.
- HMML: Recebido com menor capacidade. Hoje entregou UTI Neo (16->30), UCINCO (18->30), ALCON. Futuro (2026): CPN, CME.
- HCA: Recebido com 91. Hoje 193. Futuro (2026): Bloco Pediátrico (+192).
- HEOC: Expansão de 212 leitos prevista para entrega em 2026.
- HELAJA: Revitalizou 13 leitos e entregou 3 novos de Ortopedia. Futuro (2026): 3 leitos Clínica Médica Feminina.
- TOTAL GERAL: O sistema soma 1574 leitos atuais.

OBJETIVO:
Gerar respostas baseadas estritamente nestes números. 
Se o usuário pedir COMPARAÇÃO, estrutura a resposta claramente em: 
1. COMO RECEBEMOS (2023)
2. O QUE JÁ FIZEMOS (2023-2025)
3. O QUE VAMOS ENTREGAR (Ciclo 2026 - Novo HE e Expansões)
`;

export const generateAuditReport = async (userPrompt: string): Promise<string> => {
  try {
    const dataContext = JSON.stringify(hospitalsData, null, 2);
    const fullPrompt = `
      BASE DE DADOS TÉCNICA (JSON):
      ${dataContext}

      PERGUNTAS DO GOVERNADOR:
      ${GOVERNOR_QUESTIONS}

      SOLICITAÇÃO DO USUÁRIO:
      ${userPrompt}

      Se a pergunta for sobre "Resumo" ou "Briefing", responda as 4 perguntas do governador diretamente.
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: fullPrompt,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        temperature: 0.1,
      }
    });

    return response.text || "Não foi possível gerar a auditoria técnica no momento.";
  } catch (error) {
    console.error("Erro na auditoria IA:", error);
    return "Erro de conexão com o módulo de Auditoria IA.";
  }
};

export const generateGovernorBriefing = async (): Promise<string> => {
  try {
    const dataContext = JSON.stringify(hospitalsData, null, 2);
    
    const prompt = `
      CONTEXTO: Você está preparando o Governador para uma entrevista AO VIVO AGORA.
      
      BASE DE DADOS ATUALIZADA:
      ${dataContext}
      
      PERGUNTAS QUE O JORNALISTA VAI FAZER (E VOCÊ DEVE RESPONDER NO DISCURSO):
      ${GOVERNOR_QUESTIONS}
      
      TAREFA: Escreva um discurso direto, em primeira pessoa, respondendo a essas 4 perguntas com números exatos.
      Use a estrutura "Recebemos assim, fizemos isso, e vamos entregar aquilo em 2026".
      Cite nominalmente a entrega do NOVO HE e expansão do HCA em 2026.
      IMPORTANTE: Destaque o número total de 1.574 leitos reais (superando os 1.463 de relatórios antigos).
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: prompt,
      config: {
        temperature: 0.7,
      }
    });

    return response.text || "Não foi possível gerar o briefing no momento.";
  } catch (error) {
    console.error("Erro no briefing IA:", error);
    return "Erro ao conectar com o Gemini 3 Pro.";
  }
};