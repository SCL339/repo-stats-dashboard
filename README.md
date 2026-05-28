# repo-stats-dashboard

A **Docker-based GitHub Action** that generates a pretty HTML dashboard of your repository's stats — stars, issues, pull requests, and commits — then uploads it as a GitHub Pages artifact.

## Badges

[![GitHub release](https://img.shields.io/github/v/release/SCL339/repo-stats-dashboard?logo=github&logoColor=white)](https://github.com/SCL339/repo-stats-dashboard/releases)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-repo--stats--dashboard-blue?logo=github-actions&logoColor=white)](https://github.com/marketplace/actions/repo-stats-dashboard)
[![License](https://img.shields.io/github/license/SCL339/repo-stats-dashboard)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/SCL339/repo-stats-dashboard?style=social)](https://github.com/SCL339/repo-stats-dashboard)
[![GitHub issues](https://img.shields.io/github/issues/SCL339/repo-stats-dashboard?logo=github)](https://github.com/SCL339/repo-stats-dashboard/issues)
[![Docker](https://img.shields.io/badge/Docker-based-blue?logo=docker&logoColor=white)](https://github.com/SCL339/repo-stats-dashboard/blob/main/Dockerfile)

## Features

- **Live charts** — time-series line charts (Chart.js) for stars, issues, PRs, and commits over the last N days
- **Repository overview** — language, license, topics, fork/watcher counts
- **Recent commits** — the latest 50 commits with SHA, message, author, date
- **Open issues** — list of open issues with labels and comment counts
- **Open pull requests** — list of open PRs with draft status and label info
- **GitHub Pages ready** — writes `index.html` to a folder you can upload with `actions/upload-pages-artifact`
- **Dark theme** — matches GitHub's dark mode aesthetic

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | GitHub token with repo access | No | `${{ github.token }}` |
| `owner` | Repository owner (user or org) | No | `${{ github.repository_owner }}` |
| `repo` | Repository name | No | `${{ github.event.repository.name }}` |
| `days` | Number of days of history to display | No | `30` |
| `title` | Custom title for the dashboard page | No | `Repository Stats Dashboard` |
| `output_dir` | Directory to write `index.html` | No | `dashboard` |

## Outputs

| Output | Description |
|--------|-------------|
| `dashboard-path` | Absolute path to the generated `index.html` |

## Usage Example

```yaml
name: Stats Dashboard

on:
  schedule:
    - cron: '0 6 * * *'   # every day at 06:00 UTC
  workflow_dispatch:       # manual trigger

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate repo stats dashboard
        id: dashboard
        uses: SCL339/repo-stats-dashboard@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          days: 30

      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ${{ steps.dashboard.outputs.dashboard-path }}

  deploy:
    needs: build-dashboard
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Local Development / Testing

You need a GitHub personal access token with `repo` scope.

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (template path is relative to entrypoint.py)
GITHUB_TOKEN=ghp_xxx python entrypoint.py \
    "ghp_xxx" \
    "SCL339" \
    "my-repo" \
    30 \
    "My Dashboard" \
    "dashboard"

# Open the result
open dashboard/index.html
```

## Project Structure

```
repo-stats-dashboard/
├── action.yml           # Action metadata & input definitions
├── Dockerfile           # Docker image definition (Python 3.12)
├── entrypoint.py        # Main entrypoint — collects stats & renders HTML
├── requirements.txt     # Python dependencies
├── templates/
│   └── dashboard.html.j2  # Jinja2 HTML template with Chart.js
└── README.md            # This file
```



---

## 🤝 Support

If you find this project useful, consider supporting my work:

- 💖 **赞助支持 (Sponsor)**: 支付宝 `18559219554`
- ☁️ **Get $200 free credit** on [DigitalOcean](https://www.digitalocean.com/?refcode=scl339-01&utm_campaign=Referral_Invite&utm_medium=opensource&utm_source=SCL339)
- 🚀 **Deploy your frontend** on [Vercel](https://vercel.com/?utm_source=scl339&utm_campaign=oss)
- ⭐ **Star this repo** to help others discover it


## 📄 License

MIT

## GitHub Marketplace

This action is listed on the [GitHub Marketplace](https://github.com/marketplace/actions/repo-stats-dashboard).  
Follow the steps below to publish a new version:

1. Update the version tag (e.g., `v1.0.0`) and push
2. Create a GitHub Release — the Marketplace syncs automatically
3. Ensure `.github/marketplace.yml` and `branding` in `action.yml` are correct
