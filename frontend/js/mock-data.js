// Pure data. Everything here is synthetic. Replace via js/api.js when the backend exists.
const P = (id, category, substance, name, age, history, treatmentSummary, background, behaviors, triggers, interventions, progress) =>
  ({ id, category, substance, name, age, history, treatmentSummary, background, behaviors, triggers, interventions, progress });

export const patients = [
  P("P-001","Alcohol","Alcohol","Alex R.",42,"Daily drinking for about 8 years after a job change.","Two outpatient episodes; relapse after 5 months abstinent.","Logistics manager, lives with partner, high-pressure job.",["Drinks alone in evenings","Hides bottles"],["Work deadlines","Conflict with partner"],["Outpatient counselling (2023)","Brief motivational sessions"],{status:"Early recovery",note:"Attending weekly sessions; 3 weeks abstinent."}),
  P("P-002","Cannabis","Cannabis","Jamie T.",29,"Weekend use from 2016, daily since 2020.","One counselling referral after missed work.","Freelance designer, irregular sleep, lives alone.",["Daily evening use","Irritability when stopping"],["Insomnia","Social isolation"],["Counselling referral (2025)"],{status:"Contemplation",note:"Considering a 30-day break; sleep remains difficult."}),
  P("P-003","Opioids","Prescription opioids","Morgan L.",37,"Prescribed opioids after a 2019 back injury; non-prescribed use from 2022.","Entered a treatment program in 2025.","Warehouse worker, separated, two children.",["Seeks extra prescriptions","Withdraws from family"],["Chronic pain","Financial stress"],["Medication-assisted treatment program","Pain-management review"],{status:"Active treatment",note:"Stable attendance; pain still limiting work."}),
  P("P-004","Stimulants","Non-prescribed stimulants","Sam K.",24,"Started using for exams in 2022; daily use by 2024.","Counselling referral in 2025.","Graduate student, high academic pressure.",["Skips meals","Late-night study binges"],["Exam periods","Peer expectations"],["Counselling referral"],{status:"Early engagement",note:"Attended two sessions; use reduced but ongoing."}),
  P("P-005","Alcohol","Alcohol","Riley P.",51,"Heavy drinking since 2005; hospital admission in 2021.","Inpatient detox completed in 2025.","Retired electrician, lives with sibling.",["Morning drinking","Missed medical appointments"],["Boredom","Loneliness"],["Inpatient detox","Liver-health follow-up"],{status:"Post-detox",note:"Engaged with aftercare; sleep improving."}),
  P("P-006","Behavioral","Online gambling","Casey D.",33,"Online betting since 2021; debt reached 18 months of savings.","Family confrontation in 2025; no formal treatment yet.","Sales representative, married, one child.",["Secretive about phone use","Chases losses"],["Sports events","Payday"],["None yet; self-exclusion discussed"],{status:"Pre-treatment",note:"Open to assessment; financial counselling suggested."}),
  P("P-007","Opioids","Opioids (maintenance therapy)","Drew M.",46,"In treatment since 2015; stable and employed since 2020.","Long-term maintenance therapy; asked about tapering in 2025.","Teacher, stable housing, supportive family.",["Regular attendance","Anxiety about stopping"],["Medication changes","Stressful school terms"],["Maintenance therapy","Peer support group"],{status:"Sustained recovery",note:"Exploring taper options with their care team."}),
  P("P-008","Stimulants","Cocaine","Taylor B.",27,"Social weekend use in 2022; midweek use by 2024.","Self-referred in 2025.","Bartender, irregular hours, late nights.",["Binge pattern","Borrows money"],["Nightlife","Fatigue"],["Self-referral intake session"],{status:"Early engagement",note:"One intake completed; follow-up scheduled."}),
  P("P-009","Behavioral","Gaming","Jordan S.",35,"Remote work began 2020; gaming 10+ hours daily; job lost 2023.","Partner urged assessment in 2025.","Former analyst, living with partner.",["Sleeps by day","Withdraws from friends"],["Unstructured days","Stress after job loss"],["Initial assessment"],{status:"Assessment stage",note:"Agreed to a daily-routine plan."}),
  P("P-010","Alcohol","Alcohol","Quinn H.",58,"Drinking increased after a 2022 bereavement; daily by 2024.","GP raised concerns in 2025.","Widowed, retired nurse, adult children nearby.",["Evening drinking","Low mood"],["Anniversaries","Evenings alone"],["GP discussion","Grief-support information"],{status:"Contemplation",note:"Accepted a referral for grief and alcohol support."}),
];

export const documents = {
  NIDA:{title:"NIDA: Principles of Drug Addiction Treatment"},
  MHGAP23:{title:"WHO mhGAP Guideline (2023)"},
  MHGAPIG:{title:"WHO mhGAP Intervention Guide v2.0"},
  COCHRANE:{title:"Cochrane review: alcohol use disorder (2025)"},
};

// topics: lowercase words matched against the question.
export const chunks = [
  {id:"NIDA-p12-c1",doc:"NIDA",section:"Matching treatment to needs",page:12,topics:["treatment","needs","approach","plan","help"],text:"Mock excerpt: treatment is described as more effective when it addresses the person's wider needs, not only substance use."},
  {id:"NIDA-p18-c2",doc:"NIDA",section:"Relapse and ongoing care",page:18,topics:["relapse","recovery","retention","long-term","drinking"],text:"Mock excerpt: relapse is framed as a sign that care may need review, with longer engagement linked to better outcomes."},
  {id:"MHGAP23-p41-c3",doc:"MHGAP23",section:"Psychosocial interventions",page:41,topics:["intervention","counselling","motivational","brief","cannabis","stimulant","cocaine"],text:"Mock excerpt: brief psychosocial interventions are discussed as an option in non-specialist settings."},
  {id:"MHGAPIG-p77-c4",doc:"MHGAPIG",section:"Opioid use and withdrawal",page:77,topics:["opioid","opioids","withdrawal","maintenance","taper","pain"],text:"Mock excerpt: guidance on assessing opioid use and referring for specialist-supported management."},
  {id:"COCHRANE-p9-c5",doc:"COCHRANE",section:"Evidence summary: alcohol",page:9,topics:["alcohol","drinking","abstinence","detox"],text:"Mock excerpt: summary of trial evidence on alcohol interventions, with certainty ratings noted per outcome."},
  {id:"MHGAP23-p58-c6",doc:"MHGAP23",section:"Co-occurring conditions",page:58,topics:["mood","anxiety","sleep","insomnia","grief","depression","comorbid"],text:"Mock excerpt: low mood and sleep problems commonly co-occur with substance use and are assessed alongside it."},
  {id:"NIDA-p30-c7",doc:"NIDA",section:"Behavioral addictions",page:30,topics:["gambling","gaming","betting","behavioral","behavioural"],text:"Mock excerpt: behavioral addictions are discussed in relation to cognitive-behavioral approaches."},
];

export const sampleQuestions = [
  "What does the evidence say about relapse?",
  "Which interventions suit this case?",
  "What is the weather forecast?",
  "Trigger an error",
];
