import { patients, mockChunks } from "./mock-data.js";

const $ = (id) => document.getElementById(id);
const state = { patient: null };

// DOM construction via textContent only: no innerHTML, so text is never parsed as markup.
function el(tag, props = {}, ...kids) {
  const n = Object.assign(document.createElement(tag), props);
  n.append(...kids);
  return n;
}

function logEvent(text) {
  $("log").prepend(el("li", {}, `${new Date().toLocaleTimeString()}  ${text}`));
}

function renderList() {
  const ul = $("patients");
  patients.forEach((p) => {
    const b = el("button", { type: "button" }, `${p.id} ${p.name}`, el("small", {}, `${p.substance}, age ${p.age}`));
    b.addEventListener("click", () => select(p, b));
    ul.append(el("li", {}, b));
  });
}

function select(p, btn) {
  state.patient = p;
  document.querySelectorAll("#patients button").forEach((b) => b.removeAttribute("aria-current"));
  btn.setAttribute("aria-current", "true");
  const tl = el("ul");
  p.timeline.forEach(([y, e]) => tl.append(el("li", {}, `${y}: ${e}`)));
  $("detail").replaceChildren(
    el("div", { className: "card fact" },
      el("span", { className: "tag" }, "Patient facts (synthetic)"),
      el("p", {}, `${p.id}, ${p.name}, ${p.age}. ${p.summary}`), tl));
  $("answer").replaceChildren();
  logEvent(`Opened ${p.id}`);
}

function ask(e) {
  e.preventDefault();
  if (!state.patient) return $("answer").replaceChildren(el("p", { className: "card warn" }, "Select a patient first."));
  const mode = $("mode").value, q = $("q").value.trim();
  const useRag = mode !== "general";
  const useGen = mode === "general" || mode === "both";
  const out = [el("p", { className: "tag" }, `Mock answer. Mode: ${mode}. Not model output.`)];
  if (useGen) out.push(el("div", { className: "card model" }, el("span", { className: "tag" }, "Model interpretation (general knowledge)"),
    el("p", {}, "Placeholder general-knowledge answer. The real model call arrives in batch 07.")));
  if (useRag) out.push(el("div", { className: "card evd" }, el("span", { className: "tag" }, "Research evidence"),
    el("p", {}, "Placeholder evidence summary citing [MOCK-001] and [MOCK-002].")));
  $("answer").replaceChildren(...out);
  const ev = useRag
    ? mockChunks.map((c) => el("div", { className: "card evd" }, el("strong", {}, c.cid),
        el("div", { className: "tag" }, `${c.doc} / ${c.section} / p. ${c.page}`), el("p", {}, c.text)))
    : [el("p", { className: "empty" }, "No retrieval in this mode.")];
  $("evidence").replaceChildren(...ev);
  logEvent(`Asked (${mode}) about ${state.patient.id}: ${q.slice(0, 60)}`);
}

renderList();
$("ask").addEventListener("submit", ask);
