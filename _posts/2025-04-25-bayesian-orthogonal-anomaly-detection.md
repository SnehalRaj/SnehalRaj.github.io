---
layout: post
title: Bayesian Quantum Orthogonal Neural Networks for Anomaly Detection
date: 2025-04-25 10:00:00+05:30
description: We put Gaussian distributions on the angles of orthogonal quantum layers, build a 3D convolutional autoencoder from them, and use it to find defects in 3D-printed parts. Part of the pipeline runs on IBM Brisbane.
tags: quantum-machine-learning anomaly-detection
categories: research
related_posts: false
related_publications: mathur2025bayesian
mathjax: true
toc:
  beginning: true
---

We wrote this paper with Natansh Mathur, Brian Coyle, and Nishant Jain at QC Ware. Our coauthors at Airbus are Akshat Tandon, Jasper Simon Krauser, and Rainer Stoessel. The paper asks how a quantum-inspired network can report its own confidence. We presented it at IEEE Quantum Week 2025, and it is on [arXiv](https://arxiv.org/abs/2504.18103).

## The problem

Additive manufacturing builds a part layer by layer, and aerospace firms have adopted it fast. The printed parts still hide internal defects, such as pores and lack of fusion.

The standard check is a computed tomography (CT) scan, which a human expert reads. That reading is slow and error-prone. CT machines also fit only parts up to a set size.

Supervised models can read the scans, but they need labelled data, and defects are rare. Autoencoders need no labels. An encoder compresses the 3D object to a small latent space, and a decoder rebuilds it. If the rebuild is close, the part is normal. A poor rebuild flags an anomaly, since the model never learned to reproduce outliers.

In a safety check, the inspector needs to know how sure the model is, and an accuracy score does not tell them. Bayesian learning gives the model a way to say so.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/overview.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    An autoencoder with orthogonal 3D convolutional layers rebuilds the object. Each layer flattens a 3D patch, loads it into a quantum state, and applies the orthogonal matrix that the circuit implements. In the Bayesian version, each circuit angle has a Gaussian with a trainable mean and variance.
</div>

## Orthogonal quantum neural networks

A fully connected layer computes $$y = \sigma(Wx + b)$$. An orthogonal layer adds the constraint $$W^\top W = I$$. Orthogonal weights keep gradients from exploding or vanishing, and they come with guarantees on generalization error. Each gradient step breaks orthogonality, so training has to restore it after every update. Exact methods cost $$O(d^3)$$ for a $$d \times d$$ matrix. Approximate methods, such as singular value bounding, lose the guarantees.

Landman et al. removed the need to re-orthogonalize. Write the orthogonal matrix as a quantum circuit of reconfigurable beam splitter (RBS) gates,

$$
\mathsf{RBS}(\theta) = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta & 0 \\ 0 & \sin\theta & \cos\theta & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}.
$$

Each RBS gate is a Givens rotation on two qubits, and it preserves Hamming weight. Load a normalized data vector into the Hamming-weight-1 subspace, $$\lvert x \rangle = \sum_j x_j \lvert e_j \rangle$$. The circuit keeps the state in that subspace, so the output is $$y = Ox$$ for an orthogonal matrix $$O$$ fixed by the angles. The matrix is orthogonal by construction at every step of training. A $$d \times d$$ layer needs $$O(d^2)$$ gates in linear depth.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/ortho_layer_8x8.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    An 8 by 8 orthogonal layer in the pyramid layout. Each vertical bar is an RBS gate with its own angle. Figure from Landman et al.
</div>

The unary subspace makes these circuits easy to simulate classically, so the same model runs in two modes. A classical computer simulates it at large scale today, or the circuit runs on quantum hardware. Data encoded at Hamming weight $$k > 1$$ lives in a subspace of dimension $$\binom{n}{k}$$, which is where classical simulation gets hard. These circuits can also be free from barren plateaus, which matters once training runs on hardware at sizes a classical computer cannot simulate.

### 3D orthogonal convolutions

CT data lives in three dimensions, so we built a 3D convolution out of orthogonal layers. The idea, from Kerenidis, Landman, and Prakash, turns convolution into matrix multiplication. Flatten each of the $$k$$ filters of size $$d \times d \times d$$ into a row of a matrix $$F \in \mathbb{R}^{k \times d^3}$$. The convolution is then the product of $$F$$ with each flattened 3D patch of the input. We implement $$F$$ with an RBS circuit, so the filters are mutually orthogonal and learn less redundant features. The layer needs $$\max(k, d^3)$$ qubits, a count that does not grow with the size of the object. We call the layer OrthoConv3D.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/conv_as_matmul.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Convolution as matrix multiplication, drawn for the 2D case. The image patches form the rows of A and the flattened filters form F. We model F as an orthogonal matrix. Figure from Kerenidis, Landman, and Prakash.
</div>

## Making them Bayesian

Standard training finds one point estimate of the parameters. Bayesian learning treats the parameters as random variables with a posterior $$\pi(\theta \mid \mathcal{D})$$ given the data $$\mathcal{D}$$. A prediction averages the model's output over that posterior, and the spread of the outputs is the model's uncertainty.

The direct way to make an orthogonal network Bayesian is to put a distribution on the weight matrix and orthogonalize each sample. That brings back the cubic cost or the approximation. We put the distribution on the circuit angles instead. Each angle gets an independent Gaussian, $$\theta_i \sim \mathcal{N}(\mu_i, \Sigma_i^2)$$, with a standard normal prior. Every sample of the angles gives an exactly orthogonal matrix at quadratic cost.

We learn the means and variances by variational inference. To bring the variational distribution $$q_\gamma$$ close to the true posterior in KL divergence, we maximize the evidence lower bound,

$$
\mathcal{L}(\gamma) = \mathbb{E}_{q_\gamma}\left[\log p(\mathcal{D} \mid \theta)\right] - \frac{1}{2}\sum_{i=1}^{N}\left[\Sigma_i^2 + \mu_i^2 - \log \Sigma_i^2 - 1\right].
$$

We estimate the first term by Monte Carlo from sampled angles. At inference we sample the angles several times, run the network each time, and read off a distribution over outputs.

We score calibration with the expected calibration error (ECE). Bin the predictions by confidence, then sum the gap between mean confidence and accuracy over the bins, weighted by bin size. A model with low ECE is right about as often as it says it is.

## Results

### The data

The dataset holds about 5,000 CT scans of 3D-printed parts with defects introduced on purpose. Each scan is a $$96 \times 96 \times 96$$ greyscale tensor with a mask that marks the anomalous voxels. We cut each scan into $$16 \times 16 \times 16$$ blocks. A block is anomalous if any voxel in its mask is set. This turns masking into classification and multiplies the data 216-fold, so we train on a subset.

### Four architectures, four training methods

We tried two families of encoder and decoder. The feedforward network (FNN) has linear layers of width 128 and 64 in the encoder and 128 in the decoder. The quantum FNN (QFNN) swaps the two inner layers for orthogonal ones in the butterfly layout. The 3D-CNN uses 3D convolutions, and the 3D-QCNN uses OrthoConv3D layers. For each model we compared point-estimate gradient descent (PE), Bayesian learning, Monte Carlo dropout (MCD), and an ensemble.

| Model | ECE | Precision | Recall | F1 |
|---|---|---|---|---|
| FNN (PE) | 0.257 | 74.09 | 71.47 | 72.29 |
| FNN (Bayesian) | 0.221 | 71.68 | 71.03 | 71.35 |
| QFNN (PE) | 0.251 | 73.95 | 71.78 | 72.84 |
| QFNN (Bayesian) | 0.217 | 72.89 | 71.65 | 72.26 |
| 3D-CNN (PE) | 0.239 | 76.35 | 74.97 | 75.65 |
| 3D-CNN (Bayesian) | 0.209 | 73.98 | 72.86 | 73.41 |
| 3D-QCNN (PE) | 0.242 | 75.49 | 74.12 | 74.79 |
| 3D-QCNN (Bayesian) | 0.224 | 73.13 | 72.37 | 72.74 |

Bayesian learning had the lowest ECE of the four training methods in every architecture, with MCD second and the ensemble third. The point-estimate models kept a small lead on precision, recall, and F1. So Bayesian training costs a little accuracy and improves calibration.

Orthogonality helped the feedforward models. The QFNN beat the FNN on ECE and F1 under both training methods, with about 1.4M parameters against 1.5M. The classical 3D-CNN beat both feedforward models on every metric, which may be specific to the architectures we chose. In the 3D models, orthogonality did not help. The 3D-QCNN trailed the 3D-CNN by a little on every metric, though it has far fewer parameters.

### On IBM Brisbane

To test the quantum mode, we ran the orthogonal layers on 8 qubits of IBM's 127-qubit Brisbane device. The first experiment feeds eight 8-dimensional vectors through one orthogonal layer with fixed angles. It measures the fidelity of the output against the ideal state. Post-selection on unary bitstrings adds error mitigation on top of IBM's readout mitigation. We compared random input vectors with rows of a real data slice, at 1,000 and 10,000 shots.

On random inputs, more shots did not help. On real data they did, and the 10,000-shot runs reached the highest average hardware fidelity, about 0.98. Our guess is that real data has structure that more shots can resolve, and that the same structure hides noise on gates that barely matter. We cannot promise this holds at larger sizes.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/hw_fidelity_voxel.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Output fidelity of one orthogonal layer for eight input vectors from the anomalous voxel slice. The lines show a shot-noise simulator, a simulated noisy Brisbane, and the real device, at 1k and 10k shots.
</div>

The second experiment puts hardware inside the full pipeline. We took an anomalous voxel, downscaled it to 16 by 16 by 16, and picked slice 14, which holds the anomaly. With a 2 by 2 by 2 kernel at stride 1, that slice needs 256 circuits on 8 qubits, each at 5,000 shots.

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/voxel_slices.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The anomalous voxel used in the hardware runs, as 16 slices of 16 by 16 pixels. Slice 14 holds the anomaly.
</div>

We ran a growing fraction of those circuits on Brisbane and simulated the rest exactly. At the layer output, the mean squared error grew linearly with the hardware fraction and reached about 0.88 with every circuit on hardware. One level up, at the OrthoConv3D block, the worst case was about 3.5 × 10⁻³. For the whole autoencoder, it was about 10⁻⁸. The further an output is from the quantum circuits, the smaller their share of the computation, and the less their noise shows.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/bayesian-orthogonal-anomaly-detection/hw_mse_full_pipeline.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    Mean squared error of the full autoencoder output against its noiseless value, as more of the 256 circuits run on Brisbane. The vertical scale is 10 to the minus 8.
</div>

## What this changes

For a manufacturer, the result is a defect detector that reports its own confidence. Its layers stay exactly orthogonal with no cubic orthogonalization step, because the distribution is on the circuit angles.

The hardware runs show what the quantum version looks like on a current device. One 8-qubit layer loses a few percent of fidelity, and almost none of that reaches the output of the pipeline. As devices grow, the same layers can take inputs at higher Hamming weight, where classical simulation gets hard.

We used a mean-field Gaussian for the variational family and left richer families for later. We also compared Bayesian learning only against dropout and ensembles. Other Bayesian methods for quantum circuits, such as Langevin sampling, remain untested on orthogonal layers.
