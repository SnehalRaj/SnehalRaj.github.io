# Paper blog posts: design

Date: 2026-09-14
Status: approved in chat, pending spec review

## Goal

Give every research paper one write-up, in one place, in one format. The place is the Jekyll blog under `/blog/`. The format is the TCDQ post published on 2026-09-14 at `_posts/2026-09-14-train-classical-deploy-quantum.md`.

## Decisions

1. The Jekyll blog is the single home for paper write-ups. The standalone QGNN page at `projects/qgnn-subspace/` stays as an interactive companion and is linked from the QGNN post.
2. Six papers get a post: QGNN, Adaptive Directional Gradients, Density QML, QuIC, Bayesian orthogonal NNs, Quantum Deep Hedging. TCDQ already has one.
3. Every post has the same depth as the TCDQ post: about 1,000 to 1,500 words, four to six figures from the arXiv source, one section per main idea, a References block.
4. The projects page keeps its one card. The card links to the QGNN post instead of redirecting to the standalone page.
5. Nothing is pushed until the author has read every post.

## Post format

Each post is a markdown file in `_posts/` named `YYYY-MM-DD-<slug>.md`, where the date is the paper's first arXiv date. Front matter:

```yaml
layout: post
title: <paper title>
date: <arXiv date> 10:00:00+05:30
description: <one or two sentences>
tags: <two or three kebab-case tags>
categories: research
related_posts: false
related_publications: <bibliography key>
mathjax: true
toc:
  beginning: true
```

The first paragraph names the coauthors, links the arXiv page, and, where one exists, the journal version and the code. The first paragraph of a post about an older paper says when the paper appeared, so a reader is not misled by the date line.

Body sections follow the paper's own structure: setup, method or theorem, results, what it changes. Sentences follow the site owner's writing rules in the global CLAUDE.md.

Figures come from the arXiv e-print tarball, converted with `pdftoppm -png -r 170`, and live under `assets/img/blog/<slug>/`. Each figure uses the existing al-folio pattern:

```html
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/<slug>/<name>.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    <caption text, no LaTeX math>
</div>
```

Math in the markdown body uses `$$ ... $$`. Captions and other raw HTML blocks use plain text, since kramdown does not convert math inside HTML.

## The six posts

| Paper | Slug | Bib key | Source | Post date |
|---|---|---|---|---|
| Scalable Message-Passing Quantum Graph Neural Networks in the Weisfeiler-Leman Hierarchy | qgnn-weisfeiler-leman | raj2026qgnn | arXiv 2606.26873; figures in `projects/qgnn-subspace/figures/` | arXiv date |
| Adaptive Directional Gradients for Parameterised Quantum Circuits | adaptive-directional-gradients | coyle2026adaptive | arXiv 2606.09734 | 2026-06-08 |
| Training-Efficient Density Quantum Machine Learning | density-quantum-machine-learning | coyle2025training | arXiv 2405.20237; npj QI 11, 172 (2025) | 2024-05-30 |
| QuIC: Quantum-Inspired Compound Adapters for Parameter Efficient Fine-Tuning | quic-compound-adapters | raj2025quic | arXiv 2502.06916 | arXiv date |
| Bayesian Quantum Orthogonal Neural Networks for Anomaly Detection | bayesian-orthogonal-anomaly-detection | mathur2025bayesian | arXiv 2504.18103 | arXiv date |
| Quantum Deep Hedging | quantum-deep-hedging | cherrat2023quantum | arXiv 2303.16585; Quantum 7, 1191 (2023) | 2023-03-29 |

Post dates marked "arXiv date" are read from the arXiv abstract page when the post is written.

The QGNN post links to `/projects/qgnn-subspace/` in its first section as the interactive companion, and again at the end. Its figures can be copied from the existing companion folder rather than converted from the e-print.

## Other file changes

- `_bibliography/papers.bib`: add `blog={/blog/<year>/<slug>/}` to each of the six entries, in the same position as in the TCDQ entry.
- `_projects/qgnn.md`: change `redirect` to `/blog/2026/qgnn-weisfeiler-leman/` and update the card text to say it links to the post.

## Out of scope

- The distill layout.
- Porting the QGNN companion into Jekyll.
- Posts for AutoSumm, the patent, and the two theses.
- Changes to the talks, teaching, or news pages.

## Verification

After each post: build with Homebrew Ruby 3.2 (`export PATH=/opt/homebrew/opt/ruby@3.2/bin:$PATH && bundle exec jekyll build`), confirm the post renders at its URL with no leftover Liquid, that every figure resolves, that MathJax loads, and that the References block shows the right entry. Serve `_site` locally and check the page in a browser. Local builds print ImageMagick errors, which are expected; CI generates the responsive images.

After all six: confirm the blog index lists seven posts in date order, the publications page shows a Blog button on seven entries, and the projects card opens the QGNN post.

## Review and delivery

Each post is drafted from the LaTeX source, then handed to the author for an accuracy read. Corrections are applied in place. When all six are approved, everything is committed and pushed in one go.
