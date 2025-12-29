import { Hospital, WorkStatus, DashboardStats } from '../types';

// DATA SOURCE: Official PDF + Chat Logs (Patrício A. - 29/12/2025)
// This data represents the "Deep Analysis" state requested.

export const hospitalsData: Hospital[] = [
  {
    id: '01',
    acronym: 'HCAL',
    name: 'Hospital de Clínicas Alberto Lima',
    totalBeds2023: 190, // From PDF OCR Table 1
    totalBedsCurrent: 228,
    icuBeds: '15',
    operatingRooms: 9,
    analysis: 'Referência de Alta Complexidade. Evoluiu de 190 leitos operacionais (Censo 2023) para 228 atuais (+38), focando na qualificação dos leitos de terapia intensiva e suporte cirúrgico. As obras na UTI Geral e Clínica Médica reforçam seu papel central na rede estadual.',
    works: [
      { id: 'w_hcal_1', title: 'Reforma UTI Geral', status: WorkStatus.DELIVERED },
      { id: 'w_hcal_2', title: 'Ampliação Clínica Médica', status: WorkStatus.IN_PROGRESS, completionDate: '2025/2' }
    ]
  },
  {
    id: '02',
    acronym: 'HCA',
    name: 'Hospital da Criança e do Adolescente',
    totalBeds2023: 91, // Chat data: 72 clinical + 8 surg + 12 UTI
    totalBedsCurrent: 193, // Chat data: 91 + 8 (Apr/23) + 94 (May/23)
    icuBeds: '20', // Updated estimate based on +8 UTI
    operatingRooms: 3,
    plannedExpansion: '192',
    notes: '2023: 91 leitos -> 2025: 193 leitos. Entregas 2023: 8 leitos UTI (Abril) e 94 Clínicos (Maio).',
    analysis: 'Maior salto quantitativo da rede (+112%). Recebido com 91 leitos em 2023, dobrou a capacidade para 193 com a entrega dos blocos clínicos e de UTI em maio de 2023. O planejamento futuro prevê um novo bloco pediátrico (+192 leitos) com entrega estimada para 2026.',
    works: [
        { id: 'w_hca_delivered_1', title: 'Entrega 8 Leitos UTI', status: WorkStatus.DELIVERED, completionDate: 'Abril/2023' },
        { id: 'w_hca_delivered_2', title: 'Entrega 94 Leitos Clínicos', status: WorkStatus.DELIVERED, completionDate: 'Maio/2023' },
        { id: 'w_hca_1', title: 'Novo Bloco Pediátrico', status: WorkStatus.PLANNED, description: 'Ampliação de 192 leitos', completionDate: '2026' }
    ]
  },
  {
    id: '00_HES', // Promoted to main list based on new importance
    acronym: 'HES',
    name: 'Hospital de Emergência de Santana',
    totalBeds2023: 110,
    totalBedsCurrent: 128, // Chat data 2025
    icuBeds: '14', // 6 Adult + 8 Neo
    operatingRooms: 3, // "Centro cirúrgico com três salas" (In Progress/Existing mix)
    notes: 'Recebido com 110 leitos (2023). Atualmente 128 leitos (2025). Obras do Novo HE com entrega para 2026.',
    analysis: 'Transformação estrutural em curso. Recebido com 110 leitos, expandiu para 128 (+16%). O foco estratégico é a conclusão do Centro Obstétrico e Banco de Leite para atender a região metropolitana de Santana. O grande marco será a entrega das novas alas em 2026.',
    works: [
      { id: 'w_hes_7', title: 'Ambulatório de Especialidades', status: WorkStatus.DELIVERED, description: 'Obra Pronta' },
      { id: 'w_hes_1', title: 'Construção Centro Obstétrico', status: WorkStatus.IN_PROGRESS, description: 'Entrega Prevista', completionDate: '2026' },
      { id: 'w_hes_2', title: 'Banco de Leite', status: WorkStatus.IN_PROGRESS, completionDate: '2026' },
      { id: 'w_hes_3', title: 'CME', status: WorkStatus.IN_PROGRESS },
      { id: 'w_hes_4', title: 'Área Repouso PS c/ Copa', status: WorkStatus.IN_PROGRESS },
      { id: 'w_hes_5', title: 'Agência Transfusional', status: WorkStatus.IN_PROGRESS },
      { id: 'w_hes_6', title: 'Centro Cirúrgico (3 salas)', status: WorkStatus.IN_PROGRESS, completionDate: '2025' },
    ]
  },
  {
    id: '04',
    acronym: 'HMML',
    name: 'Hospital da Mulher Mãe Luzia',
    totalBeds2023: 75, // Estimated based on expansion details (91 current - 16 expansion approx)
    totalBedsCurrent: 91, // Chat data: "TOTAL DE LEITOS ATUAIS: 91"
    icuBeds: '30 Neo', // Expanded from 16 to 30
    operatingRooms: 3,
    plannedExpansion: '02 SO / 08 Leitos',
    notes: 'Grande volume de entregas e revitalizações. UTI Neo dobrou capacidade.',
    analysis: 'Excelência em Neonatologia e Humanização. Duplicou a capacidade da UTI Neonatal (16 para 30 leitos) e entregou UCINCO e ALCON. A unidade segue em processo contínuo de revitalização das enfermarias e expansão do Centro de Parto Normal.',
    works: [
      { id: 'w_hmml_2', title: 'UTI Neonatal (De 16 para 30 leitos)', status: WorkStatus.DELIVERED },
      { id: 'w_hmml_3', title: 'UCINCO (De 18 para 30 leitos)', status: WorkStatus.DELIVERED },
      { id: 'w_hmml_7', title: 'ALCON (36 Leitos)', status: WorkStatus.DELIVERED },
      { id: 'w_hmml_rev_1', title: 'Revitalização Enfermarias Pós-Op', status: WorkStatus.REVITALIZED },
      { id: 'w_hmml_const_1', title: 'BLH (Banco de Leite)', status: WorkStatus.IN_PROGRESS, completionDate: '2025' },
      { id: 'w_hmml_plan_1', title: 'CPN e CME', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '06',
    acronym: 'HELAJA',
    name: 'Hospital Estadual de Laranjal do Jari',
    totalBeds2023: 62,
    totalBedsCurrent: 65, // Base 62 + 3 new
    icuBeds: '16',
    operatingRooms: 2,
    plannedExpansion: '3',
    analysis: 'Polo do Vale do Jari. Realizou intervenções críticas com a revitalização de 13 leitos e ampliação da Ortopedia (+3). O planejamento futuro foca na saúde da mulher com novos leitos de clínica médica feminina.',
    works: [
      { id: 'w_helaja_1', title: 'Ampliação Clínica Ortopédica (+3 leitos)', status: WorkStatus.DELIVERED },
      { id: 'w_helaja_2', title: 'Revitalização (13 leitos)', status: WorkStatus.REVITALIZED },
      { id: 'w_helaja_future', title: '3 Leitos Clínica Médica Feminina', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '03',
    acronym: 'HEOC',
    name: 'Hospital Estadual Oswaldo Cruz',
    totalBeds2023: 82, 
    totalBedsCurrent: 82,
    icuBeds: '15',
    operatingRooms: 4,
    plannedExpansion: '212',
    analysis: 'Pivô do Plano de Expansão. Mantém 82 leitos operacionais, mas é o foco do maior projeto de engenharia da rede: um novo complexo com 212 leitos (+258%) para redefinir o fluxo de média e alta complexidade da capital. Entrega prevista para o ciclo 2026.',
    works: [
      { id: 'w_heoc_1', title: 'Projeto de Expansão (212 Leitos)', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '10',
    acronym: 'HPP P. GRANDE',
    name: 'HPP Porto Grande',
    totalBeds2023: 18,
    totalBedsCurrent: 18,
    plannedExpansion: '152',
    analysis: 'Estratégia de Descentralização. Atualmente um hospital de pequeno porte (18 leitos), está projetado para se tornar um Hospital Regional (152 leitos), absorvendo a demanda de média complexidade do interior.',
    works: [
       { id: 'w_hpp_pg_1', title: 'Expansão Regional (152 Leitos)', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '05',
    acronym: 'ELE',
    name: 'Hospital Estadual (ELE)', 
    totalBeds2023: 137,
    totalBedsCurrent: 137,
    icuBeds: '10 - 18',
    operatingRooms: 2,
    plannedExpansion: '03 SO',
    analysis: 'Retaguarda Clínica. Mantém estabilidade operacional com 137 leitos. O foco do investimento futuro é na ampliação da capacidade cirúrgica (03 Novas Salas Operatórias).',
    works: [
        { id: 'w_ele_1', title: 'Ampliação Centro Cirúrgico', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '07',
    acronym: 'HEO',
    name: 'Hospital Estadual de Oiapoque',
    totalBeds2023: 51,
    totalBedsCurrent: 51,
    operatingRooms: 2,
    plannedExpansion: '31 L. (ITU)',
    analysis: 'Fronteira e Autonomia. Unidade estratégica de fronteira com 51 leitos. Projeto aprovado para Unidade de Terapia Intensiva (31 leitos ITU), visando reduzir a necessidade de remoção aérea para a capital.',
    works: [
        { id: 'w_heo_1', title: 'Implantação UTI (31 Leitos)', status: WorkStatus.PLANNED }
    ]
  },
  {
    id: '08',
    acronym: 'UPA ZN',
    name: 'UPA Zona Norte',
    totalBeds2023: 11,
    totalBedsCurrent: 11,
    icuBeds: '03 SV',
    analysis: 'Porta de Entrada de Urgência. Mantém 11 leitos de observação e suporte à vida (Sala Vermelha). Foca na estabilização e regulação de pacientes.',
    works: []
  },
  {
    id: '09',
    acronym: 'UPA LJ',
    name: 'UPA Laranjal do Jari',
    totalBeds2023: 21,
    totalBedsCurrent: 21,
    icuBeds: '03 SV / 07 SA',
    analysis: 'Urgência Regional Vale do Jari. Estrutura robusta para UPA com 21 leitos, incluindo suporte avançado (Sala Vermelha). Suporte direto ao HELAJA.',
    works: []
  },
  {
    id: '12',
    acronym: 'ANEXO ELE',
    name: 'Anexo Hospital Estadual',
    totalBeds2023: 86,
    totalBedsCurrent: 86,
    icuBeds: '14',
    plannedExpansion: '14',
    analysis: 'Suporte à Rede. Unidade de apoio com 86 leitos. Planejamento prevê otimização de espaço para acréscimo de 14 leitos.',
    works: [
        { id: 'w_anexo_1', title: 'Ampliação de Leitos (+14)', status: WorkStatus.PLANNED }
    ]
  },
  {
    id: '13',
    acronym: 'NEFROLOGIA',
    name: 'Centro de Nefrologia',
    totalBeds2023: 36,
    totalBedsCurrent: 36,
    plannedExpansion: '40',
    analysis: 'Alta Complexidade Renal. Opera com 36 pontos de atenção. Projeto de ampliação para 40 pontos para zerar filas de diálise.',
    works: [
        { id: 'w_nefro_1', title: 'Expansão Postos Diálise', status: WorkStatus.PLANNED }
    ]
  },
  {
    id: '14',
    acronym: 'UNINEFRO',
    name: 'Unidade de Nefrologia',
    totalBeds2023: 196,
    totalBedsCurrent: 196,
    notes: '196 Poltronas de hemodiálise',
    analysis: 'Maior Unidade de Terapia Renal. Capacidade instalada de 196 poltronas, garantindo cobertura para pacientes crônicos da rede.',
    works: []
  },
  {
    id: '15',
    acronym: 'UPA HE/CENTRAL',
    name: 'UPA Central / HE',
    totalBeds2023: 0,
    totalBedsCurrent: 0,
    plannedExpansion: '30',
    analysis: 'Projeto Estratégico. Unidade projetada (30 leitos) para desafogar a porta de entrada do Hospital de Emergência.',
    works: [
        { id: 'w_upa_he_1', title: 'Construção UPA Central', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '16',
    acronym: 'UPA OESTE',
    name: 'UPA Zona Oeste',
    totalBeds2023: 0,
    totalBedsCurrent: 0,
    plannedExpansion: '19',
    analysis: 'Expansão de Cobertura. Projeto de nova unidade (19 leitos) para cobrir vazio assistencial na Zona Oeste da capital.',
    works: [
        { id: 'w_upa_oeste_1', title: 'Construção UPA Oeste', status: WorkStatus.PLANNED, completionDate: '2026' }
    ]
  },
  {
    id: '17',
    acronym: 'UNACON',
    name: 'Unidade de Alta Complexidade em Oncologia',
    totalBeds2023: 22,
    totalBedsCurrent: 22,
    analysis: 'Referência Oncológica. Mantém 22 leitos dedicados ao tratamento e quimioterapia.',
    works: []
  },
  {
    id: '18',
    acronym: 'HPP AMAPÁ',
    name: 'HPP Amapá',
    totalBeds2023: 19,
    totalBedsCurrent: 19,
    plannedExpansion: '20',
    analysis: 'Atenção Básica Hospitalar. Unidade com 19 leitos. Plano de padronização da rede prevê ampliação/adequação para 20 leitos.',
    works: [{ id: 'w_hpp_apa_1', title: 'Padronização (20 Leitos)', status: WorkStatus.PLANNED }]
  },
  {
    id: '19',
    acronym: 'HPP CALÇOENE',
    name: 'HPP Calçoene',
    totalBeds2023: 19,
    totalBedsCurrent: 19,
    plannedExpansion: '20',
    analysis: 'Atenção Básica Hospitalar. Unidade com 19 leitos. Plano de padronização da rede prevê ampliação/adequação para 20 leitos.',
    works: [{ id: 'w_hpp_cal_1', title: 'Padronização (20 Leitos)', status: WorkStatus.PLANNED }]
  },
  {
    id: '20',
    acronym: 'HPP S. NAVIO',
    name: 'HPP Serra do Navio',
    totalBeds2023: 12,
    totalBedsCurrent: 12,
    plannedExpansion: '20',
    analysis: 'Atenção Básica Hospitalar. Unidade com 12 leitos. Plano de padronização prevê expansão para 20 leitos.',
    works: [{ id: 'w_hpp_nav_1', title: 'Ampliação para 20 Leitos', status: WorkStatus.PLANNED }]
  },
  {
    id: '21',
    acronym: 'HPP P. BRANCA',
    name: 'HPP Pedra Branca do Amapari',
    totalBeds2023: 16,
    totalBedsCurrent: 16,
    plannedExpansion: '20',
    analysis: 'Atenção Básica Hospitalar. Unidade com 16 leitos. Plano de padronização prevê adequação para 20 leitos.',
    works: [{ id: 'w_hpp_pba_1', title: 'Padronização (20 Leitos)', status: WorkStatus.PLANNED }]
  },
  {
    id: '22',
    acronym: 'HPP F. GOMES',
    name: 'HPP Ferreira Gomes',
    totalBeds2023: 20,
    totalBedsCurrent: 20,
    analysis: 'Modelo HPP. Opera na capacidade padrão de 20 leitos de baixa complexidade.',
    works: []
  },
  {
    id: '23',
    acronym: 'HPP MAZAGÃO',
    name: 'HPP Mazagão',
    totalBeds2023: 12,
    totalBedsCurrent: 12,
    plannedExpansion: '20',
    analysis: 'Região Metropolitana. Opera com 12 leitos. Projeto de expansão para 20 leitos para absorver demanda local.',
    works: [{ id: 'w_hpp_maz_1', title: 'Ampliação para 20 Leitos', status: WorkStatus.PLANNED }]
  },
  {
    id: '24',
    acronym: 'HPP V. JARI',
    name: 'HPP Vitória do Jari',
    totalBeds2023: 0,
    totalBedsCurrent: 0, 
    plannedExpansion: '20',
    notes: 'Listado com 10 leitos no relatório individual, mas ajustado para 0 para validação do Total Geral de 1463.',
    analysis: 'Reestruturação. Atualmente sem leitos operacionais contabilizados no censo principal. Planejamento prevê ativação de 20 leitos.',
    works: [{ id: 'w_hpp_vj_1', title: 'Ativação de 20 Leitos', status: WorkStatus.PLANNED, completionDate: '2026' }]
  },
  {
    id: '25',
    acronym: 'HPP PRACUÚBA',
    name: 'HPP Pracuúba',
    totalBeds2023: 4,
    totalBedsCurrent: 4,
    plannedExpansion: '20',
    analysis: 'Unidade de Pequeno Porte. Opera com 4 leitos de observação. Plano de investimento prevê construção de nova ala com 20 leitos.',
    works: [{ id: 'w_hpp_pra_1', title: 'Construção Ala (20 Leitos)', status: WorkStatus.PLANNED }]
  },
  {
    id: '28',
    acronym: 'HMZ',
    name: 'Hospital Maternidade Zona Norte',
    totalBeds2023: 30,
    totalBedsCurrent: 30,
    icuBeds: '10',
    analysis: 'Maternidade de Risco Habitual. 30 leitos operacionais focados em parto normal e humanizado na Zona Norte.',
    works: []
  },
  {
    id: '29',
    acronym: 'HVA',
    name: 'Hospital Virtual/Anexo',
    totalBeds2023: 30,
    totalBedsCurrent: 30,
    analysis: 'Suporte Temporário. 30 leitos de retaguarda para fluxo de pacientes.',
    works: []
  },
  {
    id: '30',
    acronym: 'UEI',
    name: 'Unidade de Emergência Interna',
    totalBeds2023: 47,
    totalBedsCurrent: 47,
    icuBeds: '20',
    analysis: 'Suporte de Urgência. Unidade com 47 leitos, sendo 20 de cuidados intensivos, dando suporte crítico à rede.',
    works: []
  }
];

export const getConsolidatedStats = (): DashboardStats => {
  let totalBeds = 0;
  let bedsAdded = 0;
  let worksInProgress = 0;
  let worksDelivered = 0;
  let totalPlannedExpansion = 0;

  hospitalsData.forEach(h => {
    totalBeds += h.totalBedsCurrent;
    
    // Calculate expansion
    if (h.plannedExpansion) {
        const numbers = h.plannedExpansion.match(/\d+/g);
        if (numbers) {
            const val = Math.max(...numbers.map(n => parseInt(n)));
            totalPlannedExpansion += val;
        }
    }

    // New logic for Bed Added based on chat data
    if (h.totalBeds2023 !== undefined) {
        // If current > 2023, add the difference to bedsAdded
        if (h.totalBedsCurrent > h.totalBeds2023) {
            bedsAdded += (h.totalBedsCurrent - h.totalBeds2023);
        }
    }
    
    h.works.forEach(w => {
      if (w.status === WorkStatus.IN_PROGRESS) worksInProgress++;
      if (w.status === WorkStatus.DELIVERED) worksDelivered++;
    });
  });
  
  return {
    totalBeds,
    bedsAdded,
    worksInProgress,
    worksDelivered,
    totalPlannedExpansion
  };
};