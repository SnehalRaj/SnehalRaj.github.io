---
render_with_liquid: false
---

# Website Redesign: Modern Academic Portfolio

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign SnehalRaj.github.io with a modern, professional academic portfolio feel, while staying within the existing Jekyll/al-folio framework.

**Architecture:** The site stays on Jekyll + al-folio. We enhance the homepage to be a single-page academic portfolio with smooth in-page navigation, add missing sections (Work Experience/Education), improve typography/spacing, add interactive elements (show more/less), and polish the overall aesthetic. All changes are CSS/HTML/Liquid — no framework migration.

**Tech Stack:** Jekyll, SCSS, Liquid templates, Bootstrap 4.6, Font Awesome 6.4

---

## Key Differences to Address

| Feature | Target Design | Current Site | Action |
|---------|--------------|--------------|--------|
| Layout | Sidebar TOC + wide content | Top navbar + narrow (850px) content | Add in-page TOC sidebar on homepage |
| Profile | Name + photo + social links grouped prominently | Name top, photo right-floated, social at bottom | Redesign profile section |
| Work Experience | Prominent section on homepage | Not on homepage (only in CV page) | Add to homepage |
| News | Clean list with "Show More" toggle | Scrollable box, limited to 5 | Add show more/less toggle |
| Publications | Categorized (Conference, Journal, etc.) | Grouped by year only | Add category grouping |
| Social Links | Icons right below name/photo | At very bottom of page | Move to profile section |
| Typography | Clean, spacious, modern | Good but could be more polished | Improve spacing & hierarchy |
| Page Width | ~960px with sidebar | 850px | Widen to 1000px+ |

---

### Task 1: Widen Content Area & Improve Base Typography

**Files:**
- Modify: `_config.yml:56` (max_width setting)
- Modify: `_sass/_variables.scss` (add font variables)
- Modify: `_sass/_base.scss` (improve base typography)
- Modify: `_sass/_layout.scss` (container width)

**Step 1: Update max_width in config**

In `_config.yml`, change:
```yaml
max_width: 850px
```
to:
```yaml
max_width: 1100px
```

**Step 2: Add font stack variables to `_variables.scss`**

Add at the top (after the file header comment):
```scss
// Typography
$font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !default;
$font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !default;
$font-family-mono: 'JetBrains Mono', 'Fira Code', monospace !default;
```

**Step 3: Add Inter font to head.html**

In `_includes/head.html`, add the Inter font import from Google Fonts (before existing stylesheets):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

**Step 4: Update base typography in `_base.scss`**

At the top of the file, add:
```scss
body {
  font-family: $font-family-base;
  font-size: 1rem;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5, h6 {
  font-family: $font-family-heading;
  font-weight: 600;
  line-height: 1.3;
}

h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
h3 { font-size: 1.25rem; }
```

**Step 5: Verify locally**

Run: `bundle exec jekyll serve`
Expected: Site loads with wider content area and Inter font.

**Step 6: Commit**

```bash
git add _config.yml _sass/_variables.scss _sass/_base.scss _sass/_layout.scss _includes/head.html
git commit -m "feat: widen content area and improve base typography"
```

---

### Task 2: Redesign Profile Section (Name + Photo + Social Links)

**Files:**
- Modify: `_layouts/about.html`
- Modify: `_sass/_base.scss` (profile styles)
- Modify: `_pages/about.md` (frontmatter)

**Step 1: Redesign the profile section in about.html**

Replace the current profile + header section with a new hero-style layout that puts the name, subtitle, bio intro, and social links in a prominent top section alongside the profile photo. The new layout should:

- Use a two-column flex layout (content left, photo right)
- Show name as large heading, subtitle/affiliations below
- Place social icons directly under the name/subtitle (not at the bottom)
- Profile photo: 180px circular, with subtle shadow
- On mobile: stack vertically (photo on top)

Replace the current header + profile div structure with:
```html
<div class="profile-hero">
  <div class="profile-content">
    <h1 class="profile-name">
      {% if site.title == "blank" -%}
        <span class="font-weight-bold">{{ site.first_name }}</span> {{ site.middle_name }} {{ site.last_name }}
      {%- else -%}{{ site.title }}{%- endif %}
    </h1>
    <p class="profile-subtitle">{{ page.subtitle }}</p>
    <div class="profile-social">
      {% include social.html %}
    </div>
  </div>
  {% if page.profile.image %}
  <div class="profile-photo">
    {%- assign profile_image_path = page.profile.image | prepend: 'assets/img/' -%}
    {% include figure.html path=profile_image_path class="img-fluid rounded-circle" alt=page.profile.image cache_bust=true -%}
  </div>
  {% endif %}
</div>
```

**Step 2: Add profile hero styles to `_base.scss`**

```scss
// Profile Hero Section
.profile-hero {
  display: flex;
  align-items: center;
  gap: 3rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--global-divider-color);

  .profile-content {
    flex: 1;

    .profile-name {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.25rem;
      line-height: 1.2;
    }

    .profile-subtitle {
      font-size: 1rem;
      color: var(--global-text-color-light);
      margin-bottom: 1rem;

      a {
        color: var(--global-theme-color);
        text-decoration: none;
        &:hover { text-decoration: underline; }
      }
    }

    .profile-social {
      .contact-icons {
        font-size: 1.4rem;
        text-align: left;

        a {
          margin-right: 0.75rem;
          i::before {
            color: var(--global-text-color-light);
            transition: color 0.2s ease;
          }
          &:hover i::before {
            color: var(--global-theme-color);
          }
        }
      }
    }
  }

  .profile-photo {
    flex-shrink: 0;

    img {
      width: 180px;
      height: 180px;
      object-fit: cover;
      border-radius: 50%;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
  }
}

@media (max-width: 768px) {
  .profile-hero {
    flex-direction: column-reverse;
    text-align: center;
    gap: 1.5rem;

    .profile-content .profile-social .contact-icons {
      text-align: center;
    }

    .profile-photo img {
      width: 150px;
      height: 150px;
    }
  }
}
```

**Step 3: Remove the old social section at the bottom of about.html**

Remove the `{% if page.social %}` block at the bottom since social links are now in the profile hero.

**Step 4: Update about.md frontmatter**

Set `social: false` (since social is now integrated into the profile hero, not a separate bottom section).

**Step 5: Verify locally**

Run: `bundle exec jekyll serve`
Expected: Profile section shows name, affiliations, social icons, and photo in a clean two-column layout.

**Step 6: Commit**

```bash
git add _layouts/about.html _sass/_base.scss _pages/about.md
git commit -m "feat: redesign profile section with hero layout and integrated social links"
```

---

### Task 3: Add Work Experience & Education Section to Homepage

**Files:**
- Modify: `_layouts/about.html` (add experience section)
- Create: `_data/experience.yml` (experience data)
- Modify: `_sass/_base.scss` (experience styles)
- Modify: `_pages/about.md` (enable experience)

**Step 1: Create experience data file**

Create `_data/experience.yml`:
```yaml
work:
  - title: "CIFRE PhD Student"
    institution: "LIP6/CNRS - Sorbonne University & QC Ware"
    location: "Paris, France"
    date: "2022 - Present"
    description: "Theoretical and empirical study of quantum & quantum-inspired algorithms. Bridging quantum and classical machine learning."
    advisors:
      - name: "Prof. Elham Kashefi"
        url: "https://www.lip6.fr/actualite/personnes-fiche.php?ident=P1427"
      - name: "Dr. Brian Coyle"
        url: "https://scholar.google.com/citations?user=zDZuloYAAAAJ&hl=en"

  - title: "Research Intern"
    institution: "Adobe Research"
    location: ""
    date: "2021"
    description: "Worked on Large Language Models."

education:
  - degree: "MSc Advanced Computer Science"
    institution: "University of Oxford"
    location: "Oxford, UK"
    date: "2021 - 2022"
    description: "Thesis on improving simulations for Google's supremacy circuits."
    advisor:
      name: "Prof. Aleks Kissinger"
      url: "https://www.cs.ox.ac.uk/people/aleks.kissinger/"

  - degree: "BTech Computer Science & Engineering"
    institution: "Indian Institute of Technology Kanpur"
    location: "Kanpur, India"
    date: "2017 - 2021"
    description: "Thesis on Quantum Query Complexity."
    advisor:
      name: "Prof. Rajat Mittal"
      url: "https://www.cse.iitk.ac.in/users/rmittal/"
```

**Step 2: Add experience section to about.html**

After the bio content div and before the News section, add:
```html
<!-- Work Experience -->
{% if page.experience and site.data.experience %}
<div class="experience-section">
  <h2><i class="fas fa-briefcase"></i> Experience</h2>
  {% for item in site.data.experience.work %}
  <div class="experience-item">
    <div class="experience-date">{{ item.date }}</div>
    <div class="experience-details">
      <h4>{{ item.title }}</h4>
      <div class="experience-institution">{{ item.institution }}</div>
      {% if item.location %}<div class="experience-location"><i class="fas fa-map-marker-alt"></i> {{ item.location }}</div>{% endif %}
      {% if item.description %}<p class="experience-description">{{ item.description }}</p>{% endif %}
    </div>
  </div>
  {% endfor %}

  <h2><i class="fas fa-graduation-cap"></i> Education</h2>
  {% for item in site.data.experience.education %}
  <div class="experience-item">
    <div class="experience-date">{{ item.date }}</div>
    <div class="experience-details">
      <h4>{{ item.degree }}</h4>
      <div class="experience-institution">{{ item.institution }}</div>
      {% if item.location %}<div class="experience-location"><i class="fas fa-map-marker-alt"></i> {{ item.location }}</div>{% endif %}
      {% if item.advisor %}<div class="experience-advisor">Advisor: <a href="{{ item.advisor.url }}">{{ item.advisor.name }}</a></div>{% endif %}
      {% if item.description %}<p class="experience-description">{{ item.description }}</p>{% endif %}
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}
```

**Step 3: Add experience styles to `_base.scss`**

```scss
// Experience Section
.experience-section {
  margin-bottom: 2.5rem;

  h2 {
    font-size: 1.35rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--global-divider-color);

    i {
      color: var(--global-theme-color);
      margin-right: 0.5rem;
      font-size: 1.1rem;
    }
  }

  .experience-item {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.25rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--global-divider-color);

    &:last-child {
      border-bottom: none;
      margin-bottom: 0;
    }

    .experience-date {
      flex-shrink: 0;
      width: 120px;
      font-size: 0.85rem;
      color: var(--global-text-color-light);
      font-weight: 500;
      padding-top: 2px;
    }

    .experience-details {
      flex: 1;

      h4 {
        font-size: 1rem;
        font-weight: 600;
        margin: 0 0 0.25rem 0;
      }

      .experience-institution {
        font-size: 0.95rem;
        color: var(--global-text-color);
        margin-bottom: 0.125rem;
      }

      .experience-location {
        font-size: 0.85rem;
        color: var(--global-text-color-light);
        margin-bottom: 0.25rem;

        i { margin-right: 0.25rem; font-size: 0.8rem; }
      }

      .experience-advisor {
        font-size: 0.85rem;
        color: var(--global-text-color-light);
        margin-bottom: 0.25rem;
      }

      .experience-description {
        font-size: 0.9rem;
        color: var(--global-text-color-light);
        margin: 0.25rem 0 0 0;
        line-height: 1.5;
      }
    }
  }
}

@media (max-width: 576px) {
  .experience-section .experience-item {
    flex-direction: column;
    gap: 0.25rem;

    .experience-date {
      width: auto;
    }
  }
}
```

**Step 4: Enable experience in about.md**

Add `experience: true` to the frontmatter.

**Step 5: Verify locally**

Run: `bundle exec jekyll serve`
Expected: Work Experience and Education sections appear on homepage with clean timeline-style layout.

**Step 6: Commit**

```bash
git add _data/experience.yml _layouts/about.html _sass/_base.scss _pages/about.md
git commit -m "feat: add work experience and education sections to homepage"
```

---

### Task 4: Improve News Section with Show More/Less Toggle

**Files:**
- Modify: `_includes/news.html`
- Modify: `_sass/_base.scss` (news styles)

**Step 1: Read current news.html include**

Read `_includes/news.html` to understand the current implementation.

**Step 2: Update news.html with show more/less**

The news section should:
- Show the first 3 items by default
- Have a "Show More" button that reveals the rest
- Each news item shows date + inline content
- Clean, minimal design with subtle date styling

Replace the news include with:
```html
<div class="news-section">
  {%- assign news = site.news | reverse -%}
  <ul class="news-list">
    {%- for item in news -%}
    <li class="news-item{% if forloop.index > 3 %} news-hidden{% endif %}">
      <span class="news-date">{{ item.date | date: "%b %Y" }}</span>
      <span class="news-content">
        {%- if item.inline -%}
          {{ item.content | remove: '<p>' | remove: '</p>' | strip }}
        {%- else -%}
          <a class="news-title" href="{{ item.url | relative_url }}">{{ item.title }}</a>
        {%- endif -%}
      </span>
    </li>
    {%- endfor -%}
  </ul>
  {%- if news.size > 3 %}
  <button class="news-toggle" onclick="toggleNews(this)">Show More</button>
  {%- endif %}
</div>

<script>
function toggleNews(btn) {
  var items = document.querySelectorAll('.news-hidden');
  var isShowing = btn.textContent === 'Show More';
  items.forEach(function(item) {
    item.style.display = isShowing ? 'flex' : 'none';
  });
  btn.textContent = isShowing ? 'Show Less' : 'Show More';
}
</script>
```

**Step 3: Add news styles to `_base.scss`**

```scss
// News Section
.news-section {
  margin-bottom: 1.5rem;

  .news-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .news-item {
    display: flex;
    gap: 1rem;
    padding: 0.5rem 0;
    align-items: baseline;

    &.news-hidden {
      display: none;
    }

    .news-date {
      flex-shrink: 0;
      width: 70px;
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--global-theme-color);
    }

    .news-content {
      font-size: 0.9rem;
      color: var(--global-text-color);
      line-height: 1.5;
    }
  }

  .news-toggle {
    background: none;
    border: 1px solid var(--global-divider-color);
    color: var(--global-text-color-light);
    padding: 0.35rem 1rem;
    font-size: 0.8rem;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 0.75rem;
    transition: all 0.2s ease;

    &:hover {
      border-color: var(--global-theme-color);
      color: var(--global-theme-color);
    }
  }
}
```

**Step 4: Verify locally**

Run: `bundle exec jekyll serve`
Expected: News section shows 3 items with a "Show More" button that reveals the rest.

**Step 5: Commit**

```bash
git add _includes/news.html _sass/_base.scss
git commit -m "feat: add show more/less toggle to news section"
```

---

### Task 5: Add In-Page Sidebar Navigation for Homepage

**Files:**
- Modify: `_layouts/about.html` (wrap content in sidebar layout)
- Modify: `_sass/_base.scss` (sidebar styles)

**Step 1: Add sidebar navigation to about.html**

Wrap the existing content in a two-column layout. The sidebar contains anchor links to each section. The sidebar is sticky and follows scroll.

The about.html layout should become:
```html
---
layout: default
---
<div class="about-page">
  <!-- Sidebar Navigation -->
  <nav class="about-sidebar" id="about-sidebar">
    <ul>
      <li><a href="#about" class="sidebar-link active">About Me</a></li>
      {% if page.news and site.announcements.enabled %}<li><a href="#news" class="sidebar-link">News</a></li>{% endif %}
      {% if page.experience %}<li><a href="#experience" class="sidebar-link">Experience</a></li>{% endif %}
      {% if page.selected_papers %}<li><a href="#publications" class="sidebar-link">Publications</a></li>{% endif %}
      {% if page.hobbies %}<li><a href="#beyond-research" class="sidebar-link">Beyond Research</a></li>{% endif %}
    </ul>
  </nav>

  <!-- Main Content -->
  <div class="about-content">
    <!-- Profile Hero -->
    ...existing profile hero...

    <!-- Bio -->
    <div id="about" class="about-section-anchor">
      {{ content }}
    </div>

    <!-- News -->
    ...existing news section with id="news"...

    <!-- Experience -->
    ...existing experience section with id="experience"...

    <!-- Publications -->
    ...existing publications section with id="publications"...

    <!-- Beyond Research -->
    ...existing hobbies section with id="beyond-research"...
  </div>
</div>
```

**Step 2: Add sidebar styles**

```scss
// About Page Sidebar Layout
.about-page {
  display: flex;
  gap: 2rem;
}

.about-sidebar {
  flex-shrink: 0;
  width: 180px;
  position: sticky;
  top: 80px;
  align-self: flex-start;
  max-height: calc(100vh - 100px);
  overflow-y: auto;

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
    border-left: 1px solid var(--global-divider-color);
  }

  .sidebar-link {
    display: block;
    padding: 0.4rem 0 0.4rem 1rem;
    font-size: 0.8rem;
    color: var(--global-text-color-light);
    text-decoration: none;
    border-left: 2px solid transparent;
    margin-left: -1px;
    transition: all 0.2s ease;

    &:hover {
      color: var(--global-theme-color);
    }

    &.active {
      color: var(--global-theme-color);
      border-left-color: var(--global-theme-color);
      font-weight: 500;
    }
  }
}

.about-content {
  flex: 1;
  min-width: 0;
}

@media (max-width: 992px) {
  .about-sidebar {
    display: none;
  }

  .about-page {
    display: block;
  }
}
```

**Step 3: Add scroll-spy JavaScript**

Add to about.html (before closing div):
```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  var sections = document.querySelectorAll('[id]');
  var links = document.querySelectorAll('.sidebar-link');

  function updateActive() {
    var scrollPos = window.scrollY + 100;
    var activeLink = null;

    sections.forEach(function(section) {
      if (section.offsetTop <= scrollPos) {
        var id = section.getAttribute('id');
        var link = document.querySelector('.sidebar-link[href="#' + id + '"]');
        if (link) activeLink = link;
      }
    });

    links.forEach(function(l) { l.classList.remove('active'); });
    if (activeLink) activeLink.classList.add('active');
  }

  window.addEventListener('scroll', updateActive);
  updateActive();

  // Smooth scroll for sidebar links
  links.forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
});
</script>
```

**Step 4: Verify locally**

Run: `bundle exec jekyll serve`
Expected: Sidebar navigation appears on the left side of the homepage, highlights the current section on scroll, and smooth-scrolls when clicking links. On mobile, the sidebar is hidden.

**Step 5: Commit**

```bash
git add _layouts/about.html _sass/_base.scss
git commit -m "feat: add sticky sidebar navigation to homepage"
```

---

### Task 6: Polish Section Headers & Spacing

**Files:**
- Modify: `_layouts/about.html` (consistent section structure)
- Modify: `_sass/_base.scss` (section header styles)

**Step 1: Ensure all homepage sections have consistent header style**

Each section (News, Experience, Publications, Beyond Research) should use:
```html
<div id="section-id" class="homepage-section">
  <h2 class="section-heading"><i class="fas fa-icon"></i> Section Title</h2>
  ...content...
</div>
```

Icons per section:
- News: `fa-newspaper`
- Experience: `fa-briefcase`
- Education: `fa-graduation-cap`
- Publications: `fa-book`
- Beyond Research: `fa-heart`

**Step 2: Add section heading styles**

```scss
.homepage-section {
  margin-bottom: 2.5rem;
  scroll-margin-top: 80px;

  .section-heading {
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--global-text-color);
    margin-bottom: 1.25rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--global-divider-color);

    i {
      color: var(--global-theme-color);
      margin-right: 0.5rem;
      font-size: 1.1rem;
    }
  }
}
```

**Step 3: Verify sections have consistent spacing and alignment**

All sections should have uniform margin-bottom, heading style, and content padding.

**Step 4: Commit**

```bash
git add _layouts/about.html _sass/_base.scss
git commit -m "feat: polish section headers with consistent styling and icons"
```

---

### Task 7: Simplify Bio & Clean Up About Content

**Files:**
- Modify: `_pages/about.md`

**Step 1: Simplify the about page bio**

Keep the bio concise and professional. Remove the Research Interests HTML block (it's verbose) and replace with a cleaner, shorter format:

```markdown
---
layout: about
title: about
permalink: /
subtitle: <a href='https://www.qcware.com/'>QC Ware</a> | <a href='https://www.lip6.fr/?LANG=en'>LIP6</a> | <a href='https://www.sorbonne-universite.fr/'>Sorbonne Universite</a>

profile:
  align: right
  image: prof_pic.jpg
  image_circular: true

news: true
selected_papers: true
hobbies: true
experience: true
---

I am a CIFRE PhD Student at LIP6/CNRS - Sorbonne University and [QC Ware](https://www.qcware.com/), working with [Prof. Elham Kashefi](https://www.lip6.fr/actualite/personnes-fiche.php?ident=P1427) and [Dr. Brian Coyle](https://scholar.google.com/citations?user=zDZuloYAAAAJ&hl=en).

My research focuses on **quantum and quantum-inspired algorithms for machine learning** — exploring both theoretical foundations and practical applications on near-term quantum devices. I'm particularly interested in variational quantum algorithms, quantum-enhanced reinforcement learning, and parameter-efficient fine-tuning with quantum-inspired methods.

Previously, I completed my MSc at the [University of Oxford](https://www.cs.ox.ac.uk/) (2022), where I worked on improving simulations for Google's supremacy circuits with [Prof. Aleks Kissinger](https://www.cs.ox.ac.uk/people/aleks.kissinger/). Before that, I studied at [IIT Kanpur](https://www.cse.iitk.ac.in/) (BTech, CSE), where I explored quantum query complexity with [Prof. Rajat Mittal](https://www.cse.iitk.ac.in/users/rmittal/).

I've also spent time at [Adobe Research](https://research.adobe.com/) working on [LLMs](https://aclanthology.org/2021.emnlp-main.798/).
```

**Step 2: Verify locally**

Run: `bundle exec jekyll serve`
Expected: Bio reads cleanly — concise, professional, no verbose HTML blocks.

**Step 3: Commit**

```bash
git add _pages/about.md
git commit -m "refactor: simplify bio for cleaner professional presentation"
```

---

### Task 8: Dark Mode Polish & Color Refinement

**Files:**
- Modify: `_sass/_themes.scss` (refine dark mode colors)
- Modify: `_sass/_variables.scss` (adjust accent color)

**Step 1: Refine the color scheme for a more modern feel**

Update accent color to a slightly warmer, more modern blue:
```scss
$accent-color: #5B9BD5 !default;  // Softer blue accent
$accent-color-light: #8BBCE8 !default;
```

**Step 2: Polish dark mode theme**

In `_themes.scss`, refine dark mode to be warmer and more readable:
```scss
html[data-theme='dark'] {
  --global-bg-color: #0F1117;
  --global-bg-secondary: #181B25;
  --global-card-bg-color: #181B25;
  --global-text-color: #E1E4E8;
  --global-text-color-light: #8B949E;
  --global-divider-color: #21262D;
  --global-border-color: #21262D;
}
```

**Step 3: Verify both light and dark mode look good**

Run: `bundle exec jekyll serve`
Toggle dark mode. Check all sections render properly in both modes.

**Step 4: Commit**

```bash
git add _sass/_themes.scss _sass/_variables.scss
git commit -m "feat: refine color scheme and polish dark mode"
```

---

### Task 9: Add Smooth Page Transitions & Hover Polish

**Files:**
- Modify: `_sass/_base.scss` (add animation utilities)

**Step 1: Add smooth transitions and hover effects**

Add to `_base.scss`:
```scss
// Smooth scroll globally
html {
  scroll-behavior: smooth;
}

// Subtle fade-in animation
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.about-content > * {
  animation: fadeIn 0.4s ease both;
}

// Better link hover transitions
a {
  transition: color 0.2s ease;
}

// Card hover lift effect
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--global-shadow-md);
  }
}

// Publication item hover
.publications ol.bibliography li {
  transition: background-color 0.2s ease;
  padding: 0.75rem;
  border-radius: 6px;

  &:hover {
    background-color: var(--global-bg-secondary, #f8f9fa);
  }
}
```

**Step 2: Verify animations are subtle and not distracting**

Run: `bundle exec jekyll serve`
Expected: Page loads with subtle fade-in. Hovering on cards and publication items shows smooth effects.

**Step 3: Commit**

```bash
git add _sass/_base.scss
git commit -m "feat: add smooth transitions and hover polish"
```

---

### Task 10: Final Integration Test & Cleanup

**Files:**
- All modified files

**Step 1: Run full build**

```bash
bundle exec jekyll build
```
Expected: Build completes without errors.

**Step 2: Run local server and test all pages**

```bash
bundle exec jekyll serve
```

Test checklist:
- [ ] Homepage loads with new profile hero, sidebar, experience sections
- [ ] Dark mode toggle works correctly
- [ ] Sidebar highlights correct section on scroll
- [ ] "Show More" in news works
- [ ] Publications section renders correctly
- [ ] Mobile responsive layout works (sidebar hidden, content stacks)
- [ ] All navigation links work
- [ ] All other pages (publications, projects, talks, cv) still work

**Step 3: Fix any visual issues found during testing**

Address any spacing, color, or layout issues.

**Step 4: Final commit**

```bash
git add -A
git commit -m "chore: final polish and integration fixes for redesign"
```

---

## Execution Notes

- **Do NOT change the Jekyll framework** — all changes are CSS/HTML/Liquid templates
- **Preserve all existing content** — we're changing presentation, not content
- **Test dark mode at every step** — easy to break with new styles
- **Mobile responsiveness matters** — test at 375px width too
- **Back up before starting** — the git history is the backup, but commit frequently

---
