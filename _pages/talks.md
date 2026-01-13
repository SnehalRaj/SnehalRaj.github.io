---
layout: page
title: talks
permalink: /talks/
description: Academic presentations, conference talks, and invited lectures.
nav: true
nav_order: 3
---

<div class="talks">
{% for year_group in site.data.talks %}
  <h2 class="year-header">{{ year_group.year }}</h2>
  <div class="talks-grid">
    {% for talk in year_group.talks %}
    <div class="talk-card">
      <div class="talk-header">
        {% if talk.logo %}
        <img src="{{ '/assets/img/talks/' | append: talk.logo | relative_url }}"
             alt="{{ talk.venue }} logo"
             class="conference-logo">
        {% else %}
        <div class="conference-logo-placeholder">
          <i class="fas fa-microphone-alt"></i>
        </div>
        {% endif %}
        <div class="talk-meta">
          <span class="talk-type {{ talk.type }}">{{ talk.type }}</span>
          <h3 class="talk-title">{{ talk.title }}</h3>
          <p class="talk-venue">{{ talk.venue }}</p>
          <p class="talk-date">{{ talk.date | date: "%B %d, %Y" }}</p>
          {% if talk.location %}
          <p class="talk-location">
            <i class="fas fa-map-marker-alt"></i>{{ talk.location }}
          </p>
          {% endif %}
        </div>
      </div>

      {% if talk.description %}
      <p class="talk-description">{{ talk.description }}</p>
      {% endif %}

      {% if talk.slides or talk.video or talk.paper or talk.poster or talk.code %}
      <div class="talk-links">
        {% if talk.slides %}
        <a href="{{ talk.slides }}" class="btn-talk" target="_blank">
          <i class="fas fa-file-powerpoint"></i>Slides
        </a>
        {% endif %}
        {% if talk.video %}
        <a href="{{ talk.video }}" class="btn-talk" target="_blank">
          <i class="fas fa-video"></i>Video
        </a>
        {% endif %}
        {% if talk.paper %}
        <a href="{{ talk.paper }}" class="btn-talk">
          <i class="fas fa-file-alt"></i>Paper
        </a>
        {% endif %}
        {% if talk.poster %}
        <a href="{{ talk.poster }}" class="btn-talk" target="_blank">
          <i class="fas fa-image"></i>Poster
        </a>
        {% endif %}
        {% if talk.code %}
        <a href="{{ talk.code }}" class="btn-talk" target="_blank">
          <i class="fab fa-github"></i>Code
        </a>
        {% endif %}
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
{% endfor %}
</div>
