---
layout: post
title: 'Scalable Message-Passing Quantum Graph Neural Networks in the Weisfeiler-Leman Hierarchy'
date: 2026-06-25 10:00:00+05:30
description: A quantum graph neural network that passes messages inside the circuit, is exactly permutation equivariant, and reaches a chosen level of the Weisfeiler-Leman hierarchy. We prove the three properties and test them in simulations of up to 56 qubits.
tags: quantum-machine-learning graph-neural-networks
categories: research
related_posts: false
related_publications: raj2026qgnn
mathjax: true
toc:
  beginning: true
---

Our new preprint, written with Brian Coyle, Léo Monbroussou, André J. Ferreira-Martins, Renato M. S. Farias, and Elham Kashefi, builds a quantum graph neural network that keeps the three properties of its classical counterpart. It passes messages inside the circuit, is exactly permutation equivariant, and reaches a chosen level of the Weisfeiler-Leman hierarchy. The paper is on [arXiv](https://arxiv.org/abs/2606.26873), and the code is on [GitHub](https://github.com/SnehalRaj/mp-qgnns). An [interactive companion]({{ '/projects/qgnn-subspace/' | relative_url }}) shows the subspace the model works in as you change the register sizes.

## Message passing on a quantum state

A classical graph network refines node features over L rounds of message passing. Most quantum graph models skip this loop. They place gates along the graph's edges and leave the aggregation to a classical readout.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/gnn_properties.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) Message passing: each node updates from its neighbours. (b) Permutation equivariance: relabelling the input relabels the output. (c) Weisfeiler-Leman expressivity: the particle number j sets the level the model reaches.
</div>

Our model runs the loop on the quantum state, across two registers. A node register of N qubits at Hamming weight j indexes the graph. Its basis states are the j-subsets of nodes: single nodes at j = 1, edges at j = 2. An embedding register of D qubits at Hamming weight k holds the features. Its size does not grow with the graph.

Four blocks act on these registers.

- **Loader** V(x) writes the graph into the registers. We re-upload it at every layer, which makes the map nonlinear.
- **Adjacency** A(G) applies a Givens rotation between each pair of node qubits. The edge weights set the angles and fix the gate order. It needs no training.
- **Evolution** W(θ) updates the features on the embedding register only. Every node shares the same W. At (D, k) = (6, 3), 15 parameters drive a 20 × 20 rotation.
- **Mixer** M couples the two registers once, before the readout.

The state after $$L$$ layers is

$$
\lvert \psi(\mathbf{x}, G) \rangle = M(\boldsymbol{\theta}_M)\, \big[\, W(\boldsymbol{\theta})\, \mathcal{A}(G)\, V(\mathbf{x}) \,\big]^{L}\, \lvert \psi_0 \rangle .
$$

The readout measures the one-particle density matrix of the embedding register, one D × D matrix per node. A small classical head maps it to node and edge features.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/architecture_standalone.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The circuit. A loader, an adjacency block, and a trainable evolution repeat for L layers. A mixer then couples the registers, and a readout returns node and edge features.
</div>

Exact permutation equivariance follows. The edge weights fix the gate order, so a relabelling of the nodes reorders nothing. The evolution block treats every node the same way. The output is the relabelled output of the original, at every parameter value. Earlier equivariant quantum graph models tie parameters across the symmetric group. We tie none.

## Where the model sits in the Weisfeiler-Leman hierarchy

The Weisfeiler-Leman test measures how finely a model can tell graphs apart. The 1-WL test gives each node a colour. Each round replaces that colour with a hash of it and the multiset of its neighbours' colours. The test declares two graphs different when their final colour histograms differ. A message-passing network can separate two graphs only if 1-WL can. A 1-WL network cannot count cycles, so it can give two distinct molecules the same prediction.

The set-based j-WL test applies the same refinement to j-subsets of nodes. Each subset has a colour. The test refines it over the subsets that differ from it by one node. In this convention j = 2 matches 1-WL, j = 3 matches 2-WL, and j = 4 matches 3-WL.

Our node register at Hamming weight j has one basis state per j-subset. A Givens rotation between node qubits a and b couples exactly the subsets that differ by a swap of a for b. That is the neighbourhood that defines j-WL. So one circuit iteration performs one round of j-WL refinement. We prove that for 2 ≤ j ≤ 4, at generic parameters, the model matches set-based j-WL. After L iterations it separates exactly the graphs that L rounds of j-WL separate. For j ≥ 3 this passes the 1-WL ceiling. To our knowledge it is the first quantum graph model proven to do so.

The graph structure enters through the initial state, which fingerprints each j-subset's induced subgraph with closed-walk counts. That fingerprint fails at j ≥ 5, so the theorem stops at j = 4.

## Staying trainable in a particle-number subspace

Variational circuits suffer from barren plateaus: gradients vanish as the circuit grows. The effect grows with the size of the space the dynamics explore. Every gate in our model preserves Hamming weight, so the dynamics stay inside a structured subspace. The trainable block acts on the embedding register alone.

This lets us pre-train on small graphs and deploy on larger ones. The trainable evolution acts on D qubits, and D does not depend on N. The adjacency block needs no training. Parameters fitted at one graph size initialise the next.

The gradients hold up in simulation. We measured the per-parameter gradient variance at random initialisation for three embeddings, out to N + D = 56 qubits. At fixed (D, k) the variance is flat in N. Initialise from a model trained on 5-city instances, and the gradient stays one to two orders of magnitude above a random start. This holds at every size we test. A log-log fit favours a power law over an exponential in each case.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/trainability_2panel.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    (a) Per-parameter gradient variance against qubit count, out to 56 qubits, at (D, k) = (6, 3), (8, 4), and (10, 5). Dotted lines fall as one over the joint subspace dimension. (b) Four initialisations. Transfer from a 5-city model stays one to two orders of magnitude above a random start.
</div>

We call this evidence heuristic. The supplement gives a polynomial lower bound under a 2-design assumption and all-pair mixer connectivity. We have not yet verified it for our nearest-neighbour mixer. The simulations are also expensive. One forward-and-backward pass takes 1 second at N = 20 and 114 seconds at N = 50 on one CPU core.

Deployment needs a cheap readout. We can estimate the density matrix to accuracy ε in O(D³/ε²) shots, by a Hartree-Fock readout or a matchgate shadow. The D-qubit embedding register sets the cost, up to a factor polynomial in N. A computational-basis readout recovers only the diagonal and stalls at a tour ratio of 1.043 on the travelling salesman task. The matchgate readouts reach 1.006 at the same shot budget.

## Results

We test the model on three datasets, with several random seeds each. The largest run, the travelling salesman problem with 50 cities, uses 56 qubits.

### Distinguishing graphs (CFI)

Cai-Fürer-Immerman graphs are pairs of non-isomorphic graphs that 1-WL cannot tell apart. We use CFI(K3) on 6 vertices, separable at j = 3, and CFI(K4) on 8 vertices, separable at j = 4. We train the model as a binary classifier on 200 random relabellings of each graph, so it must learn a permutation-invariant rule.

On both families the test accuracy jumps from chance to 100% exactly at the predicted particle number, and stays at chance below it. At a matched parameter budget, a 1-WL graph isomorphism network stays at chance on both families, while a 3-WL network (PPGN) separates both.

<div class="row mt-3">
    <div class="col-sm-6 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/cfi.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Test accuracy on two CFI families as j rises. Accuracy reaches 100% exactly at the predicted level. The dashed line is a 1-WL GIN baseline at chance.
</div>

### Molecular property prediction (QM9)

QM9 holds 130,831 small organic molecules with up to nine heavy atoms. We predict the HOMO-LUMO gap, the energy difference between a molecule's highest occupied and lowest unoccupied orbitals. Between runs we change only j.

The error falls as j rises: 0.398 eV at j = 1, 0.308 eV at j = 2, and 0.235 eV at j = 3. The j = 1 value is a validation estimate, since that run kept no test checkpoint; the other two are test errors. The parameter count barely moves, from 2,591 to 2,655. A classical message-passing network reaches 0.121 eV with 849,569 parameters, about 320 times more.

<div class="row mt-3">
    <div class="col-sm-6 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/qm9.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Mean absolute error on the QM9 HOMO-LUMO gap as j rises, at near-constant parameter count.
</div>

### Travelling salesman

The Euclidean travelling salesman problem asks for the shortest closed tour through N cities in the plane. We use the benchmark instances of Skolik et al. and run the model end to end at j = 1. An encoder maps each city's coordinates onto the embedding register. A head scores every edge from the per-node density matrices, and a beam search of width 100 decodes a tour.

Tour quality is the tour length over the optimal length, so 1.0 is optimal. The mean ratio is 1.008, 1.034, 1.078, 1.128, and 1.201 at N = 5, 10, 20, 30, 50. The equivariant quantum circuit of Skolik et al. reaches 1.026, 1.047, and 1.139 at N = 5, 10, 20. Our model is at or below these where the two overlap, though the pipelines optimise different objectives. Beyond N = 20 their N-qubit state vector is too large to simulate.

<div class="row mt-3">
    <div class="col-sm-6 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/qgnn-weisfeiler-leman/tsp.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Tour ratio at j = 1 against the equivariant quantum circuit of Skolik et al., with 1.0 optimal. The 50-city run is a 56-qubit simulation.
</div>

Two further tests use the 5-city instances. Built-in equivariance lowers the validation loss at every training-set size against a matched-parameter variant with a fixed gate order. The gains are 14%, 6%, and 16% at 500, 1,000, and 2,000 instances. At a matched parameter count of about 5,800, a classical graph convolutional network reaches a lower edge-prediction loss, 0.080 against our 0.224. At j = 1 the model sits in the same Weisfeiler-Leman class as that network.

## What this changes

This model carries the three properties of a classical graph network onto the quantum state. We prove all three. The particle number j sets the expressivity. Raise j and the model climbs the Weisfeiler-Leman hierarchy, on synthetic pairs and on a real chemistry task, at almost no cost in parameters.

The evidence for trainability is heuristic. Barren-plateau theorems describe generic, randomly initialised circuits. Our structured, pre-trained model sits outside that class, so the theory does not settle its behaviour. We have also not run the model on hardware. A run at N = 50 needs 56 qubits and about 10⁴ two-qubit gates per forward pass, within the qubit count of current superconducting devices. The trained circuit is matchgate-compatible, so the parameters can move to hardware without retraining.

The [companion page]({{ '/projects/qgnn-subspace/' | relative_url }}) lets you change the register sizes and watch the active subspace move.
