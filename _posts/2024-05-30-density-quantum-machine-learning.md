---
layout: post
title: Training-Efficient Density Quantum Machine Learning
date: 2024-05-30 10:00:00+05:30
description: A density quantum neural network is a mixture of trainable circuits. Cut a circuit into commuting pieces and the mixture trains at backpropagation cost. Stack copies and it grows without a deeper circuit.
tags: quantum-machine-learning trainability
categories: research
related_posts: false
related_publications: coyle2025training
mathjax: true
toc:
  beginning: true
---

Our paper on density quantum neural networks asks how to make a quantum model bigger without making its gradients more expensive. My coauthors are Brian Coyle, Natansh Mathur, El Amine Cherrat, Nishant Jain, Sofiene Kazdaghli, and Iordanis Kerenidis at QC Ware. The paper appeared on [arXiv](https://arxiv.org/abs/2405.20237) in May 2024 and in [npj Quantum Information](https://www.nature.com/articles/s41534-025-01099-6) in 2025. There is a recorded talk from [QTML 2024](https://www.youtube.com/watch?v=1Dp_U6U6hGQ).

## Why training a quantum model is expensive

A quantum neural network is usually one parametrized circuit. To train it you need the gradient of a loss with respect to every parameter. The standard tool is the parameter-shift rule. It needs separate circuits for every parameter, so a circuit with $$N$$ parameters costs $$O(N)$$ circuits per gradient step.

Abbas et al. estimated the limit. With one day of compute and plausible clock speeds, the parameter-shift rule reaches about 9,000 parameters on a 100-qubit circuit. Classical deep learning runs billions of parameters because backpropagation costs about as much as one forward pass, up to a log factor. Most quantum circuits have no such scaling.

There are exceptions. Bowles et al. showed that commuting-block circuits admit a backpropagation scaling. When the generators in a block commute, and each one commutes or anticommutes with the measured observable, the gradient observables commute too. One circuit, with a diagonalizing unitary appended, reads all of them at once. The price is expressivity. A single block of commuting gates is a restricted circuit, and some such circuits are easy to simulate classically.

A useful circuit must be hard to simulate classically and still cheap to train. Density models are one way to get a bigger model without giving up cheap gradients.

## Density models

A density quantum neural network prepares a mixture of trainable unitaries. Take $$K$$ circuits $$U_1(\theta_1), \dots, U_K(\theta_K)$$ and a probability vector $$\alpha$$. Load the data into a state $$\rho(x)$$. The model is

$$
\rho(\theta, \alpha, x) := \sum_{k=1}^K \alpha_k \, U_k(\theta_k) \, \rho(x) \, U_k^\dagger(\theta_k), \qquad \sum_{k=1}^K \alpha_k = 1 .
$$

The output is the expectation of an observable, $$f = \mathrm{Tr}(\mathcal{O}\rho)$$. The circuit parameters $$\theta_k$$ and the weights $$\alpha_k$$ are both trainable, and the weights may also depend on the input, $$\alpha_k(x)$$.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/density-quantum-machine-learning/fig1_density_schematic.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Three ways to combine K sub-unitaries. (a) A linear combination of unitaries prepares a pure state and needs an ancilla register plus post-selection. (b) A deterministic circuit prepares the density state exactly, with controlled sub-unitaries. (c) The randomised version runs one sub-unitary per shot, chosen with probability α<sub>k</sub>. It needs no ancillas and no controlled gates.
</div>

There are two ways to prepare this state on hardware. A deterministic circuit prepares it exactly, with an ancilla register and a controlled version of each sub-unitary. The controlled gates are expensive. The second way samples from $$\alpha$$. On each shot, draw an index $$k$$ with probability $$\alpha_k$$ and run only $$U_k$$. The average over many shots is the mixture. Its cost per forward pass is the cost of the most expensive sub-unitary.

A linear combination of unitaries (LCU) model prepares the pure state $$\sum_k \alpha_k U_k \lvert x \rangle$$ instead. That needs post-selection on an ancilla register, so a forward pass succeeds only with some probability.

## What the mixture buys you

### Gradients split across sub-unitaries

The model is linear in the sub-unitaries, so its gradient is a weighted sum of their gradients. If the sub-unitaries share no parameters, an unbiased gradient estimate costs $$\sum_k T_k$$ circuits, where $$T_k$$ is what sub-unitary $$k$$ costs on its own. Take commuting-block sub-unitaries with $$B_k$$ blocks each. Then the full gradient costs $$O(2\sum_k B_k - K)$$ circuits on $$n+1$$ qubits. With $$K = O(\log N)$$, the density model keeps the backpropagation scaling of its parts.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/density-quantum-machine-learning/fig3_hwe_two_paths.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A hardware-efficient circuit with D layers on n qubits, and two density versions. Left: each layer becomes one sub-unitary, and the gradient needs 2D circuits where the pure circuit needs 2nD. Right: K copies of the full circuit become the sub-unitaries, with K times more parameters and 2nDK gradient circuits.
</div>

The first route cuts the circuit into its layers and makes each layer a sub-unitary. Each piece is a commuting-generator circuit, so a constant number of circuits gives all of its gradients. For a hardware-efficient ansatz with $$D$$ layers on $$n$$ qubits, the parameter-shift rule needs $$2nD$$ circuits. The density version needs $$2D$$. A pyramid orthogonal circuit goes from $$O(n^2)$$ gradient circuits to $$O(1)$$, and a round-robin circuit from $$O(n^2)$$ to $$O(n)$$.

The second route keeps the circuit whole and takes $$K$$ copies with independent parameters. Gradients cost $$K$$ times more, but the copies run in parallel, and the model has $$K$$ times more parameters.

### The Mixing lemma

Why should a random mixture do as well as a linear combination? The Hastings-Campbell Mixing lemma comes from randomised compiling. If a linear combination of unitaries approximates a target well, the random mixture of the same unitaries approximates it almost as well. We prove a supervised-learning version. Suppose each of $$K$$ trained sub-unitaries predicts a target function with error at most $$\delta_1$$. Suppose some LCU of them predicts it with error at most $$\delta_2$$. Then the density model with the same weights has error at most

$$
\frac{\delta_1^2}{4 \lVert \mathcal{O} \rVert_\infty} + 2\delta_2 .
$$

If the LCU cuts the error quadratically, $$\delta_2 = \delta_1^2$$, the density model is also an $$O(\delta_1^2)$$ predictor at the cost of one sub-unitary. The lemma assumes the target is itself a quantum model with a known observable. In the experiments we skip the LCU step and train the density model directly.

### Dropout and mixtures of experts

Dropping $$K-1$$ sub-unitaries on each shot looks like dropout. We argue the analogy is incomplete. Classical dropout combines an exponential number of sub-networks at inference, while a density model with a backpropagation scaling has at most $$O(\log N)$$ sub-unitaries. The closer classical relative is the mixture of experts. A gating network sets the weights $$\alpha_k(x)$$ for each input, so the sub-unitaries act as experts.

## Results

We tested three model families in simulation.

### Equivariant circuits on bars and dots

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/density-quantum-machine-learning/fig5_equivariant_results.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Test accuracy on the noisy bars-and-dots task at 10 qubits, by (a) epochs and (b) measurement shots. Dashed lines are the base models from Bowles et al. Solid lines are density versions with two sub-unitaries, started from the pretrained base model at epoch 1000. Mean and standard deviation over 5 runs.
</div>

We ran the translation-invariant bars-and-dots task from Bowles et al. at 10 qubits with noise $$\sigma = 1.8$$. The base model is their commuting-generator XX circuit. The density version adds a second sub-unitary with the same structure and Pauli-Y generators, so both parts keep cheap gradients. We set the weights to $$\alpha = (0.99, 0.01)$$ at the start, biased toward the pretrained XX model, and trained for 1,000 more epochs. Test accuracy rose by 5.8%. Density versions of a non-commuting equivariant circuit and a QCNN, each built from two independently trained copies, gained 2.6% and 3.4%.

### Orthogonal circuits on MNIST

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/density-quantum-machine-learning/fig7_round_robin_results.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Round-robin orthogonal circuits on MNIST at 10 qubits. Top: the full circuit (red) against a density model built from its 9 layers (blue), by epochs (a) and by shots (b). Thin lines are sub-unitaries pretrained alone for 25 epochs. Bottom: sub-unitary depth D = 1, 2, 3, 4, and n minus 1, by epochs (c) and by shots on a log scale (d).
</div>

Hamming-weight-preserving circuits built from RBS gates act on a unary-encoded vector as an orthogonal matrix. They are interpretable and stable to train, but the parameter-shift rule needs $$O(n^2)$$ circuits for a round-robin layout. We cut the round-robin circuit into its $$n-1$$ layers. Each layer holds $$n/2$$ commuting gates, so each sub-unitary's gradient costs one circuit. At $$n = 10$$, a gradient step costs 9 circuits. The full circuit needs 180. We reduced MNIST to 10 features by PCA. The shallow density model reached almost the same test accuracy as the full circuit with a small fraction of the shots.

A single orthogonal circuit, however deep, outputs one orthogonal matrix. A density model outputs a convex combination of orthogonal matrices, which is a larger class. Deeper sub-unitaries raised test accuracy at every step, from about 0.57 at $$D = 1$$ to about 0.86 at $$D = n-1$$. Gradient cost rose from $$O(n)$$ to $$O(n^3)$$ circuits. In all of these runs a linear gating network predicted the weights from the input.

### Data reuploading and overfitting

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/density-quantum-machine-learning/fig8_reuploading_overfitting.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) A single-qubit data reuploading circuit with L reuploads, and a density version with 5 sub-unitaries of D reuploads each. The curves show the partial Fourier series each sub-unitary learned. (b) Test mean squared error and the train/test gap on a Chebyshev polynomial regression task, against L, at matched parameter counts.
</div>

A single-qubit data reuploading circuit computes a partial Fourier series in its input. More reuploads mean more frequencies. We compared a circuit with $$L$$ reuploads and $$3L$$ parameters to a density model with five sub-unitaries of depth $$D$$, with $$5 \times 3D \approx 3L$$. The task is to regress a Chebyshev polynomial from noisy training data. Past about 40 reuploads the single circuit overfits. Its test error and its train/test gap both climb. The density model's test error stays low at every $$L$$ where the single circuit overfits. Each sub-unitary is a shorter Fourier series, so the mixture overfits less than one deep circuit does.

## What this changes

A density model gives a practitioner one more design choice. Cut a circuit into commuting pieces and it trains at backpropagation cost. Or stack copies. The model grows $$K$$-fold and its gradients run in parallel. The Mixing lemma says the randomised version keeps the accuracy of the far more expensive linear combination. On the tasks we tried, the density model matched or beat its pure-state parent. It cost less to train, or it overfit less at equal size.

Barren plateaus are a property of the sub-unitaries, and mixing does not remove them. If the sub-unitaries have different gradient behaviour, the easiest one to train can dominate. The mixture-of-experts literature calls this expert collapse. Whether a density version of a circuit stays hard to simulate classically is an open question. The next step is to find more circuit families with cheap gradients and lift them into density versions. We did that here for equivariant and orthogonal circuits.
