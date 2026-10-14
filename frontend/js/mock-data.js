// All patients are fictional. Timelines are brief and internally consistent.
export const patients = [
  {id:"P-001",name:"Alex R.",age:42,substance:"Alcohol",summary:"Daily drinking for 8 years; two failed attempts to cut down.",timeline:[["2018","Drinking increases after job change"],["2023","First outpatient visit"],["2025","Relapse after 5 months abstinent"]]},
  {id:"P-002",name:"Jamie T.",age:29,substance:"Cannabis",summary:"Daily use since age 19; reports sleep problems when stopping.",timeline:[["2016","Begins weekend use"],["2020","Daily use"],["2025","Seeks help after missed work"]]},
  {id:"P-003",name:"Morgan L.",age:37,substance:"Opioids",summary:"Prescription opioid use after injury progressed to non-prescribed use.",timeline:[["2019","Back injury, prescribed opioids"],["2022","Obtains opioids outside prescription"],["2025","Enters treatment program"]]},
  {id:"P-004",name:"Sam K.",age:24,substance:"Stimulants",summary:"Non-prescribed stimulant use for study, now escalating.",timeline:[["2022","Starts using for exams"],["2024","Daily use, weight loss"],["2025","Counselling referral"]]},
  {id:"P-005",name:"Riley P.",age:51,substance:"Alcohol",summary:"Long-term heavy drinking with liver-related health concerns.",timeline:[["2005","Regular heavy drinking"],["2021","Hospital admission"],["2025","Inpatient detox completed"]]},
  {id:"P-006",name:"Casey D.",age:33,substance:"Gambling",summary:"Online betting with growing debt and secrecy from family.",timeline:[["2021","Begins online betting"],["2024","Debt reaches 18 months of savings"],["2025","Family confrontation"]]},
  {id:"P-007",name:"Drew M.",age:46,substance:"Opioids",summary:"Stable on maintenance therapy; concerned about stopping.",timeline:[["2015","Begins treatment"],["2020","Stable, employed"],["2025","Asks about tapering"]]},
  {id:"P-008",name:"Taylor B.",age:27,substance:"Stimulants",summary:"Weekend cocaine use that has become midweek use.",timeline:[["2022","Social use"],["2024","Midweek use, financial strain"],["2025","Self-referral"]]},
  {id:"P-009",name:"Jordan S.",age:35,substance:"Gaming",summary:"Gaming 10+ hours daily, withdrawn from work and friends.",timeline:[["2020","Remote work begins"],["2023","Loses job"],["2025","Partner urges assessment"]]},
  {id:"P-010",name:"Quinn H.",age:58,substance:"Alcohol",summary:"Drinking increased after bereavement; low mood reported.",timeline:[["2022","Spouse dies"],["2024","Daily drinking"],["2025","GP raises concerns"]]},
];

// Placeholder chunks, NOT real document text. Replaced by pgvector retrieval in batch 06.
export const mockChunks = [
  {cid:"MOCK-001",doc:"NIDA Principles (mock)",section:"Principles of effective treatment",page:"-",text:"Placeholder: treatment works best when matched to the person's needs."},
  {cid:"MOCK-002",doc:"WHO mhGAP (mock)",section:"Psychosocial interventions",page:"-",text:"Placeholder: brief psychosocial interventions are discussed for substance use."},
];
