---
layout: default
permalink: /cv/
title: cv
nav: true
nav_order: 4
description: Snehal Raj's CV
---

<div class="post">
  <header class="post-header">
    <h1 class="post-title">{{ page.title }} <a href="{{ '/assets/pdf/resume.pdf' | relative_url }}" target="_blank" rel="noopener noreferrer" class="float-right"><i class="fas fa-file-pdf"></i></a></h1>
    <p class="post-description">{{ page.description }}</p>
  </header>

  <iframe src="{{ '/assets/pdf/resume.pdf' | relative_url }}" width="100%" height="900px" style="border: none;"></iframe>
</div>
