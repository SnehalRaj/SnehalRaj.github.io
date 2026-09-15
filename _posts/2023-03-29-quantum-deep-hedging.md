---
layout: post
title: Quantum Deep Hedging
date: 2023-03-29 10:00:00+05:30
description: Quantum neural networks with orthogonal and compound layers act as the policy and the critic in Deep Hedging. A distributional actor-critic gives the best policies, and the models run on a trapped-ion processor with up to 16 qubits.
tags: quantum-machine-learning finance reinforcement-learning
categories: research
related_posts: false
related_publications: cherrat2023quantum
mathjax: true
toc:
  beginning: true
---

El Amine Cherrat, Iordanis Kerenidis, and I wrote this paper at QC Ware with colleagues at JPMorgan Chase. It brings quantum neural networks into Deep Hedging, the reinforcement learning approach to hedging a derivatives book. We build two kinds of quantum layer and prove that they train without barren plateaus. Then we run the trained models on a trapped-ion processor. The paper appeared on [arXiv](https://arxiv.org/abs/2303.16585) in March 2023 and in [Quantum](https://quantum-journal.org/papers/q-2023-11-29-1191/) in November 2023.

## Hedging as a learning problem

Hedging means trading the underlying asset to reduce the risk of a derivative. Classical finance gives the optimal hedge in a frictionless market. Real markets have transaction costs and limited liquidity, so traders must adapt the textbook hedge.

Deep Hedging, introduced by Buehler et al., turns this into a finite-horizon Markov decision process whose horizon $$T$$ is the maturity. The state $$s_t$$ holds the market history. A deterministic policy maps it to a trade, $$a_t = \pi_t(s_t)$$. Trades have no market impact, so the next state does not depend on the trade. The reward is the cashflow minus the transaction cost.

The trading goal is risk-adjusted. We use the exponential utility with risk aversion $$\lambda > 0$$,

$$
\mathcal{E}_\lambda[X] = -\frac{1}{\lambda} \log \mathbb{E}[\exp(-\lambda X)],
$$

applied to the cumulative return. With this goal the value function no longer satisfies the standard Bellman equation. Policy-search Deep Hedging trains one policy network by gradient descent to maximize the sampled utility. Actor-critic Deep Hedging trains a value network as well and uses it to update the policy.

## Quantum models for the policy and the value

Both kinds of layer are circuits of RBS gates. An RBS gate rotates the pair $$\lvert 01 \rangle, \lvert 10 \rangle$$ by an angle $$\theta$$ and leaves $$\lvert 00 \rangle$$ and $$\lvert 11 \rangle$$ alone. A circuit of them never changes the number of ones in a basis state.

### Orthogonal layers

An orthogonal layer on $$n$$ qubits works in the unary basis, the $$n$$ basis states with one bit set. A log-depth loader maps a vector $$\boldsymbol{x} \in \mathbb{R}^n$$ to a unary state with amplitudes $$x_i / \lVert \boldsymbol{x} \rVert$$. The RBS circuit then acts on that state as an $$n \times n$$ orthogonal matrix. Tomography reads out the $$n$$-dimensional output at low cost. We apply a classical nonlinearity and reload for the next layer.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quantum-deep-hedging/orthogonal_layers.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Three circuits for an orthogonal layer. Each vertical line is an RBS gate with its own angle. Pyramid (left) and Brick (middle) use n(n-1)/2 gates on nearest-neighbour qubits. Butterfly (right) has logarithmic depth and (n/2) log n gates but needs all-to-all connectivity.
</div>

The circuit can only produce orthogonal matrices, so the layer needs no re-orthogonalization step. A classical computer can simulate each layer in $$O(n^2)$$ time. We therefore train by simulation and keep the quantum processor for inference. We drop these layers into feed-forward, recurrent, and attention blocks in place of the linear layers.

### Compound layers

The same circuit also acts on every other Hamming-weight subspace. On the subspace of weight $$k$$ it acts as the $$k$$-th compound matrix $$A^{(k)}$$ of the orthogonal matrix $$A$$, whose entries are the $$k \times k$$ minors of $$A$$. The unitary is block diagonal, with one block of size $$\binom{n}{k}$$ per weight.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quantum-deep-hedging/compound_block_diagonal.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A compound layer U(theta) is block diagonal. Block k acts on the basis states of Hamming weight k and equals the k-th compound matrix of one n by n orthogonal matrix.
</div>

A compound layer explores an exponentially large space with $$O(n^2)$$ angles. The data loader decides how much of that space the layer uses. Load into the unary basis and the layer is orthogonal. Load with a Hadamard on each qubit and every weight takes part.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quantum-deep-hedging/compound_nn.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A quantum compound neural network. A data loader prepares the input state, a compound layer acts on it, and a computational-basis measurement on every qubit ends the circuit.
</div>

### Trainability

Highly expressive circuits hit barren plateaus, where the gradient variance shrinks exponentially in the qubit count. We prove that compound layers avoid this. Take Gaussian initialization with variance $$O(1/n^2)$$ and a single-qubit $$Z$$ observable. For a uniform superposition as input, over all basis states or over those of weight $$k$$, the expected squared gradient norm is $$\Omega(1/\mathrm{poly}(n))$$. The proof computes the gradient at $$\boldsymbol{\theta} = 0$$ by hand and applies a result of Zhang et al.

## Training

### Orthogonal policies in a classical market

A quantum policy network reads the price history and outputs the hedge position at each step. We train it with policy-search Deep Hedging. Sample $$N$$ paths and run the policy along each one. Then update the parameters by gradient descent on the negative sampled utility of the total returns.

### A quantum market and a distributional critic

The second method is quantum-native. Each market observation becomes an $$n$$-bit string, so the market state is a basis state $$\lvert s_t \rangle$$. A transition oracle writes the next-step probabilities into amplitudes, and a sequence of oracles prepares a superposition over every future path. The oracles need no action register, since trades have no market impact. A diagonal observable gives path $$s_T$$ the eigenvalue $$\exp(-\lambda R_t^\pi(s_T))$$. The value function then follows from its expectation in that superposition.

That observable defines a categorical distribution over future returns, which links the method to distributional reinforcement learning. The whole distribution has an exponential support and is impractical to learn. We split the future paths by the Hamming weight of the remaining path and learn one expectation per subset. In a random-walk market, that weight counts the up moves still to come. The model gives the probability of each subset, so the overall expectation follows.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quantum-deep-hedging/distributional_subsets.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    A schematic trimodal target (orange). Left: one learned distribution (blue) fitted to its mean misses its shape. Right: three subsets, each with its own learned expectation (green), keep the modes and the tails.
</div>

One Hamming-weight preserving unitary acts on every subset at once, so a single circuit predicts each subset expectation and the overall one. Two ancilla qubits in $$\lvert 01 \rangle$$ give every subset a support of at least two atoms, as the Cramér projection requires. A fixed observable with evenly spaced eigenvalues, independent of the policy, then reproduces the value distribution in expectation.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/quantum-deep-hedging/black_scholes_circuit.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The circuit for the Black-Scholes quantum market. Yellow: t qubits load the past jumps, and Hadamard gates on the next T - t qubits prepare an equal superposition over future jumps. Two ancilla qubits hold 01. Blue: a Brick compound layer on the future and ancilla qubits, with separate angles for each value of each past qubit. Green: measurement of every future and ancilla qubit.
</div>

Training follows an actor-critic loop. The critic minimizes a squared error between its predicted expectation and the observed $$\exp(-\lambda \widetilde{R}^i_t)$$. The expected critic predicts one number per state. The distributional critic predicts it for the Hamming-weight subset the path landed in. The policy then minimizes a one-step utility loss adapted from Murray et al. The loss uses the critic's value for the next state. With $$O(T^2)$$ parameters per network, $$\mathrm{poly}(T)$$ training episodes suffice for generalization.

## Results, including on hardware

We evaluated the models in three ways: exact classical simulation, the Quantinuum H1-1 noisy emulator, and the H1-1 and H1-2 trapped-ion processors. All training ran in exact simulation.

### Classical market, orthogonal layers

The market follows geometric Brownian motion with zero drift and volatility 0.2. The instrument is a short European call struck at the money, hedged daily over 30 trading days with a proportional transaction cost of 0.01. Each layer has 16 features or 16 qubits. The table gives utilities with costs on 256 paths for classical linear layers and Butterfly orthogonal layers.

| Model | Classical utility | Butterfly utility | Classical parameters | Butterfly parameters |
|---|---|---|---|---|
| Feed-forward | -5.064 | -5.043 | 881 | 257 |
| Recurrent | -5.075 | -4.854 | 881 | 257 |
| LSTM | -4.743 | -4.787 | 569 | 217 |
| Transformer | -4.713 | -4.822 | 1905 | 865 |

The Butterfly models stay close to their classical counterparts with 29% to 45% of the parameters, and Pyramid layers score about the same. Without costs, every quantum model lands within 0.03 utility of its classical counterpart. We note in the paper that classical pruning might give a similar parameter reduction.

On the H1-1 emulator we used one layer per model and 1,000 shots per circuit. The Butterfly LSTM lost the least to noise: -4.809 in simulation, -4.866 on the emulator. On the H1-1 processor we ran the LSTM and the Transformer with 16-qubit Butterfly circuits over 5 days on 4 paths. The LSTM went from -2.176 to -2.194 and its per-path PnL tracked simulation closely. The Transformer fell from -2.195 to -2.539.

### Quantum market, compound layers

The quantum market is a discretized geometric Brownian motion with one up-or-down jump per day. Maturity is 10 days and the transaction cost is 0.002. Classical simulation of the full Hamming-weight space capped the circuits at 12 qubits. We trained with policy search and with both actor-critic algorithms for 2,000 Adam steps, 3 seeds, and 16 episodes per step.

In exact simulation the distributional actor-critic gave the best utility, -3.875 without costs and -4.424 with costs. Policy search gave -4.064 and -4.639, and the expected actor-critic gave -4.193 and -4.668. On the H1-1 emulator, the utilities matched simulation to within 0.02 for all three algorithms, and the distributional policy still scored best.

The hardware run used 8 paths on H1-1 and H1-2, with transaction costs, and compared against the Black-Scholes delta hedge.

| Policy | Utility, simulation | Utility, hardware |
|---|---|---|
| Black-Scholes delta hedge | -4.884 | |
| Expected actor-critic | -3.547 | -3.501 |
| Distributional actor-critic | -3.309 | -3.369 |

Both learned policies beat the delta hedge by more than one utility unit, and the distributional policy was best. Hardware agreed with simulation to within 0.06 in utility. The terminal PnLs were similar path by path.

## What this changes

Orthogonal layers slot into standard time-series models and match classical layers with fewer parameters. The LSTM version survives a trapped-ion processor at 16 qubits. Compound layers turn a Hamming-weight preserving circuit into a distributional critic, and that critic gave the best policies in every setting we compared. The circuits are small, since qubit count and depth scale with the maturity.

Classical simulation of training capped the maturity at 10 days for compound models. If we trained on the processor with the parameter-shift rule, the maturity could reach a month or more. The model would then be beyond classical simulation. Some circuits we ran are classically simulable, though a simple change of input state makes them hard. A quantum environment for the Heston model is still open. So is a distributional loss with temporal-difference updates.
