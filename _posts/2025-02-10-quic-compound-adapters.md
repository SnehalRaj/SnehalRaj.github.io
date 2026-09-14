---
layout: post
title: 'QuIC: Quantum-Inspired Compound Adapters for Parameter Efficient Fine-Tuning'
date: 2025-02-10 10:00:00+05:30
description: An adapter built from one small orthogonal matrix and its compound matrices fine-tunes DeBERTa, DINOv2, and LLaMA with under 0.02% of the base model's memory, over 40 times smaller than LoRA.
tags: parameter-efficient-fine-tuning quantum-inspired
categories: research
related_posts: false
related_publications: raj2025quic
mathjax: true
toc:
  beginning: true
---

Our preprint, written with Brian Coyle at QC Ware, asks how few parameters a fine-tuning adapter can have and still do useful work. We build the adapter from one small orthogonal matrix and its compound matrices, a structure taken from Hamming-weight preserving quantum circuits. It fine-tunes DeBERTa, DINOv2, and LLaMA with less than 0.02% of the base model's memory. The paper is on [arXiv](https://arxiv.org/abs/2502.06916).

## Fine-tuning with almost no new parameters

A foundation model holds weight matrices $$W^* \in \mathbb{R}^{d \times d}$$ in its attention and feed-forward layers. Full fine-tuning updates all of them. For a model with billions of parameters, that costs too much memory and time. Parameter-efficient fine-tuning (PEFT) freezes $$W^*$$ and trains a small adapter $$\Delta W$$ instead. Additive methods set $$W_{\mathrm{adapt}} = W^* + \Delta W$$. Multiplicative methods set $$W_{\mathrm{adapt}} = \Delta W \, W^*$$.

LoRA is the best-known additive method. It writes $$\Delta W = \alpha W_{\mathrm{up}} W_{\mathrm{down}}$$ with two thin matrices of rank $$r \ll d$$. On DeBERTaV3-base, LoRA at rank 8 still trains 1.33 million parameters. Some settings need far less. Think of a personal model that lives on a phone, or a server that holds thousands of task-specific adapters at once.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/overview_adapters.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Four ways to fine-tune one weight matrix, with trainable parameters in dark green. (a) Full fine-tuning. (b) LoRA adds a product of two thin matrices. (c) OFT multiplies W* by a block-diagonal orthogonal matrix. (d) QuIC trains only the small base matrix at the top left of each block and computes the compound blocks from it.
</div>

## Orthogonal adapters

Orthogonal fine-tuning (OFT) is a multiplicative method. Its adapter satisfies $$\Delta W^\top \Delta W = \mathbb{1}$$. An orthogonal map keeps the norms of feature vectors and the angles between them. The fine-tuned layer keeps the spectral properties of $$W^*$$. The OFT authors argue that this protects the pretrained knowledge.

OFT keeps $$\Delta W$$ orthogonal with the Cayley transform. For a skew-symmetric matrix $$Q$$, the matrix $$(\mathbb{1} + Q)(\mathbb{1} - Q)^{-1}$$ is orthogonal with determinant one. We update $$Q$$ during training, and the adapter stays orthogonal at every step. To cut parameters, OFT makes $$\Delta W$$ block-diagonal with $$r$$ blocks of size $$d/r$$. That costs $$O(d^2/r)$$ parameters, or $$O(d^2/r^2)$$ if the blocks share weights. BOFT writes the adapter as a product of sparse butterfly factors and reaches $$O(d \log d)$$.

Our adapter starts from OFT and compresses each block further.

## Compound adapters

Take a base matrix $$A \in \mathbb{R}^{n \times n}$$. Its compound matrix of order $$k$$ is the $$\binom{n}{k} \times \binom{n}{k}$$ matrix whose entries are the $$k \times k$$ minors of $$A$$:

$$
\mathcal{C}_k := A^{(k)}, \qquad A^{(k)}_{IJ} := \det(A_{IJ}), \qquad I, J \subseteq [n], \quad \lvert I \rvert = \lvert J \rvert = k.
$$

Here $$A_{IJ}$$ is the submatrix of $$A$$ with rows $$I$$ and columns $$J$$. The first compound is $$A$$ itself. The second has $$\binom{n}{2}$$ rows, so a $$44 \times 44$$ base matrix defines a $$946 \times 946$$ compound.

A circuit of fermionic beam splitter gates preserves Hamming weight. On the weight-one part of its input it applies some orthogonal matrix $$A$$. Kerenidis et al. showed that on the weight-$$k$$ part it applies the compound matrix $$A^{(k)}$$.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/hw_compound_circuit.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A Hamming-weight preserving circuit and its matrix. Left: loaders write data into the weight-1, weight-2, and weight-3 subspaces, then one trainable layer acts on all of them. Right: that layer is a block-diagonal unitary U. Each block is a compound matrix of one base matrix, and it acts on the states of one Hamming weight.
</div>

We call the adapters quantum-inspired because, for a constant order $$k$$, a classical computer can apply $$A^{(k)}$$ directly to each subspace.

A QuIC adapter copies this block structure. Split $$\Delta W_Q$$ into $$N$$ diagonal blocks of size $$b = d/N$$. Inside block $$i$$, place the direct sum of the compounds of one base matrix $$A_i$$ up to a maximum order $$K$$. Then pad with an identity to fill the block:

$$
\Delta W_Q = \bigoplus_{i=1}^{N} \Delta W_Q^i, \qquad
\Delta W_Q^i := \begin{bmatrix} \bigoplus_{k=1}^{K} A_i^{(k)} & 0 \\ 0 & \mathbb{1}_{b - d_{\mathrm{comp}}} \end{bmatrix}, \qquad
d_{\mathrm{comp}} := \sum_{k=1}^{K} \binom{n}{k}.
$$

The base size $$n$$ is the largest integer with $$d_{\mathrm{comp}} \le b$$. For $$d = 1024$$, one block, and $$K = 2$$, that gives $$n = 44$$: a $$44 \times 44$$ block for $$A$$, a $$946 \times 946$$ block for $$A^{(2)}$$, and 34 padded dimensions. With $$K = 1$$ the adapter is OFT.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/adapter_configs.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Three QuIC configurations. Left: C1 only with four blocks, which is OFT when A is orthogonal. Middle: C1 plus C2 with four blocks. Right: C1 plus C2 plus C3 with two blocks. The trailing dimensions of each block hold an identity matrix and are not trained.
</div>

If $$A$$ is orthogonal, every compound $$A^{(k)}$$ is orthogonal. That follows from the Cauchy-Binet formula. The identity padding is orthogonal too, so the whole adapter is. The Cayley parametrization keeps it so during training.

Every trainable parameter lives in the base matrices. With orthogonality, block $$i$$ trains $$n(n-1)/2$$ numbers, so the adapter trains $$N n(n-1)/2$$ in total. A larger $$K$$ forces a smaller $$n$$, so higher orders mean fewer parameters.

The forward pass costs $$O(d^2/N)$$. Building the compounds from $$A$$ is a one-time cost, polynomial in $$n$$ for fixed $$K$$.

## Results

We fine-tune three backbones on four kinds of task: DeBERTaV3-base on language, DINOv2-large on vision, and LLaMA-7B on math and reading comprehension. Unless we say otherwise, the QuIC configuration is $$\mathcal{C}_1 \oplus \mathcal{C}_2$$ with three blocks, orthogonality on, and no weight sharing across blocks.

We combine accuracy and parameter count in one Pareto score. It is the accuracy gain over the zero-shot baseline, divided by $$\log_{10}$$ of the parameter count in thousands.

### Language

On five GLUE tasks, the QuIC adapter trains 0.03 million parameters and stores them in 0.12 MB. LoRA at rank 8 needs 1.33 million and 5.3 MB, so QuIC is over 40 times smaller. Full fine-tuning trains 184 million, so the adapter is under 0.02% of the base model. QuIC's mean score is 85.57, against 86.30 for LoRA and 88.50 for BOFT. Its Pareto score of 28.14 is the highest in the table, and it sits on the Pareto frontier with LoKr, AdaLoRA, and BOFT.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/pareto_glue.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Mean GLUE score against adapter memory on a log scale, for DeBERTaV3-base. Blue points lie on the Pareto frontier. QuIC (star) is the smallest adapter on the frontier at 0.12 MB.
</div>

### Vision

On five VTAB-1k tasks, QuIC trains 0.13 million parameters against 1.77 million for LoRA at rank 4. Each task gives 1,000 labeled images for training and validation, and we report accuracy on the full test set. Mean accuracy is 82.61; LoRA gets 83.24 and BOFT 83.82. On CIFAR-100 QuIC scores 87.5, about ten points above every other method in the table.

### Math and reasoning

On LLaMA-7B we use four blocks per adapter, which gives 0.5 million parameters. LoRA at rank 32 has 58.1 million on the math tasks and QuanTA has 13.3 million. On four MATH10K word-problem sets, QuIC averages 52.1, against 65.6 for LoRA and 64.5 for QuanTA. It is best on AQuA at 24.8 and well behind on GSM8K. DROP is closer: 52.6 for QuIC, 54.0 for LoRA, 59.5 for QuanTA. The gap to LoRA is under one point on GLUE and about thirteen points on the math sets. That is the trade at this level of compression.

### What the ablations say

We ran ablations on STS-B, one of the GLUE tasks.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/config_params_accuracy.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    STS-B accuracy (line, right axis) and trainable parameters (bars, left axis, log scale) for seven compound configurations. Every configuration that includes C1 scores above 88. Every configuration without it scores near 40.
</div>

Without the first-order compound, nothing else helps. $$\mathcal{C}_1$$ alone, which is OFT, scores 91.68 with 1.8 million parameters. Add $$\mathcal{C}_2$$ and the count drops to 33 thousand, for a score of 88.85. Add $$\mathcal{C}_3$$ too and it drops to 13 thousand, for 88.48. Remove $$\mathcal{C}_1$$ and the score falls to about 40, whatever else is present. We think the gradient has trouble reaching $$A$$ through the determinant when $$A$$ itself is absent.

Orthogonality matters as much. Averaged over the seven configurations, orthogonal adapters score 68.70 and non-orthogonal ones 27.32. For $$\mathcal{C}_1 \oplus \mathcal{C}_2$$ the constraint lifts the score from 33.29 to 88.85.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quic-compound-adapters/orthogonality_stsb.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    STS-B accuracy with and without the orthogonality constraint, for each compound configuration. The constraint helps in every case. It is decisive whenever a higher-order compound is present.
</div>

We also replaced the determinant on the minors with the elementwise maximum and with the average. Both do far worse. Our reading is that max and avg break orthogonality, which a multiplicative adapter needs.

Once a higher-order compound is in the adapter, the parameter count drops sharply, and we cannot tune it finely. To add capacity back, we multiply several adapters together. Four $$\mathcal{C}_1 \oplus \mathcal{C}_2$$ adapters in a product have 0.14 million parameters. They lift STS-B from 90.16 to 91.44 and CoLA from 64.57 to 65.83, while RTE and MRPC fall a little.

## What this changes

QuIC runs at parameter budgets below any other method in our tables. BOFT gives the best mean accuracy on GLUE and VTAB with 0.75 and 1.99 million parameters. At 0.03 and 0.13 million, QuIC keeps most of that accuracy. OFT is QuIC at $$K = 1$$, so one framework covers both ends.

The construction also gives a direct route to quantum hardware. Fixed Hamming-weight loaders write the input into the weight-1 to weight-$$K$$ subspaces, and a layer of beam splitter gates applies the compounds. Train the gate angles instead of the Cayley parameters, and the trained adapter is already a compiled circuit. Other quantum-inspired adapters lack this. QuanTA's tensors have no efficient general compilation to unitaries. QPA reads $$2^N$$ outcome probabilities from a circuit. For a billion adapter parameters, that needs about 10,000 billion shots at 0.01 accuracy.

We left two things for later. One is additive QuIC adapters in the style of LoRA. The other is larger $$K$$, where the compound circuits become hard to simulate classically and a quantum implementation could pay off.
