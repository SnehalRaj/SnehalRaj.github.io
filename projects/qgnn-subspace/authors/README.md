# Author headshots

Replace the placeholder initials avatars with a square image per author
(recommended ≥ 256×256, JPG or PNG). Keep the exact filenames:

| file | author |
|------|--------|
| `raj.jpg`              | Snehal Raj |
| `coyle.jpg`            | Brian Coyle |
| `monbroussou.jpg`      | Léo Monbroussou |
| `ferreira-martins.jpg` | André J. Ferreira-Martins |
| `farias.jpg`           | Renato M. S. Farias |
| `kashefi.jpg`          | Elham Kashefi |

Displayed as 58px circles (`object-fit: cover`), so a square crop looks best.
After replacing, rebuild and re-embed:

```bash
npm run build
rsync -a --delete dist/ /Users/snehal/PhD/career/SnehalRaj.github.io/projects/qgnn-subspace/
```
