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

Our new preprint, written with Natansh Mathur and Alejandro Perdomo-Ortiz at QC Ware, asks a question that the train-classical, deploy-quantum literature has mostly skipped. Once the classical loss has converged, does the quantum circuit generalize? The paper is on [arXiv](https://arxiv.org/abs/2608.31117).

## The setup

A quantum circuit Born machine prepares a parametrized state and samples it in the computational basis. For some circuit families, that sampling is believed to be classically hard. Training such a circuit on hardware is expensive. Each gradient needs many circuit runs, and barren plateaus can flatten the loss landscape.

The train-classical, deploy-quantum (TCDQ) strategy avoids this cost. The loss is evaluated and minimized on a classical computer. The quantum device only draws samples after training. This works when the loss depends on quantities that are classically tractable, even when sampling the full distribution is hard. The usual example is the squared maximum mean discrepancy, MMD², which compares the model and the data through their Pauli-Z correlators.

Prior work on TCDQ asked two questions. Can the classical loss be optimized? Can a classical surrogate reproduce the deployed model? We ask a third. Once the loss has converged, does the model produce new, valid samples?

## What generalization means here

We follow Gili et al. and score a generative model by the samples it produces. Let $$S$$ be the valid set and $$T \subset S$$ the training set. The model generalizes if its forward KL divergence to the target, $$\mathrm{KL}(p^* \,\|\, q_\theta)$$, is small. This divergence is infinite unless the model gives positive probability to every valid string. In deployment we cannot compute it, so we use two sample-based proxies.

- **Coverage** is the fraction of unseen valid strings, $$S \setminus T$$, that appear among $$Q$$ samples from the model.
- **Fidelity** is the fraction of samples that are valid.

A model that emits uniform random bits sets a no-learning floor for coverage, $$C_{\mathrm{rand}} = 1-(1-2^{-N})^Q$$.

## Moment losses cannot certify generalization

Every deployed TCDQ loss is a moment loss. It depends on the model only through a finite list of $$d$$ observable expectations. MMD² with a Gaussian-Hamming kernel is a weighted sum over all Pauli-Z correlators. A fixed-order correlator loss keeps only the correlators up to order $$L$$, so it has capacity $$d = \sum_{\ell \le L} \binom{N}{\ell} = O(N^L)$$.

Our main theorem says that such a loss has exact minimizers with almost no coverage.

**Theorem.** Let $$p^*$$ have full support on a finite valid set $$S$$, and let $$\mathcal{L}$$ be a moment loss of capacity $$d$$ with $$d+1 < \lvert S \rvert$$. Then there is an exact global minimizer $$q_{\mathrm{sparse}}$$ of the population loss, supported on at most $$d+1$$ strings, with

$$
\mathcal{L}_*(q_{\mathrm{sparse}}) = \mathcal{L}_*(p^*), \qquad
\mathrm{KL}(p^* \,\|\, q_{\mathrm{sparse}}) = \infty, \qquad
C_\infty(q_{\mathrm{sparse}}) \le \frac{d+1}{\lvert S \rvert}.
$$

The target and the sparse minimizer give the same loss value, so the loss cannot tell them apart. On the cardinality task, where the valid set holds every $$N$$-bit string of Hamming weight $$N/2$$, an order-$$L$$ correlator loss admits a minimizer with coverage $$O(N^{L+1/2} / 2^N)$$. The proof is the Boolean-cube form of the argument Arora et al. made for GANs with bounded-capacity discriminators.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/mmd_kl_demo.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Two exact minimizers of the same truncated moment loss. The distributions p<sub>good</sub> and p<sub>bad</sub> match every correlator through order L, yet their support coverages are 1 and 0.07.
</div>

The minimizer is explicit. A linear program at N = 12 and L = 2 finds a distribution that matches every correlator of the uniform target through order 2 on a support of 66 strings. Its truncated loss is about 10⁻²⁸. Its coverage is 0.07 against the target's 1.00. Its forward KL is infinite.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/scaling_props.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The low-coverage minimizer scales as the theorem predicts. For N = 8 to 16 at L = 2, a linear program builds a distribution that matches every correlator of the uniform target up to order 2. Realized coverage (red) and the bound from the corollary (gray), on a log scale.
</div>

The full MMD² is different in principle. Its kernel is characteristic, so the target is the unique minimizer of the population loss. Training, however, minimizes the empirical loss against a finite training set. The exact minimizer of that empirical loss is the memorizer, the empirical training distribution, which covers zero unseen strings. Either way, the loss value alone cannot substitute for sampling the trained model.

## The benchmark

We trained thirteen generative models on the same training subsets and scored each one by free sampling.

- **Likelihood-trained:** a tensor-network Born machine (TNBM), three transformers, three GRU recurrent networks, and a restricted Boltzmann machine.
- **Moment-trained:** an IQP Born machine, a magic fermionic Born machine (FBM), a passive number-conserving FBM, an active FBM, and a classical generative moment-matching network.

We used two datasets.

- **Cardinality-constrained:** every N-bit string of Hamming weight N/2, with a uniform target, at N = 16, 20, and 30. At N = 30 we simulate full state vectors over a valid set of about 155 million strings.
- **Genomic single-nucleotide variants:** observed variant sequences, at N = 16 and 20. Here the valid set is the observed data itself.

## What we found

### Loss and coverage decouple

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/rank6_combined.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Rank correlations among MMD², coverage, and forward KL at N = 16, for the cardinality data (top) and the genomic data (bottom). Left: the two generalization measures agree. Middle and right: the moment-matching loss correlates poorly with both.
</div>

On the cardinality task, the moment-trained IQP and FBM models drive the MMD² to a low value and still fail to cover the valid set. The IQP Born machine and the TNBM reach the same MMD² within 40%, yet they cover 0.09 and 0.41 of the unseen valid strings. Coverage and forward KL rank the models almost the same way. MMD² ranks them differently from both.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/fig_mechanism.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) IQP at N = 16: the MMD² falls by an order of magnitude while coverage stays at the random-bits floor. (b) A likelihood-trained transformer: the NLL falls and coverage rises to the finite-sample ceiling. (c) Coverage against parameter count: the classical models and the TNBM improve with size, while IQP and the magic FBM stay flat. (d) Normalized coverage against N up to 30: the gap widens.
</div>

We checked the easy explanations. Enlarging the IQP circuit 18× in gate count leaves its coverage flat. Sweeping the kernel bandwidth from sharp to broad keeps IQP near the random floor. Raising the query budget lifts the likelihood-trained models toward the ceiling and leaves the moment-trained ones where they were, so the low coverage is not a finite-sampling artifact.

<div class="row mt-3">
    <div class="col-sm-9 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/tcdq/n16_grid_part1.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Where the models put their probability mass. The full space of 2¹⁶ bitstrings at N = 16, rendered as a 256 × 256 grid. Gray cells lie off the Hamming-weight-8 slice. Colored cells lie on it, with intensity proportional to sample probability. The number-conserving FBM puts all its mass on the valid slice by construction. The moment-trained models assign substantial probability outside the valid sector.
</div>

### Structure does what the loss cannot

One moment-trained model did well on the cardinality task. The passive fermionic Born machine is a matchgate circuit that only emits strings of fixed Hamming weight. Its architecture confines it to the valid set, whatever the loss does. On the genomic data, which has no fixed Hamming weight, the same model generalized as poorly as the other moment-trained models.

### The genomic data

On the genomic variants, the transformer and the RNN reached the highest coverage, with the TNBM just behind. The moment-trained models were again the weakest generators. Loss and coverage correlated a little better than on the cardinality task, so how well MMD² tracks generalization depends on the dataset. Per-locus allele frequencies, linkage disequilibrium, and PCA projections of the samples tell the same story in the appendix.

## What this changes

TCDQ has been justified by trainability and by the hardness of sampling. Both can hold for a model that never produces a new valid sample. We think generalization should be checked directly, by sampling the trained model, before anyone reads a low training loss as success.

Two directions look most promising to us. Replace moment matching with a loss that targets generalization, such as maximum likelihood or an objective with a coverage-aware term. Or build the constraint into the model, as the passive FBM does for fixed Hamming weight. Finding structure-preserving circuits for other domains, such as molecular validity or graph properties, is an open problem.
