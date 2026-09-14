# Paper Blog Posts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish one blog post per research paper, six posts in all, in the same format as the existing TCDQ post, and wire the publications page and the projects card to them.

**Architecture:** Each post is a markdown file in `_posts/` plus a folder of PNG figures under `assets/img/blog/<slug>/`. Posts are independent, so Tasks 2 to 7 run in parallel, one agent each. Task 1 adds a checker script the post tasks run. Task C is a critic pass, run by a fresh agent on each post after its writer finishes. Task 8 wires the bibliography and the project card. Task 9 verifies the whole site.

**Tech Stack:** Jekyll (al-folio theme), kramdown, MathJax 3, jekyll-scholar, Homebrew Ruby 3.2, poppler `pdftoppm`, Python 3.

**Spec:** `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

## Global Constraints

- Build command: `export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH && bundle exec jekyll build`. System Ruby fails.
- Post tasks run in parallel in one working tree. A post task touches only `_posts/<its file>.md` and `assets/img/blog/<its slug>/`. It builds with `--disable-disk-cache -d <its own output dir>` so builds do not collide.
- Post tasks do not run `git add` or `git commit`. The orchestrator commits after the author's review (spec, Decisions 5).
- Local builds print red `Imagemagick: ... convert: command not found` lines. They are expected. Ignore them.
- Post depth: about 1,000 to 1,500 words in the body, four to six figures, one section per main idea, a References block (spec, Decisions 3).
- Post date is the paper's first arXiv date, taken from `citation_date` on the arXiv abstract page (spec, Post format).
- Captions and any raw HTML block use plain text, never `$$` math. Body markdown uses `$$ ... $$` for math (spec, Post format).
- Writing rules from `~/.claude/CLAUDE.md` apply to every sentence: short words, active voice, one idea per sentence, no "not X but Y" constructions, no em-dashes, at most two examples in a list of illustrations, no announcing what you are about to say.
- Scratch space: `/private/tmp/claude-501/-Users-snehal-PhD-career-SnehalRaj-github-io/a479dfae-c71a-45ab-94d5-88dc9bfaee48/scratchpad/`. Referred to below as `$SC`.

---

## Reference: the model post

Every post task copies the shape of `_posts/2026-09-14-train-classical-deploy-quantum.md`. Read it first. Its front matter:

```yaml
---
layout: post
title: '"Train classical, deploy quantum" requires rethinking generalization'
date: 2026-09-14 10:00:00+05:30
description: A converged moment-matching loss does not tell you whether a quantum generative model generalizes. We prove why, and we measure it across thirteen models at up to 30 qubits.
tags: quantum-machine-learning generative-models
categories: research
related_posts: false
related_publications: raj2026tcdq
mathjax: true
toc:
  beginning: true
---
```

Its figure pattern, used once per figure:

```html
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/fig_mechanism.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) IQP at N = 16: the MMD² falls by an order of magnitude while coverage stays at the random-bits floor. (b) A likelihood-trained transformer: the NLL falls and coverage rises to the finite-sample ceiling.
</div>
```

For a narrow figure, replace `col-sm` with `col-sm-8 mx-auto` so it does not stretch.

Its section order: an opening paragraph that names coauthors and links the paper, then `## The setup`, `## <method or theorem>`, `## The benchmark` or `## Results`, `## What this changes`. Use `##` for sections and `###` for subsections. The layout adds the title, the date, the table of contents, and the References block.

---

## Reference: getting the paper source

```bash
SC=/private/tmp/claude-501/-Users-snehal-PhD-career-SnehalRaj-github-io/a479dfae-c71a-45ab-94d5-88dc9bfaee48/scratchpad
mkdir -p "$SC/<slug>/paper" "$SC/<slug>/png"
curl -sL "https://arxiv.org/e-print/<arxiv-id>" -o "$SC/<slug>/paper/src.tar.gz"
cd "$SC/<slug>/paper" && tar xzf src.tar.gz && grep -l '\\documentclass' *.tex
```

If `tar` fails, the e-print may be a single gzipped `.tex`: run `gunzip -c src.tar.gz > main.tex`.

To map the paper, run:

```bash
grep -nE 'section\{|begin\{abstract\}|begin\{theorem\}|begin\{lemma\}|begin\{definition\}|caption\{|label\{fig|includegraphics' main.tex | cut -c1-240
```

Then read the abstract, the introduction, the method section, the main results, the conclusion, and every figure caption with `sed -n 'A,Bp' main.tex`. Read the whole paper if it is under 1,500 lines. Do not write from the abstract alone.

Figure date:

```bash
curl -sL "https://arxiv.org/abs/<arxiv-id>" | grep -oE '<meta name="citation_(title|date)" content="[^"]*"'
```

Figure conversion, one line per chosen figure:

```bash
pdftoppm -png -r 170 -singlefile "$SC/<slug>/paper/<path>/<name>.pdf" "$SC/<slug>/png/<name>"
```

If a figure is a PNG or JPG in the source, copy it as is. If a figure is TikZ drawn inside the `.tex`, skip it; do not compile LaTeX. Then:

```bash
mkdir -p /Users/snehal/PhD/career/SnehalRaj.github.io/assets/img/blog/<slug>
cp "$SC/<slug>/png/"*.png /Users/snehal/PhD/career/SnehalRaj.github.io/assets/img/blog/<slug>/
```

Keep each PNG under 400 KB. If one is larger, rerun `pdftoppm` at `-r 120`.

---

## Reference: building and checking one post

```bash
cd /Users/snehal/PhD/career/SnehalRaj.github.io
export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH
SC=/private/tmp/claude-501/-Users-snehal-PhD-career-SnehalRaj-github-io/a479dfae-c71a-45ab-94d5-88dc9bfaee48/scratchpad
bundle exec jekyll build --disable-disk-cache -d "$SC/site-<slug>" > "$SC/build-<slug>.log" 2>&1; echo "exit $?"
grep -iE 'error|warn|liquid' "$SC/build-<slug>.log" | grep -v Imagemagick
python3 bin/check_post.py "$SC/site-<slug>" <year>/<slug> <bibkey>
```

The build must exit 0, the grep must print nothing, and the checker must print `PASS` on every line. If the checker fails, fix the post and rerun. Do not edit the checker.

---

### Task 1: Post checker script

**Files:**
- Create: `bin/check_post.py`

**Interfaces:**
- Produces: `python3 bin/check_post.py <site_dir> <year>/<slug> <bibkey>`. Exit code 0 when every check passes, 1 otherwise. Tasks 2 to 7 and Task 9 run it.

- [ ] **Step 1: Write the checker**

```python
#!/usr/bin/env python3
"""Check one built blog post. Usage: check_post.py SITE_DIR YEAR/SLUG BIBKEY"""
import html
import os
import re
import sys


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    site, path, bibkey = sys.argv[1:]
    page = os.path.join(site, "blog", path, "index.html")
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + label)
        ok = ok and cond

    check(os.path.isfile(page), f"page exists: {page}")
    if not os.path.isfile(page):
        return 1
    t = open(page, encoding="utf-8").read()

    check(not re.search(r"\{%|\{\{", t), "no leftover Liquid tags")
    check("tex-mml-chtml" in t, "MathJax script present")
    check("<h2>References</h2>" in t, "References heading present")
    check(bibkey in t, f"bibliography entry {bibkey} present")

    art = re.search(r'<div id="markdown-content">(.*?)</article>', t, re.S)
    body = art.group(1) if art else ""
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    words = len(re.findall(r"\b\w+\b", text))
    check(900 <= words <= 1900, f"body word count {words} in 900..1900")

    imgs = re.findall(r'<img[^>]+src="([^"]+)"', body)
    figs = [i for i in imgs if "/assets/img/blog/" in i]
    check(4 <= len(figs) <= 6, f"figure count {len(figs)} in 4..6")
    for src in figs:
        f = os.path.join(site, src.lstrip("/"))
        check(os.path.isfile(f), f"figure file exists: {src}")
    caps = body.count('class="caption"')
    check(caps == len(figs), f"caption count {caps} equals figure count {len(figs)}")

    check(not re.search(r'class="caption">[^<]*\$\$', body), "no $$ math inside captions")
    check(len(re.findall(r"<h2[^>]*>", body)) >= 3, "at least three h2 sections")
    check("arxiv.org/abs/" in body, "arXiv link in body")
    check(not re.search(r"—", text), "no em-dashes")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it against the existing TCDQ post to verify it passes**

```bash
cd /Users/snehal/PhD/career/SnehalRaj.github.io
export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH
bundle exec jekyll build > /dev/null 2>&1
python3 bin/check_post.py _site 2026/train-classical-deploy-quantum raj2026tcdq; echo "exit $?"
```

Expected: every line starts with `PASS`, `exit 0`.

- [ ] **Step 3: Run it against a wrong key to verify it fails**

```bash
python3 bin/check_post.py _site 2026/train-classical-deploy-quantum nosuchkey; echo "exit $?"
```

Expected: one `FAIL bibliography entry nosuchkey present` line, `exit 1`.

- [ ] **Step 4: Commit**

```bash
git add bin/check_post.py
git commit -m "bin: add a checker for built blog posts"
```

---

### Task 2: QGNN post

**Files:**
- Create: `_posts/<arxiv-date>-qgnn-weisfeiler-leman.md`
- Create: `assets/img/blog/qgnn-weisfeiler-leman/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `projects/qgnn-subspace/index.html`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2026/qgnn-weisfeiler-leman/`. Task 8 links to that URL.

Paper facts:
- Title: Scalable Message-Passing Quantum Graph Neural Networks in the Weisfeiler-Leman Hierarchy
- arXiv 2606.26873. Bib key `raj2026qgnn`. Slug `qgnn-weisfeiler-leman`.
- Authors: Snehal Raj, Brian Coyle, Léo Monbroussou, André J. Ferreira-Martins, Renato M. S. Farias, Elham Kashefi.
- Code: https://github.com/SnehalRaj/mp-qgnns
- Interactive companion: `/projects/qgnn-subspace/` (link it as `{{ '/projects/qgnn-subspace/' | relative_url }}`).
- Figures: already rendered as PNG in `projects/qgnn-subspace/figures/`. Copy the ones you use into `assets/img/blog/qgnn-weisfeiler-leman/`. Do not convert from the e-print.
- Suggested tags: `quantum-machine-learning graph-neural-networks`

- [ ] **Step 1: Read the model post and the companion page**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full. Read `projects/qgnn-subspace/index.html` with `sed -n '20,420p'` and note its section order: graph neural networks, quantum graph neural network, subspace explorer, results (TSP, QM9, CFI), permutation equivariance, trainability and readout, data loader, adjacency evolution, discussion.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=qgnn-weisfeiler-leman` and `<arxiv-id>=2606.26873`. Read the abstract, introduction, the architecture section, the Weisfeiler-Leman result, the trainability section, the three experiments, and the conclusion. Record the `citation_date`.

- [ ] **Step 3: Choose four to six figures**

Pick from `projects/qgnn-subspace/figures/`: `architecture_standalone.png` (the model), `equivariance.png`, `trainability_2panel.png` or `trainability_bound.png`, `results_combined.png` or the three of `tsp.png`, `qm9.png`, `cfi.png`. Copy them:

```bash
mkdir -p assets/img/blog/qgnn-weisfeiler-leman
cp projects/qgnn-subspace/figures/<chosen>.png assets/img/blog/qgnn-weisfeiler-leman/
```

- [ ] **Step 4: Write the post**

Create `_posts/<YYYY-MM-DD>-qgnn-weisfeiler-leman.md` with the date from Step 2. Front matter as in "Reference: the model post" with `title: Scalable Message-Passing Quantum Graph Neural Networks in the Weisfeiler-Leman Hierarchy`, `related_publications: raj2026qgnn`, and the suggested tags. The opening paragraph names the coauthors, links the arXiv page, links the code, and links the interactive companion with one sentence saying what the companion adds (the subspace explorer). Sections: `## Message passing on a quantum state`, `## Where the model sits in the Weisfeiler-Leman hierarchy`, `## Staying trainable in a particle-number subspace`, `## Results` with `### Distinguishing graphs (CFI)`, `### Molecular property prediction (QM9)`, `### Travelling salesman`, then `## What this changes`. End with one sentence that links the companion again. Every number you state must appear in the paper; quote the largest simulation size (56 qubits) and name the datasets.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=qgnn-weisfeiler-leman`, `<year>=2026`, `<bibkey>=raj2026qgnn`. Fix until every line is `PASS`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread the post once. Cut every sentence over 25 words into two. Remove any "not X but Y" shape. Confirm every caption is plain text. Rebuild and rerun the checker if you changed anything.

- [ ] **Step 7: Report**

Reply with: the post path, the date used, the word count, the list of figures, and any claim you were unsure about. Do not commit.

---

### Task 3: Adaptive Directional Gradients post

**Files:**
- Create: `_posts/2026-06-08-adaptive-directional-gradients.md`
- Create: `assets/img/blog/adaptive-directional-gradients/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2026/adaptive-directional-gradients/`. Task 8 links to that URL.

Paper facts:
- Title: Adaptive Directional Gradients for Parameterised Quantum Circuits
- arXiv 2606.09734, first posted 2026-06-08. Bib key `coyle2026adaptive`. Slug `adaptive-directional-gradients`.
- Authors: Brian Coyle, Snehal Raj, Virag Umathe, El Amine Cherrat, Elham Kashefi.
- Key ideas from the abstract: forward gradient estimators that average a tunable number of random directional derivatives; SPSA, random coordinate descent, and the parameter-shift rule as limiting cases; no ancilla or controlled gates; an adaptive optimiser named QUIVER; Hamming-weight-preserving orthogonal quantum neural networks trained at up to 60 qubits.
- Suggested tags: `quantum-machine-learning optimization`

- [ ] **Step 1: Read the model post**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=adaptive-directional-gradients` and `<arxiv-id>=2606.09734`. Read the abstract, introduction, the estimator definition, the variance or measurement-cost analysis, the QUIVER algorithm, the experiments, and the conclusion. Confirm the `citation_date` is 2026-06-08; if it differs, use the page's date in the filename and front matter.

- [ ] **Step 3: Choose and convert four to six figures**

Prefer: a schematic of the estimator family, the plot that places SPSA, random coordinate descent, and parameter shift as limiting cases, the measurement-cost or variance comparison, the 60-qubit training curves. Convert with `pdftoppm` per the reference and copy into `assets/img/blog/adaptive-directional-gradients/`.

- [ ] **Step 4: Write the post**

Create `_posts/2026-06-08-adaptive-directional-gradients.md` with front matter per "Reference: the model post", `title: Adaptive Directional Gradients for Parameterised Quantum Circuits`, `related_publications: coyle2026adaptive`, and the suggested tags. Opening paragraph: coauthors, arXiv link, code link if the paper gives one. Sections: `## The measurement cost of a gradient`, `## Forward gradients from random directions`, `## Three known optimisers as special cases`, `## QUIVER`, `## Results`, `## What this changes`. Give the definition of the estimator in one display equation with `$$` on its own lines. State how the number of directions trades variance for circuit evaluations, in words the paper supports.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=adaptive-directional-gradients`, `<year>=2026`, `<bibkey>=coyle2026adaptive`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread once. Split sentences over 25 words. Remove any "not X but Y" shape. Captions plain text. Rebuild and recheck if changed.

- [ ] **Step 7: Report**

Reply with the post path, the date used, the word count, the figures, and any uncertain claim. Do not commit.

---

### Task 4: Density QML post

**Files:**
- Create: `_posts/2024-05-30-density-quantum-machine-learning.md`
- Create: `assets/img/blog/density-quantum-machine-learning/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2024/density-quantum-machine-learning/`. Task 8 links to that URL.

Paper facts:
- Title: Training-Efficient Density Quantum Machine Learning
- arXiv 2405.20237, first posted 2024-05-30. Published in npj Quantum Information 11, 172 (2025): https://www.nature.com/articles/s41534-025-01099-6. Bib key `coyle2025training`. Slug `density-quantum-machine-learning`.
- Authors: Brian Coyle, Snehal Raj, Natansh Mathur, El Amine Cherrat, Nishant Jain, Sofiene Kazdaghli, Iordanis Kerenidis.
- Talk: QTML 2024, https://www.youtube.com/watch?v=1Dp_U6U6hGQ
- Suggested tags: `quantum-machine-learning trainability`

- [ ] **Step 1: Read the model post**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=density-quantum-machine-learning` and `<arxiv-id>=2405.20237`. The arXiv version may differ from the journal version in title and content; write from the arXiv source and say in the opening paragraph that the journal version appeared in npj Quantum Information in 2025. Read the abstract, introduction, the density model definition, the training-cost analysis, the experiments, and the conclusion.

- [ ] **Step 3: Choose and convert four to six figures**

Prefer: the density model schematic, the cost or gradient-variance comparison against a standard quantum neural network, the main benchmark plot, one scaling plot. Convert and copy into `assets/img/blog/density-quantum-machine-learning/`.

- [ ] **Step 4: Write the post**

Create `_posts/2024-05-30-density-quantum-machine-learning.md` with front matter per the reference, `title: Training-Efficient Density Quantum Machine Learning`, `related_publications: coyle2025training`, and the suggested tags. Opening paragraph: coauthors, arXiv link, journal link, talk link, and one sentence that this paper appeared on arXiv in May 2024 and in npj Quantum Information in 2025. Sections: `## Why training a quantum model is expensive`, `## Density models`, `## What the mixture buys you`, `## Results`, `## What this changes`. Define the density model in one display equation.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=density-quantum-machine-learning`, `<year>=2024`, `<bibkey>=coyle2025training`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread once. Split sentences over 25 words. Remove any "not X but Y" shape. Captions plain text. Rebuild and recheck if changed.

- [ ] **Step 7: Report**

Reply with the post path, the date used, the word count, the figures, and any uncertain claim. Do not commit.

---

### Task 5: QuIC post

**Files:**
- Create: `_posts/<arxiv-date>-quic-compound-adapters.md`
- Create: `assets/img/blog/quic-compound-adapters/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2025/quic-compound-adapters/`. Task 8 links to that URL.

Paper facts:
- Title: QuIC: Quantum-Inspired Compound Adapters for Parameter Efficient Fine-Tuning
- arXiv 2502.06916 (February 2025; read the exact `citation_date`). Bib key `raj2025quic`. Slug `quic-compound-adapters`.
- Authors: Snehal Raj, Brian Coyle.
- Key ideas from the abstract: adapter modules with under 0.02% memory footprint, orthogonal weights that preserve pretrained representations, compound (Hamming-weight) structure, evaluated on LLaMA and vision transformers, over 40x compression against LoRA in advanced configurations.
- Suggested tags: `parameter-efficient-fine-tuning quantum-inspired`

- [ ] **Step 1: Read the model post**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=quic-compound-adapters` and `<arxiv-id>=2502.06916`. Read the abstract, introduction, the adapter construction (orthogonal layers, compound matrices, Hamming-weight subspaces), the parameter-count analysis, the experiments on language and vision models, and the conclusion. Record the `citation_date`.

- [ ] **Step 3: Choose and convert four to six figures**

Prefer: the adapter schematic, a figure explaining the compound matrix or Hamming-weight structure, the parameter-count versus accuracy plot, the main LLaMA and vision results. Convert and copy into `assets/img/blog/quic-compound-adapters/`.

- [ ] **Step 4: Write the post**

Create `_posts/<YYYY-MM-DD>-quic-compound-adapters.md` with front matter per the reference, `title: 'QuIC: Quantum-Inspired Compound Adapters for Parameter Efficient Fine-Tuning'` (quoted, because of the colon), `related_publications: raj2025quic`, and the suggested tags. Opening paragraph: coauthor, arXiv link, code link if the paper gives one. Sections: `## Fine-tuning with almost no new parameters`, `## Orthogonal adapters`, `## Compound adapters`, `## Results`, `## What this changes`. Define the compound matrix in one display equation.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=quic-compound-adapters`, `<year>=2025`, `<bibkey>=raj2025quic`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread once. Split sentences over 25 words. Remove any "not X but Y" shape. Captions plain text. Rebuild and recheck if changed.

- [ ] **Step 7: Report**

Reply with the post path, the date used, the word count, the figures, and any uncertain claim. Do not commit.

---

### Task 6: Bayesian orthogonal neural networks post

**Files:**
- Create: `_posts/<arxiv-date>-bayesian-orthogonal-anomaly-detection.md`
- Create: `assets/img/blog/bayesian-orthogonal-anomaly-detection/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2025/bayesian-orthogonal-anomaly-detection/`. Task 8 links to that URL.

Paper facts:
- Title: Bayesian Quantum Orthogonal Neural Networks for Anomaly Detection
- arXiv 2504.18103 (April 2025; read the exact `citation_date`). Presented at IEEE Quantum Week 2025. Bib key `mathur2025bayesian`. Slug `bayesian-orthogonal-anomaly-detection`.
- Authors: Natansh Mathur, Brian Coyle, Nishant Jain, Snehal Raj, Akshat Tandon, Jasper Simon Krauser, Rainer Stoessel.
- Suggested tags: `quantum-machine-learning anomaly-detection`

- [ ] **Step 1: Read the model post**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=bayesian-orthogonal-anomaly-detection` and `<arxiv-id>=2504.18103`. Read the abstract, introduction, the orthogonal network and its Bayesian treatment, the anomaly-detection setup and data, the experiments, and the conclusion. Record the `citation_date`.

- [ ] **Step 3: Choose and convert four to six figures**

Prefer: the model schematic, the Bayesian inference or uncertainty figure, the anomaly-detection result, a comparison against classical baselines. Convert and copy into `assets/img/blog/bayesian-orthogonal-anomaly-detection/`.

- [ ] **Step 4: Write the post**

Create `_posts/<YYYY-MM-DD>-bayesian-orthogonal-anomaly-detection.md` with front matter per the reference, `title: Bayesian Quantum Orthogonal Neural Networks for Anomaly Detection`, `related_publications: mathur2025bayesian`, and the suggested tags. Opening paragraph: coauthors, arXiv link, one sentence that the paper was presented at IEEE Quantum Week 2025. Sections: `## The problem`, `## Orthogonal quantum neural networks`, `## Making them Bayesian`, `## Results`, `## What this changes`.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=bayesian-orthogonal-anomaly-detection`, `<year>=2025`, `<bibkey>=mathur2025bayesian`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread once. Split sentences over 25 words. Remove any "not X but Y" shape. Captions plain text. Rebuild and recheck if changed.

- [ ] **Step 7: Report**

Reply with the post path, the date used, the word count, the figures, and any uncertain claim. Do not commit.

---

### Task 7: Quantum Deep Hedging post

**Files:**
- Create: `_posts/2023-03-29-quantum-deep-hedging.md`
- Create: `assets/img/blog/quantum-deep-hedging/*.png`
- Read: `_posts/2026-09-14-train-classical-deploy-quantum.md`, `docs/superpowers/specs/2026-09-14-paper-blog-posts-design.md`

**Interfaces:**
- Consumes: `bin/check_post.py` from Task 1.
- Produces: the post at `/blog/2023/quantum-deep-hedging/`. Task 8 links to that URL.

Paper facts:
- Title: Quantum Deep Hedging
- arXiv 2303.16585, first posted 2023-03-29. Published in Quantum 7, 1191 (2023): https://quantum-journal.org/papers/q-2023-11-29-1191/. Bib key `cherrat2023quantum`. Slug `quantum-deep-hedging`.
- Authors: El Amine Cherrat, Snehal Raj, Iordanis Kerenidis, Abhishek Shekhar, Ben Wood, Jon Dee, Shouvanik Chakrabarti, Richard Chen, Dylan Herman, Shaohan Hu, Pierre Minssen, Ruslan Shaydulin, Yue Sun, Romina Yalovetzky, Marco Pistoia. Name the first three and say "and colleagues at QC Ware and JPMorgan Chase" for the rest.
- Suggested tags: `quantum-machine-learning finance reinforcement-learning`

- [ ] **Step 1: Read the model post**

Read `_posts/2026-09-14-train-classical-deploy-quantum.md` in full.

- [ ] **Step 2: Fetch and read the paper source**

Follow "Reference: getting the paper source" with `<slug>=quantum-deep-hedging` and `<arxiv-id>=2303.16585`. Read the abstract, introduction, the deep hedging setup, the quantum policy and value models (orthogonal and compound layers), the reinforcement-learning algorithms, the hardware experiments, and the conclusion.

- [ ] **Step 3: Choose and convert four to six figures**

Prefer: the hedging setup, the quantum model architecture, a training or P&L distribution plot, the quantum hardware result. Convert and copy into `assets/img/blog/quantum-deep-hedging/`.

- [ ] **Step 4: Write the post**

Create `_posts/2023-03-29-quantum-deep-hedging.md` with front matter per the reference, `title: Quantum Deep Hedging`, `related_publications: cherrat2023quantum`, and the suggested tags. Opening paragraph: authors as instructed, arXiv link, journal link, and one sentence that the paper appeared on arXiv in March 2023 and in Quantum in November 2023. Sections: `## Hedging as a learning problem`, `## Quantum models for the policy and the value`, `## Training`, `## Results, including on hardware`, `## What this changes`.

- [ ] **Step 5: Build and check**

Follow "Reference: building and checking one post" with `<slug>=quantum-deep-hedging`, `<year>=2023`, `<bibkey>=cherrat2023quantum`.

- [ ] **Step 6: Self-edit against the writing rules**

Reread once. Split sentences over 25 words. Remove any "not X but Y" shape. Captions plain text. Rebuild and recheck if changed.

- [ ] **Step 7: Report**

Reply with the post path, the date used, the word count, the figures, and any uncertain claim. Do not commit.

---

### Task C: Anti-slop critic pass (run once per post, six times, by a fresh agent each time)

Parameters: `<post-file>` (the path from the writer's report), `<slug>`, `<year>`, `<bibkey>` (from the writer's task).

**Files:**
- Modify: `_posts/<post-file>` (prose only)
- Read: `~/.claude/CLAUDE.md`, `$SC/<slug>/paper/main.tex` (or the companion page for QGNN)

**Interfaces:**
- Consumes: a post that passes `bin/check_post.py`.
- Produces: the same post with AI-writing tells removed, still passing the checker.

- [ ] **Step 1: Read the post and the rules**

Read `_posts/<post-file>` in full. Read `~/.claude/CLAUDE.md` in full. Read the paper source so you can check claims.

- [ ] **Step 2: Invoke the humanizer skill**

Invoke the `humanizer` skill and apply its full checklist to the post's prose: the opening paragraph, every section body, and every caption. Leave the front matter, the figure include lines, the display equations, and the section order alone.

- [ ] **Step 3: Hunt these tells one by one**

Search the post for each item and fix every hit:

- Em-dashes (`—`) and spaced hyphens used as dashes. Replace with a full stop, a comma, or a rewrite.
- The "not X but Y", "not X, it's Y", "X isn't the problem, Y is", "rather than X, Y" shells. Rewrite as a plain statement.
- Lists of exactly three adjectives, nouns, or examples that were padded to three. Cut to two or expand with real content from the paper.
- Announcements: "In this post", "Let's dive in", "Here's the thing", "It's worth noting", "Notably", "Importantly", "Crucially", "In summary", "Overall", "Ultimately".
- Vocabulary: delve, crucial, pivotal, landscape, tapestry, leverage, harness, robust, seamless, underscore, testament, showcase, foster, navigate, unlock, elevate, game-changing, groundbreaking, novel, exciting, powerful, elegant, intriguing.
- Vague attribution: "researchers have shown", "it is widely believed", "experts agree". Name the source or cut.
- Two paragraphs in a row that end on a punchline. Flatten one.
- Neighbouring sentences of the same length and shape. Vary them.
- Passive voice where the actor is known. Name the actor.
- Sentences over 25 words. Split.
- Bold on whole sentences. Keep bold to the first few words of a bullet, or remove it.
- Hedges stacked on one claim: "may potentially", "could possibly".
- Any number, dataset name, model name, or result that you cannot find in the paper source. Do not rewrite it; list it in the report.

- [ ] **Step 4: Rebuild and check**

```bash
cd /Users/snehal/PhD/career/SnehalRaj.github.io
export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH
SC=/private/tmp/claude-501/-Users-snehal-PhD-career-SnehalRaj-github-io/a479dfae-c71a-45ab-94d5-88dc9bfaee48/scratchpad
bundle exec jekyll build --disable-disk-cache -d "$SC/site-<slug>" > "$SC/build-<slug>-critic.log" 2>&1; echo "exit $?"
python3 bin/check_post.py "$SC/site-<slug>" <year>/<slug> <bibkey>
```

Expected: `exit 0` and every line `PASS`. If the word count dropped under 900, restore substance from the paper, in plain sentences, until it passes.

- [ ] **Step 5: Report**

Reply with: a numbered list of the edits you made, each as the old phrase and the new phrase; the list of claims you could not verify in the source; and the final word count. Do not commit.

---

### Task 8: Wire the bibliography and the project card

Run after Tasks 2 to 7 are done and their post filenames are known.

**Files:**
- Modify: `_bibliography/papers.bib` (six entries)
- Modify: `_projects/qgnn.md`

**Interfaces:**
- Consumes: the six post URLs from Tasks 2 to 7.
- Produces: a Blog button on each of the six publication entries; the QGNN project card opens the QGNN post.

- [ ] **Step 1: Add `blog=` fields**

In each of the six entries, insert one line after the `html={...},` line, in this form:

```
  blog={/blog/2026/qgnn-weisfeiler-leman/},
```

Keys and URLs:

| Key | blog value |
|---|---|
| raj2026qgnn | /blog/2026/qgnn-weisfeiler-leman/ |
| coyle2026adaptive | /blog/2026/adaptive-directional-gradients/ |
| coyle2025training | /blog/2024/density-quantum-machine-learning/ |
| raj2025quic | /blog/2025/quic-compound-adapters/ |
| mathur2025bayesian | /blog/2025/bayesian-orthogonal-anomaly-detection/ |
| cherrat2023quantum | /blog/2023/quantum-deep-hedging/ |

If a post's year differs from this table (a different arXiv date), use the year from the post's filename.

- [ ] **Step 2: Repoint the project card**

Replace the whole of `_projects/qgnn.md` with:

```markdown
---
layout: page
title: Quantum Graph Neural Networks
description: Scalable message-passing quantum GNNs in the Weisfeiler–Leman hierarchy. A blog post on the architecture and results, with a link to the interactive subspace explorer.
img: assets/img/qgnn.jpg
importance: 1
category: work
redirect: /blog/2026/qgnn-weisfeiler-leman/
github: https://github.com/SnehalRaj/mp-qgnns
---

This card links to the blog post for **Scalable Message-Passing Quantum Graph
Neural Networks in the Weisfeiler–Leman Hierarchy**. The post links to the
interactive project page with the subspace explorer. If you are not redirected,
open [the post](/blog/2026/qgnn-weisfeiler-leman/).
```

- [ ] **Step 3: Build and verify**

```bash
cd /Users/snehal/PhD/career/SnehalRaj.github.io
export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH
bundle exec jekyll build > /dev/null 2>&1; echo "exit $?"
grep -c '>Blog</a>' _site/publications/index.html
grep -o 'href="/blog/2026/qgnn-weisfeiler-leman/"' _site/projects/index.html | head -1
```

Expected: `exit 0`, Blog count `7`, and the project href printed once.

- [ ] **Step 4: Do not commit yet**

The orchestrator commits after the author's review.

---

### Task 9: Whole-site verification and review handoff

**Files:**
- Read only.

- [ ] **Step 1: Build and run the checker on all seven posts**

```bash
cd /Users/snehal/PhD/career/SnehalRaj.github.io
export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH
bundle exec jekyll build > /dev/null 2>&1; echo "exit $?"
for p in "2026/train-classical-deploy-quantum raj2026tcdq" "2026/qgnn-weisfeiler-leman raj2026qgnn" "2026/adaptive-directional-gradients coyle2026adaptive" "2024/density-quantum-machine-learning coyle2025training" "2025/quic-compound-adapters raj2025quic" "2025/bayesian-orthogonal-anomaly-detection mathur2025bayesian" "2023/quantum-deep-hedging cherrat2023quantum"; do set -- $p; echo "== $1"; python3 bin/check_post.py _site "$1" "$2" | grep -c FAIL; done
```

Expected: `exit 0` and `0` after every `==` line. Adjust a path if a post used a different arXiv date.

- [ ] **Step 2: Check the blog index order**

```bash
grep -oE 'href="/blog/20[0-9]{2}/[a-z-]+/"' _site/blog/index.html | uniq
```

Expected: seven distinct URLs, newest first: TCDQ, QGNN, adaptive gradients, Bayesian, QuIC, density QML, deep hedging. If pagination splits them across pages, also check `_site/blog/page/2/index.html`.

- [ ] **Step 3: Browser spot check**

Serve `_site` with `python3 -m http.server 4321 --bind 127.0.0.1` from `_site`, open each post URL once, and confirm the title, the table of contents, one figure, and one rendered equation. Stop the server afterwards.

- [ ] **Step 4: Hand the posts to the author**

Give the author the seven URLs and each agent's list of uncertain claims. Wait for corrections. Apply them. Then commit everything in one commit and push.
