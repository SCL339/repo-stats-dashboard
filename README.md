1|     1|     1|# repo-stats-dashboard
     2|     2|     2|
     3|     3|     3|---
     4|     4|     4|
     5|     5|     5|
     6|     6|     6|[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-repo--stats--dashboard-blue?logo=github-actions&logoColor=white)](https://github.com/marketplace/actions/repo-stats-dashboard)
     7|     7|     7|[![License](https://img.shields.io/github/license/SCL339/repo-stats-dashboard)](LICENSE)
     8|     8|     8|[![GitHub stars](https://img.shields.io/github/stars/SCL339/repo-stats-dashboard?style=social)](https://github.com/SCL339/repo-stats-dashboard)
     9|     9|     9|[![GitHub issues](https://img.shields.io/github/issues/SCL339/repo-stats-dashboard?logo=github)](https://github.com/SCL339/repo-stats-dashboard/issues)
    10|    10|    10|[![Docker](https://img.shields.io/badge/Docker-based-blue?logo=docker&logoColor=white)](https://github.com/SCL339/repo-stats-dashboard/blob/main/Dockerfile)
    11|    11|    11|
    12|    12|    12|---
    13|    13|    13|
    14|    14|    14|
    15|    15|    15|- **Repository overview** — language, license, topics, fork/watcher counts
    16|    16|    16|- **Recent commits** — the latest 50 commits with SHA, message, author, date
    17|    17|    17|- **Open issues** — list of open issues with labels and comment counts
    18|    18|    18|- **Open pull requests** — list of open PRs with draft status and label info
    19|    19|    19|- **GitHub Pages ready** — writes `index.html` to a folder you can upload with `actions/upload-pages-artifact`
    20|    20|    20|- **Dark theme** — matches GitHub's dark mode aesthetic
    21|    21|    21|
    22|    22|    22|---
    23|    23|    23|
    24|    24|    24|
    25|    25|    25||-------|-------------|----------|---------|
    26|    26|    26|| `token` | GitHub token with repo access | No | `${{ github.token }}` |
    27|    27|    27|| `owner` | Repository owner (user or org) | No | `${{ github.repository_owner }}` |
    28|    28|    28|| `repo` | Repository name | No | `${{ github.event.repository.name }}` |
    29|    29|    29|| `days` | Number of days of history to display | No | `30` |
    30|    30|    30|| `title` | Custom title for the dashboard page | No | `Repository Stats Dashboard` |
    31|    31|    31|| `output_dir` | Directory to write `index.html` | No | `dashboard` |
    32|    32|    32|
    33|    33|    33|---
    34|    34|    34|
    35|    35|    35|
    36|    36|    36||--------|-------------|
    37|    37|    37|| `dashboard-path` | Absolute path to the generated `index.html` |
    38|    38|    38|
    39|    39|    39|---
    40|    40|    40|
    41|    41|    41|
    42|    42|    42|name: Stats Dashboard
    43|    43|    43|
    44|    44|    44|on:
    45|    45|    45|  schedule:
    46|    46|    46|    - cron: '0 6 * * *'   # every day at 06:00 UTC
    47|    47|    47|  workflow_dispatch:       # manual trigger
    48|    48|    48|
    49|    49|    49|permissions:
    50|    50|    50|  contents: read
    51|    51|    51|  pages: write
    52|    52|    52|  id-token: write
    53|    53|    53|
    54|    54|    54|jobs:
    55|    55|    55|  build-dashboard:
    56|    56|    56|    runs-on: ubuntu-latest
    57|    57|    57|    steps:
    58|    58|    58|      - uses: actions/checkout@v4
    59|    59|    59|
    60|    60|    60|      - name: Generate repo stats dashboard
    61|    61|    61|        id: dashboard
    62|    62|    62|        uses: SCL339/repo-stats-dashboard@v1
    63|    63|    63|        with:
    64|    64|    64|          token: ${{ secrets.GITHUB_TOKEN }}
    65|    65|    65|          days: 30
    66|    66|    66|
    67|    67|    67|      - name: Upload Pages artifact
    68|    68|    68|        uses: actions/upload-pages-artifact@v3
    69|    69|    69|        with:
    70|    70|    70|          path: ${{ steps.dashboard.outputs.dashboard-path }}
    71|    71|    71|
    72|    72|    72|  deploy:
    73|    73|    73|    needs: build-dashboard
    74|    74|    74|    runs-on: ubuntu-latest
    75|    75|    75|    environment:
    76|    76|    76|      name: github-pages
    77|    77|    77|      url: ${{ steps.deployment.outputs.page_url }}
    78|    78|    78|    steps:
    79|    79|    79|      - name: Deploy to GitHub Pages
    80|    80|    80|        id: deployment
    81|    81|    81|        uses: actions/deploy-pages@v4
    82|    82|    82|```
    83|    83|    83|
    84|    84|    84|---
    85|    85|    85|
    86|    86|    86|EN=ghp_xxx python entrypoint.py \
    87|    87|    87|    "ghp_xxx" \
    88|    88|    88|    "SCL339" \
    89|    89|    89|    "my-repo" \
    90|    90|    90|    30 \
    91|    91|    91|    "My Dashboard" \
    92|    92|    92|    "dashboard"
    93|    93|    93|
    94|    94|    94|# Open the result
    95|    95|    95|open dashboard/index.html
    96|    96|    96|```
    97|    97|    97|
    98|    98|    98|---
    99|    99|    99|
   100|   100|   100|
   101|   101|   101|repo-stats-dashboard/
   102|   102|   102|├── action.yml           # Action metadata & input definitions
   103|   103|   103|├── Dockerfile           # Docker image definition (Python 3.12)
   104|   104|   104|├── entrypoint.py        # Main entrypoint — collects stats & renders HTML
   105|   105|   105|├── requirements.txt     # Python dependencies
   106|   106|   106|├── templates/
   107|   107|   107|│   └── dashboard.html.j2  # Jinja2 HTML template with Chart.js
   108|   108|   108|└── README.md            # This file
   109|   109|   109|```
   110|   110|   110|
   111|   111|   111|---
   112|   112|   112|
   113|   113|   113|ARKER
   114|   114|   114|- 🚀 **Deploy your frontend** on [Vercel](https://vercel.com/?utm_source=scl339&utm_campaign=oss)
   115|   115|   115|- ⭐ **Star this repo** to help others discover it
   116|   116|   116|
   117|   117|   117|
   118|   118|   118|---
   119|   119|   119|
   120|   120|   120|ARKERace syncs automatically
   121|   121|   121|3. Ensure `.github/marketplace.yml` and `branding` in `action.yml` are correct
   122|   122|   122|

---

## 🤝 赞助支持 (Sponsor)

如果这个项目对你有帮助，可以请我喝杯咖啡 ☕

- 💖 **支付宝 (Alipay)**: `18559219554` | 邮箱联系: `530765059@qq.com`
- ☁️ **DigitalOcean 联盟链接**: [免费 $200 额度](https://www.digitalocean.com/?refcode=scl339-01&utm_campaign=Referral_Invite&utm_medium=opensource&utm_source=SCL339)
- ⭐ **在 GitHub 上点 Star** 帮助更多人发现这个项目

## 📄 License
