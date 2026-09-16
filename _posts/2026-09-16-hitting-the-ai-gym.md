---
layout: post
title: Hitting the AI gym, three years later
date: 2026-09-16 10:00:00+05:30
description: In 2023 I asked whether leaning on AI would weaken the skills it takes over. Two studies have since measured it. They led me to build skill-issue, a tool that quizzes you on the code your agent just wrote.
tags: ai-assisted-coding learning
categories: essays
related_posts: false
toc:
  beginning: true
---

In August 2023 I wrote a short essay on Medium called [Hitting the AI Gym](https://medium.com/@snehalraj/hitting-the-ai-gym-the-balance-between-machine-learning-and-mental-muscles-495ef72ed9d7). It asked what happens to our own ability to think once language models do much of the thinking for us. Three years on, I write much of my code with an AI agent. Two controlled studies have since measured the effect. They also pushed me to build [skill-issue](https://github.com/SnehalRaj/skill-issue), an open-source tool that quizzes you on the code your agent just wrote.

## The argument from 2023

The essay opened with a line often credited to Sheikh Yamani, a former Saudi oil minister: "The stone age did not end for lack of stone." I asked whether our own age of thinking could end the same way, with the ability still there and nobody using it.

The analogy was walking. For most of history people got around on foot, and exercise came with every trip. Cars and trains took that exercise away, so we built gyms to put it back. Medical researchers now treat long hours of sitting as a [health risk of its own](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2996155/).

Language models could do the same to thinking. An instant answer skips the search and the dead ends, and those steps are where much of the learning happens.

Psychologists call the habit of storing information outside your head *cognitive offloading*. It frees memory for other work, and it has a cost. In one [experiment](https://doi.org/10.1126/science.1207745), people typed trivia statements into a computer. Those told that the computer would save the statements remembered them worse than those told that the statements would be erased.

The 2023 essay stopped at the diagnosis. It called for a gym for the mind and pointed to schools that mix AI tools with project work. It said little about what that gym would look like for people who already work with these tools all day.

## What the studies found

Coding agents have changed a lot since 2023. They now read a whole codebase, write features across many files, and run the tests until they pass. Two studies from the past fourteen months measured what this does to the people who use them.

In July 2025, METR published a [randomised controlled trial](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) with 16 experienced open-source developers. They worked on 246 real issues from projects they knew well. When AI tools were allowed, the developers took 19% longer. Before the study they had predicted a 24% speed-up. Afterwards, they still believed the tools had made them 20% faster.

In January 2026, Judy Hanwen Shen and Alex Tamkin at Anthropic [reported a second trial](https://arxiv.org/abs/2601.20245). Fifty-two engineers, most of them junior, learned Trio, a Python library for asynchronous programming. One group could use an AI assistant and the other wrote code by hand. The AI group finished about two minutes faster, a gap too small to be statistically significant. On a quiz afterwards, the AI group averaged 50% and the hand-coding group averaged 67%.

The paper sorts the ways people used the assistant into six patterns, and three of them kept quiz scores high. In one, people asked follow-up questions about the code the assistant wrote. In another, they asked only conceptual questions and fixed their errors on their own.

That result led me to skill-issue. A gym needs a separate trip, and busy people skip separate trips. I wanted the practice inside the work, at the moment the agent does something worth understanding.

## skill-issue

The tool has two parts. A skill file tells the coding agent when to pause and ask you a question. A small command-line program keeps your scores on your own machine. It works with Claude Code and Cursor, and with any agent that reads a system prompt.

Every question is about the code you just approved. When the agent writes a non-trivial algorithm or fixes a subtle bug, it follows up with a short check. A check should take between 30 and 90 seconds. The design notes give this example, asked after the agent used the parameter-shift rule:

```
🧠 SKILL CHECK #48 — quantum-circuits — Difficulty: Expert

I just used the parameter shift rule to compute the gradient of an expectation value.

→ In 2–3 sentences: Why is the shift exactly π/2? What property of the gate
  generator makes this work?

answer   hint   skip
```

There are six types of question. You might predict what a function returns, or find the bug in a broken copy of the code you just accepted. The agent stays quiet during boilerplate and urgent debugging, and it leaves at least eight minutes between questions. Say "focus mode", or skip three in a row, and the questions stop.

### Keeping score

Each subject has a knowledge graph. The quantum machine learning graph has 14 concepts, among them barren plateaus and the parameter-shift rule. Every concept carries a weight between 0 and 1 for how often it comes up in real work. Next to that weight sits your mastery score, which changes after each answer.

The agent picks the concept with the highest priority, which is weight × (1 − mastery). A basic idea you have not yet shown you understand comes first. A wrong answer keeps a concept near the top, so it comes back sooner. Mastery fades too. After three days without practice, a score drops by 0.02 each day.

<div class="row mt-3">
    <div class="col-sm-8 mx-auto mt-3 mt-md-0">
        {% include figure.html path="assets/img/blog/hitting-the-ai-gym/knowledge-graph.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The machine learning knowledge graph in the terminal. Each bar shows mastery of one concept. The list at the bottom ranks concepts by priority, the weight of a concept times the gap in mastery.
</div>

You do not have to start from zero. If you already have Claude Code sessions on disk, `skill-issue analyze` reads them and sets your starting scores. It counts the questions you asked as signs of weakness and the code you wrote as signs of strength.

There is also a small game layer of points and streaks. A correct answer earns 12 points, multiplied by the difficulty and by a bonus for your current streak. The game is there to make a daily habit easier to keep. Your scores live in `~/.skill-issue/` as plain JSON and YAML files, so you can read them or keep them in version control.

To try it, install the package and run the setup:

```bash
pip install skill-issue-cc
skill-issue init
```

Then say "challenge me" to your agent.

## Limits

A good score on a one-minute check is weak evidence that you could build the same thing alone. The agent that wrote the code also writes the question and grades your answer. The knowledge graphs are hand-made, and the nine current domains cover only part of what people build. If your field is missing, the graphs are JSON files in `references/knowledge_graphs/`, and pull requests are welcome.

In 2023 I looked to schools and researchers for an answer. For people who work with agents all day, I now think the first step is smaller. Ask yourself a few questions about the code you just accepted, and answer them before you move on.
