// Pure rendering. Uses textContent only (never innerHTML) so data is never parsed as markup.
export function el(tag, props = {}, ...kids) {
  const n = Object.assign(document.createElement(tag), props);
  n.append(...kids.filter((k) => k != null));
  return n;
}
const list = (items) => el("ul", {}, ...items.map((i) => el("li", {}, i)));
const section = (title, ...kids) => [el("h3", {}, title), ...kids];
const block = (cls, label, ...kids) => el("div", { className: `block ${cls}` }, el("span", { className: "label" }, label), ...kids);

export function patientList(root, patients, selectedId, onSelect) {
  root.setAttribute("aria-busy", "false");
  const btns = patients.map((p) => {
    const b = el("button", { type: "button", className: "pt" }, el("strong", {}, `${p.id} ${p.name}`),
      el("small", {}, el("span", { className: "cat" }, p.category), `, age ${p.age}`), el("small", {}, p.history));
    b.setAttribute("aria-pressed", String(p.id === selectedId));
    b.addEventListener("click", () => onSelect(p.id));
    b.addEventListener("keydown", (e) => {
      const i = btns.indexOf(b), d = e.key === "ArrowDown" ? 1 : e.key === "ArrowUp" ? -1 : 0;
      if (d) { e.preventDefault(); btns[(i + d + btns.length) % btns.length].focus(); }
    });
    return b;
  });
  root.replaceChildren(...btns);
}

export function patientDetail(root, p) {
  root.replaceChildren(
    block("fact", "Patient facts · synthetic, not a real person",
      el("p", {}, el("strong", {}, `${p.id} · ${p.name}, ${p.age}`), ` · ${p.category} (${p.substance})`),
      ...section("Background", el("p", {}, p.background)),
      ...section("History", el("p", {}, p.history)),
      ...section("Observed behaviors", list(p.behaviors)),
      ...section("Triggers", list(p.triggers)),
      ...section("Previous interventions", list(p.interventions)),
      ...section("Treatment-history summary", el("p", {}, p.treatmentSummary)),
      ...section("Progress", el("p", {}, el("span", { className: "tag" }, p.progress.status), p.progress.note))));
}

export function message(role, ...kids) { return el("div", { className: `msg ${role}` }, ...kids); }

export function answer(blocks, onCite) {
  const wrap = el("div", { className: "msg bot" });
  blocks.forEach((b) => {
    if (b.kind === "fact") wrap.append(block("fact", "Patient fact (synthetic)", el("p", {}, b.text)));
    else if (b.kind === "model") wrap.append(block("mdl", "Model interpretation · mock, not evidence", el("p", {}, b.text)));
    else if (b.kind === "notice") wrap.append(block("", "No evidence found", el("p", { className: "state" }, b.text)));
    else {
      const p = el("p", {}, b.text, " ");
      b.cites.forEach((id) => { const c = el("button", { type: "button", className: "cite" }, `[${id}]`); c.addEventListener("click", () => onCite(id)); p.append(c); });
      wrap.append(block("evd", "Retrieved research evidence", p));
    }
  });
  return wrap;
}

export function evidencePanel(root, view, onOpen) {
  if (view.kind !== "chunks") return root.replaceChildren(el("p", { className: `state ${view.kind === "error" ? "error" : ""}` }, view.text));
  root.replaceChildren(...view.chunks.map((c) => {
    const open = el("button", { type: "button" }, "Open excerpt");
    open.addEventListener("click", () => onOpen(c.id));
    const box = el("div", { className: "chunk" + (c.id === view.active ? " on" : ""), id: `chunk-${c.id}` },
      el("strong", {}, c.docTitle), el("div", { className: "meta" }, `${c.section} · p. ${c.page} · citation ${c.id}`),
      block("evd", "Retrieved text", el("p", {}, c.text)), open);
    return box;
  }));
}

export function timeline(root, events) {
  root.replaceChildren(...(events.length ? events.map((e) => el("li", {}, el("time", {}, e.time), el("span", { className: "tag" }, e.type), e.text))
    : [el("li", { className: "state" }, "No activity yet.")]));
}
