# MindEvidence Lab: Frontend (Batch 01)

Vanilla HTML, CSS and ES modules. Mock data only; no backend, no build step. All patients are synthetic.

## Run
ES modules need http, not `file://`:

    cd frontend
    python -m http.server 5500

Open http://localhost:5500.

## Structure
- `index.html`: layout and landmarks
- `css/styles.css`: styles (light and dark, responsive)
- `js/mock-data.js`: patients, documents, chunks, sample questions (data only)
- `js/api.js`: async data layer with the same shape a fetch client will have; swap its internals in later batches
- `js/views.js`: DOM rendering (textContent only)
- `js/main.js`: state and interactions

## Visual distinction
- Patient facts: blue, solid edge
- Retrieved research evidence: green, double edge
- Model interpretation: purple, dashed edge
Each block also carries a text label, so color is never the only cue.

## Demo checklist
- [x] 10 synthetic patients listed, selectable by click or Up/Down keys
- [x] Selecting a patient updates the detail panel (background, behaviors, history, triggers, interventions, progress)
- [x] Question submission adds a message; the answer shows loading, then content
- [x] Mode switch (General Knowledge / RAG / Both) updates the indicator and the evidence state
- [x] Citation buttons and "Open excerpt" show the mock excerpt in a dialog
- [x] Activity timeline logs selection, retrieval, generation, inspection and errors
- [x] States: loading (patients, answer), empty, error, no evidence
- [x] Google sign-in button present but inactive (Batch 04)
- [x] Keyboard use, visible focus, labelled controls, dark mode, responsive layout

## Try these
- "What does the evidence say about relapse?" returns cited chunks
- "What is the weather forecast?" demonstrates no evidence
- "Trigger an error" demonstrates the error state
- Switch to General Knowledge to see retrieval off

Limitations: answers and excerpts are placeholders, not real document text, and nothing was tested in multiple browsers.
