// Data layer. Same async signatures a future fetch()-based backend client will use.
import { patients, chunks, documents } from "./mock-data.js";
import { API_BASE } from "./config.js";

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
const ev = (type, text) => ({ time: now(), type, text });

// Explicit demo mode only (?mock=1). A backend failure is NEVER silently replaced with mock data.
export const MOCK = new URLSearchParams(location.search).has("mock");
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

async function http(path) {
  let r;
  try { r = await fetch(API_BASE + path); }
  catch { throw new Error(`Cannot reach the API at ${API_BASE}. Is the backend running?`); }
  if (!r.ok) {
    let msg = `API error ${r.status}`;
    try { msg = (await r.json()).error?.message || msg; } catch { /* non-JSON error body */ }
    throw new Error(msg);
  }
  return r.json();
}

const toSummary = (p) => ({ id: p.patient_id, name: p.display_alias, category: cap(p.primary_category), age: p.age_years, history: p.summary });
const span = (a, b) => `${a.slice(0, 7)} to ${b ? b.slice(0, 7) : "ongoing"}`;

function toDetail(d) {
  const of = (k) => d.factors.filter((f) => f.kind === k).map((f) => f.description);
  const last = d.progress[d.progress.length - 1];
  return {
    ...toSummary(d), substance: (d.use.find((u) => u.is_primary) || d.use[0] || { name: "unknown" }).name,
    background: d.social_context, behaviors: of("observed_behavior"), triggers: of("trigger"),
    interventions: d.interventions.map((i) => `${i.intervention_type} (${span(i.start_date, i.end_date)}, ${i.status})`),
    treatmentSummary: d.interventions.length ? d.interventions.map((i) => `${i.intervention_type}: ${i.outcome_note}`).join("; ") : "No formal interventions recorded.",
    progress: last ? { status: last.direction, note: last.observation } : { status: "unknown", note: "No observations recorded." },
  };
}

export async function listPatients() {
  if (MOCK) { await wait(350); return patients.map(({ id, category, name, age, history, treatmentSummary }) => ({ id, category, name, age, history, treatmentSummary })); }
  return (await http("/api/patients?limit=100")).items.map(toSummary);
}
export async function getPatient(id) {
  if (MOCK) { await wait(120); const p = patients.find((x) => x.id === id); if (!p) throw new Error("Patient not found"); return p; }
  return toDetail(await http(`/api/patients/${encodeURIComponent(id)}`));
}
export const getDocumentTitle = (key) => documents[key].title;

function retrieve(question) {
  const q = question.toLowerCase();
  return chunks.map((c) => ({ c, s: c.topics.filter((t) => q.includes(t)).length })).filter((x) => x.s > 0)
    .sort((a, b) => b.s - a.s).slice(0, 3).map((x) => ({ ...x.c, docTitle: documents[x.c.doc].title }));
}

// Returns { blocks:[{kind:"fact|evidence|model|notice", text, cites?}], evidence:[], events:[] }
export async function ask({ patientId, question, mode }) {
  await wait(700);
  if (/error/i.test(question)) throw new Error("Mock service error: the generation step failed. No answer was produced.");
  const p = await getPatient(patientId);
  const events = [ev("request", `Question received (mode: ${mode})`)];
  const blocks = [];
  let evidence = [];
  if (mode !== "general") {
    evidence = retrieve(question);
    events.push(ev("retrieval", `Retrieved ${evidence.length} chunk(s)`));
    blocks.push({ kind: "fact", text: `${p.id} (${p.category}): ${p.history}` });
    if (evidence.length) {
      blocks.push({ kind: "evidence", text: "Retrieved passages relate to this question (mock summary).", cites: evidence.map((e) => e.id) });
    } else {
      blocks.push({ kind: "notice", text: "No supporting evidence was found in the corpus for this question. Nothing is cited." });
    }
  }
  if (mode !== "rag") {
    events.push(ev("generation", "Model interpretation generated (mock)"));
    blocks.push({ kind: "model", text: mode === "both" && !evidence.length
      ? "Mock interpretation based on general knowledge only; no corpus evidence supports it."
      : "Mock interpretation: a student might compare this patient's history with typical approaches, without choosing a treatment." });
  } else {
    events.push(ev("generation", "Evidence-only answer assembled (mock)"));
  }
  return { blocks, evidence, events };
}
