---
layout: post
title: Adaptive Directional Gradients for Parameterised Quantum Circuits
date: 2026-06-08 10:00:00+05:30
description: A gradient estimator for quantum circuits that averages V random directional derivatives. SPSA, random coordinate descent, and the parameter-shift rule are its limiting cases, and the QUIVER optimiser sets V from the measurement statistics.
tags: quantum-machine-learning optimization
categories: research
related_posts: false
related_publications: coyle2026adaptive
mathjax: true
toc:
  beginning: true
---

Our new preprint, with Brian Coyle, Virag Umathe, El Amine Cherrat, and Elham Kashefi, counts the circuit evaluations a gradient step needs. The parameter-shift rule needs two per parameter. We show that a much smaller number of random directional derivatives does the same job. We also build an optimiser that picks that number during training. The paper is on [arXiv](https://arxiv.org/abs/2606.09734).

## The measurement cost of a gradient

Gradient descent needs a gradient estimate at every step. A classical network gets it from backpropagation at about the cost of one forward pass.

A quantum circuit has no such shortcut. The parameter-shift rule is the standard tool. It evaluates the loss circuit at two shifted parameter values and takes their difference. The derivative it returns is exact. A model with $$N$$ parameters needs $$2N$$ circuit evaluations per step, each with $$M$$ shots, so $$2NM$$ shots per gradient. At $$N = 1770$$ that cost dominates the shot budget.

Two known estimators drop the explicit $$N$$ per step. SPSA shifts every parameter at once along one random sign vector and uses two circuit evaluations per step. Random coordinate descent (RCD) picks one parameter at random and computes its exact derivative. Neither escapes the cost. The variance of SPSA grows linearly in $$N$$, and RCD needs of order $$N$$ times more steps.

## Forward gradients from random directions

Forward-mode automatic differentiation computes a directional derivative, $$\nabla_{v} f = v \cdot \nabla f$$, for one direction $$v$$. Baydin et al. showed that a few of them give a usable gradient estimate for classical networks. Draw $$V$$ random directions whose components are independent with zero mean and unit variance. The quantum forward gradient estimator is

$$
\widetilde{\nabla}^{\mathsf{F}} f(\theta) = \frac{1}{V} \sum_{\ell=1}^{V} \big(\widetilde{\nabla}^{\varepsilon}_{v^\ell} f\big)\, v^\ell,
\qquad
\widetilde{\nabla}^{\varepsilon}_{v} f = \frac{f^M(\theta + \varepsilon v) - f^M(\theta - \varepsilon v)}{2\varepsilon}.
$$

Here $$f^M$$ is the $$M$$-shot estimate of the circuit output. Each directional derivative is a central finite difference, so a step costs $$2V$$ circuit evaluations and $$2VM$$ shots. The circuits are the loss circuits with the parameters shifted along $$v$$. There are no ancilla qubits and no controlled gates.

The estimator is unbiased in the limit of small $$\varepsilon$$. The loss of a quantum circuit is a trigonometric polynomial with bounded frequency, so a large step $$\varepsilon$$ still gives a small bias. Shot noise enters the error as $$1/\varepsilon^2$$ and the bias as $$\varepsilon^2$$. On a VQE example the energy error is lowest at $$\varepsilon = 0.1$$, and we use that value in every experiment.

The number of directions $$V$$ trades variance for circuit evaluations. With Rademacher directions, the second moment of the estimator is $$(N + V - 1)/V$$ times the squared gradient norm. At $$V = 1$$ the factor is $$N$$, and at $$V = N$$ it is close to 2. More directions give a more precise step and cost more circuits. In the convergence bound the two effects cancel. The number of steps scales as $$N/V$$, each step costs $$V$$ circuits, and the total is independent of $$V$$. Under shot noise at a fixed per-step budget, the noise floor is also independent of $$V$$. This is a no-free-lunch result for convex losses. The savings we see come earlier in training, where a larger $$V$$ finds better descent directions on a non-convex landscape.

## Three known optimisers as special cases

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/schematic.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) The training loop. (b) Four estimators as directions probed at M shots each. Parameter shift covers all N basis directions at cost 2NM. SPSA and RCD draw one direction at cost 2M. The forward gradient draws V random directions at cost 2VM. (c) A cartoon: about N/V times fewer shots than parameter shift for the same loss. (d) QUIVER adapts V and M over training.
</div>

Set $$V = 1$$ and draw $$v$$ from the Rademacher distribution, so each component is $$+1$$ or $$-1$$. That gives SPSA. For RCD, set $$V = 1$$ and draw $$v$$ as one basis vector $$e_j$$ scaled by $$N$$, with the derivative from the parameter-shift rule. Enumerate all $$N$$ basis vectors in one step instead of sampling them, and you have the parameter-shift rule. The $$N$$-fold variance of SPSA and the $$N$$-fold slowdown of RCD both follow from the second-moment formula.

The new ingredient is $$V$$. It runs from 1, the cheapest and noisiest estimator, to $$N$$, the exact gradient at full cost. Among isotropic distributions with independent components, Rademacher directions give the smallest estimator variance at fixed $$V$$.

## QUIVER

The iCANS and gCANS optimisers keep the parameter-shift structure and give more shots to noisy gradient components. That works because each shifted circuit perturbs a different gate, so the measurement variance differs across parameters. A random direction perturbs every parameter at once, and concentration of measure makes the variance nearly the same for every direction. We prove this for local Hamiltonians on bounded-depth circuits and check it numerically. Across VQE and QAOA instances with $$N$$ up to about $$10^3$$, the per-direction variances sit within 15% of their mean. Per-direction shot allocation has nothing to work with.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/v_schedule.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A decaying V-schedule (blue) against its two fixed-V endpoints (grey) at a matched per-step budget. (a) QAOA MaxCut, linear, 30 to 2. (b) ECG5000 at n = 50, linear, 50 to 2. (c) MNIST at n = 50, cosine, 150 to 5. (d) VQE, exponential, 20 to 2.
</div>

A fixed schedule for $$V$$ already helps. Decay $$V$$ over training while the per-step budget $$B = 2VM$$ stays fixed, so $$M$$ rises as $$V$$ falls. On all four benchmarks a decaying schedule beat both fixed endpoints at matched shots. We present this as a heuristic, since the best shape and range vary by problem.

QUIVER (Quantum Iterative V-adaptive Estimator Refinement) replaces the schedule with a rule computed from the measurement statistics. The optimiser keeps two exponential moving averages at no extra shot cost. One, $$\widehat{g}^2_t$$, tracks the squared norm of the reconstructed gradient. The other, $$\widehat{\sigma}^2_t$$, tracks the variance across the $$V$$ directional derivatives. Each epoch it sets

$$
V^\star_t = \frac{(N - 1 + \alpha)\, \widehat{g}^2_t}{\tau^2},
\qquad
M^\star_t = \frac{N\, \widehat{\sigma}^2_t}{\alpha\, \widehat{g}^2_t},
$$

with two hyperparameters: a ratio $$\alpha$$ that sets the shots per direction and a target variance $$\tau^2$$ for the gradient estimate. As training shrinks the gradient, $$V$$ falls and $$M$$ rises. Early on the optimiser probes many directions with few shots each. Later it concentrates shots on a few directions. A short warmup and a clamp on each update keep the noisy early averages from swinging $$V$$ and $$M$$. The derivation assumes a loss linear in circuit expectation values, which holds for VQE and QAOA.

The rule solves a cost problem. Among all $$(V, M)$$ pairs that reach a target mean-squared error with at least $$M_{\min}$$ shots per direction, it picks the cheapest. Its shot budget matches the Cramér-Rao lower bound for any unbiased gradient estimator on a shot-noise oracle, up to a factor $$(N - 1 + \alpha)/N$$. Parameter shift saturates the same bound, so the practical gain is a constant factor.

## Results

We train orthogonal quantum neural networks, circuits that preserve Hamming weight, on ECG5000 time-series classification and MNIST image classification. These circuits have $$N = n(n-1)/2$$ parameters on $$n$$ qubits, so $$n = 60$$ gives $$N = 1770$$. We also run VQE on a transverse-field Ising model at $$n = 10$$, with $$N = 160$$. The QAOA benchmark is depth-3 MaxCut on 16-vertex weighted graphs, with $$N = 99$$. Every stochastic method gets $$B = 1000$$ shots per step. The parameter-shift rule gets $$M = 10$$ shots per parameter, so its per-step cost grows with $$N$$. All methods use Adam, and we report means over three seeds.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/four_domains.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The best forward gradient configuration against parameter shift (PS), SPSA, and RCD. (a) QAOA MaxCut, N = 99. (b) VQE at n = 10, N = 160. (c) ECG5000 at n = 60, N = 1770. (d) MNIST at n = 50, N = 1225. Bands: one standard deviation over three seeds. We omit PS from (d) for cost.
</div>

### Fixed V against the baselines

On ECG5000, forward gradients with $$V = 10$$ beat SPSA and RCD at every system size. They match or beat the parameter-shift rule at a fraction of the total shots. The gap to the exact gradient is 1 to 2 percentage points up to $$n = 60$$. The best $$V$$ is 10 at most sizes and 25 at $$n = 60$$. MNIST shows the same ordering.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/ecg_forward_vs_ps.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    ECG5000 test accuracy against total shots, for n from 10 to 60 qubits. Green: forward gradients at a fixed per-step budget of 1000 shots. Purple: parameter shift at 10 or 50 shots per parameter. Blue line: the exact gradient.
</div>

On VQE at $$N = 160$$, forward gradients with $$V = 10$$ reach a best energy error of 0.115 ± 0.010 at 5 × 10⁶ shots. Adam with parameter shift reaches 0.203 ± 0.021 at the same budget, and SPSA reaches 0.215. On QAOA at $$N = 99$$, forward gradients with $$V = 10$$ reach an approximation ratio of 0.988, within about 0.01 of the exact gradient.

### QUIVER against iCANS and gCANS

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/quiver_vs_icans.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    QUIVER against iCANS, gCANS, and parameter shift on VQE at n = 10 and a matched budget of 5 million shots, three seeds. (a) N = 80 at learning rate 0.05. (b) N = 160 at learning rate 0.003.
</div>

The iCANS shot rule carries a prefactor in $$L\eta$$, the Lipschitz constant times the learning rate. At $$N = 80$$ and $$\eta = 0.05$$ that product is about 0.95, so iCANS and gCANS adapt. QUIVER still reaches a lower final energy error. At $$N = 160$$ and $$\eta = 0.003$$ the product is about 0.06. The prefactor then pins iCANS and gCANS at their minimum shot count, and both collapse onto plain parameter shift. QUIVER leads by a margin well outside the seed-to-seed spread. On QAOA MaxCut at a 10⁶-shot budget, QUIVER leads iCANS at every $$N$$ we tested.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/adaptive-directional-gradients/quiver_trajectory.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    One QUIVER run on VQE at n = 8, depth 20, N = 320, three seeds. (a) V and M over epochs. (b) The signal and noise moving averages. (c, d) The energy error against epochs and against total shots.
</div>

On that run, both $$V_t$$ and $$M_t$$ move after the 50-epoch warmup and span an order of magnitude. The signal average decays while the noise average stays flat, and their ratio drives the update. The energy error descends monotonically on both axes.

## What this changes

The parameter-shift rule costs $$2N$$ circuits per gradient step. Forward gradients cost $$2V$$ for any $$V$$ from 1 to $$N$$, and QUIVER picks $$V$$ from statistics the training loop already produces. The circuits need no ancillas or mid-circuit measurements. The $$V$$ directional derivatives are independent jobs and can run in parallel across devices.

The convergence bound says the per-step saving cannot become an asymptotic speedup on convex losses. Yet the empirical saving grows with $$N$$ on non-convex landscapes, and we do not yet know why. The noise-concentration proof covers local Hamiltonians on bounded-depth circuits, so it does not yet cover chemistry Hamiltonians or long-range spin systems.
