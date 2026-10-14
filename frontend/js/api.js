// Data layer. Same async signatures a future fetch()-based backend client will use.
import { patients, chunks, documents } from "./mock-data.js";

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
const ev = (type, text) => ({ time: now(), type, text });

export async function listPatients() { await wait(350); return patients.map(({ id, category, name, age, history, treatmentSummary }) => ({ id, category, name, age, history, treatmentSummary })); }
export async function getPatient(id) { await wait(120); const p = patients.find((x) => x.id === id); if (!p) throw new Error("Patient not found"); return p; }
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
