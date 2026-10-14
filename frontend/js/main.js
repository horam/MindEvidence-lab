import * as api from "./api.js";
import { sampleQuestions } from "./mock-data.js";
import * as v from "./views.js";

const $ = (id) => document.getElementById(id);
const MODE_NAMES = { general: "General Knowledge", rag: "RAG", both: "Both" };
const state = { patients: [], patient: null, mode: "rag", last: null, events: [], busy: false, activeCite: null, error: null };

const log = (...evs) => { state.events.unshift(...evs.reverse()); v.timeline($("timeline"), state.events); };
const toast = (t) => { $("toast").textContent = t; $("toast").hidden = false; setTimeout(() => ($("toast").hidden = true), 4000); };

function evidenceView() {
  if (state.error) return { kind: "error", text: state.error };
  if (state.mode === "general") return { kind: "off", text: "Retrieval is off in General Knowledge mode. Answers show no corpus evidence and no citations." };
  if (!state.last || state.last.mode === "general") return { kind: "empty", text: "No retrieval yet for this mode. Ask a question to retrieve evidence." };
  if (!state.last.evidence.length) return { kind: "none", text: "No evidence found: the retrieval step returned no matching chunks for the last question." };
  return { kind: "chunks", chunks: state.last.evidence, active: state.activeCite };
}
const renderEvidence = () => v.evidencePanel($("evidence"), evidenceView(), openExcerpt);

function openExcerpt(id) {
  const c = state.last?.evidence.find((e) => e.id === id);
  if (!c) return;
  state.activeCite = id; renderEvidence();
  $("ex-title").textContent = c.docTitle;
  $("ex-meta").textContent = `${c.section} · p. ${c.page} · citation ${c.id}`;
  $("ex-text").textContent = c.text;
  $("excerpt").showModal();
  log({ time: new Date().toLocaleTimeString(), type: "inspect", text: `Opened excerpt ${id}` });
}

function setMode(mode) {
  state.mode = mode;
  $("mode-ind").textContent = MODE_NAMES[mode];
  renderEvidence();
}

async function selectPatient(id) {
  state.patient = await api.getPatient(id);
  v.patientList($("patients"), state.patients, id, selectPatient);
  v.patientDetail($("detail"), state.patient);
  $("context").textContent = `Context: ${state.patient.id} (${state.patient.category}, synthetic). Questions use this patient.`;
  $("messages").replaceChildren(v.el("p", { className: "state" }, "No messages yet for this patient."));
  state.last = null; state.error = null; renderEvidence();
  log({ time: new Date().toLocaleTimeString(), type: "select", text: `Selected ${id}` });
  document.querySelector(`.pt[aria-pressed=true]`)?.focus();
}

async function submit(question) {
  if (state.busy) return;
  if (!state.patient) return toast("Select a patient first.");
  const box = $("messages");
  if (box.querySelector(".state")) box.replaceChildren();
  box.append(v.message("user", question));
  const pending = v.message("bot", v.el("p", { className: "state" }, "Retrieving and generating (mock)…"));
  pending.setAttribute("aria-busy", "true");
  box.append(pending);
  state.busy = true; $("send").disabled = true; state.error = null;
  v.evidencePanel($("evidence"), { kind: "empty", text: "Loading evidence…" });
  try {
    const mode = state.mode;
    const res = await api.ask({ patientId: state.patient.id, question, mode });
    state.last = { mode, evidence: res.evidence }; state.activeCite = null;
    pending.replaceWith(v.answer(res.blocks, openExcerpt));
    log(...res.events);
  } catch (e) {
    state.error = e.message;
    pending.replaceWith(v.message("bot", v.el("p", { className: "state error", role: "alert" }, e.message + " Try again.")));
    log({ time: new Date().toLocaleTimeString(), type: "error", text: e.message });
  } finally {
    state.busy = false; $("send").disabled = false; renderEvidence(); box.scrollTop = box.scrollHeight;
  }
}

async function init() {
  $("google").addEventListener("click", () => toast("Google sign-in is not available yet (planned for Batch 04)."));
  document.querySelectorAll("input[name=mode]").forEach((r) => r.addEventListener("change", () => setMode(r.value)));
  $("ask").addEventListener("submit", (e) => { e.preventDefault(); const q = $("q").value.trim(); if (!q) return; $("q").value = ""; submit(q); });
  $("excerpt").addEventListener("close", () => {});
  $("ex-close").addEventListener("click", () => $("excerpt").close());
  document.querySelector(".chips").append(...sampleQuestions.map((q) => {
    const b = v.el("button", { type: "button" }, q); b.addEventListener("click", () => submit(q)); return b;
  }));
  setMode("rag");
  try {
    state.patients = await api.listPatients();
    v.patientList($("patients"), state.patients, null, selectPatient);
  } catch (e) {
    $("patients").replaceChildren(v.el("p", { className: "state error", role: "alert" }, "Could not load patients. Reload to retry."));
  }
}
init();
