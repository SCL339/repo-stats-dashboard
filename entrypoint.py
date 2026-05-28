#!/usr/bin/env python3
"""
repo-stats-dashboard — GitHub Action entrypoint.

Generates a pretty HTML dashboard of repository statistics (stars, issues, PRs,
commits) and writes it to a specified output directory. Designed to run as a
Docker-based GitHub Action, but can also be executed locally for testing.
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone

from github import Github, GithubException
from jinja2 import Environment, FileSystemLoader


def parse_args(argv: list[str]) -> dict:
    """Parse CLI arguments passed by the GitHub Action runner."""
    args = {
        "token":        argv[1] if len(argv) > 1 else os.environ.get("GITHUB_TOKEN", ""),
        "owner":        argv[2] if len(argv) > 2 else "",
        "repo":         argv[3] if len(argv) > 3 else "",
        "days":         int(argv[4]) if len(argv) > 4 else 30,
        "title":        argv[5] if len(argv) > 5 else "Repository Stats Dashboard",
        "output_dir":   argv[6] if len(argv) > 6 else "dashboard",
    }
    return args


def collect_stats(gh: Github, owner: str, repo_name: str, days: int) -> dict:
    """
    Collect all relevant stats from the GitHub API for a given repository.

    Returns a dictionary suitable for rendering into the HTML template.
    """
    repo = gh.get_repo(f"{owner}/{repo_name}")

    # Basic info
    stats = {
        "owner":          owner,
        "repo":           repo_name,
        "full_name":      repo.full_name,
        "description":    repo.description or "No description",
        "language":       repo.language or "N/A",
        "topics":         repo.get_topics(),
        "license":        repo.license.spdx_id if repo.license else "N/A",
        "fork_count":     repo.forks_count,
        "watchers":       repo.subscribers_count,
        "created_at":     repo.created_at.isoformat() if repo.created_at else "N/A",
        "updated_at":     repo.updated_at.isoformat() if repo.updated_at else "N/A",
        "default_branch": repo.default_branch,
        "open_issues_count": repo.open_issues_count,
        "html_url":       repo.html_url,
    }

    # Stars (all time + trend)
    stars = list(repo.get_stargazers_with_dates())
    stats["star_count"] = len(stars)

    # Star timeline (daily bucketed)
    stats["star_timeline"] = _bucket_timeline(
        [s.starred_at for s in stars if s.starred_at],
        days,
    )

    # Open issues (excluding PRs)
    open_issues = list(repo.get_issues(state="open", sort="created", direction="desc"))
    stats["issues"] = []
    for iss in open_issues[:50]:  # cap at 50 for display
        if iss.pull_request is None:  # real issues only
            stats["issues"].append({
                "number":    iss.number,
                "title":     iss.title,
                "state":     iss.state,
                "created":   iss.created_at.isoformat(),
                "html_url":  iss.html_url,
                "labels":    [l.name for l in iss.labels],
                "comments":  iss.comments,
            })
    stats["open_issue_count"] = len(stats["issues"])

    # Issue timeline
    issue_dates = [
        i.created_at for i in open_issues[:200]
        if i.pull_request is None and i.created_at
    ]
    stats["issue_timeline"] = _bucket_timeline(issue_dates, days)

    # Pull requests
    open_prs = list(repo.get_pulls(state="open", sort="created", direction="desc"))
    stats["prs"] = []
    for pr in open_prs[:50]:
        stats["prs"].append({
            "number":    pr.number,
            "title":     pr.title,
            "state":     pr.state,
            "created":   pr.created_at.isoformat(),
            "html_url":  pr.html_url,
            "draft":     pr.draft,
            "labels":    [l.name for l in pr.labels],
            "comments":  pr.comments,
            "review_comments": pr.review_comments,
        })
    stats["open_pr_count"] = len(stats["prs"])

    # PR timeline
    pr_dates = [p.created_at for p in open_prs if p.created_at]
    stats["pr_timeline"] = _bucket_timeline(pr_dates, days)

    # Commits (on default branch, recent)
    try:
        commits = list(repo.get_commits(sha=stats["default_branch"], until=datetime.now(timezone.utc)))
        stats["commit_count"] = len(commits)
        stats["commits"] = []
        for cm in commits[:50]:
            stats["commits"].append({
                "sha":       cm.sha[:8],
                "message":   (cm.commit.message or "").split("\n")[0],
                "author":    cm.commit.author.name if cm.commit.author else "Unknown",
                "date":      cm.commit.author.date.isoformat() if cm.commit.author and cm.commit.author.date else "N/A",
                "html_url":  cm.html_url,
            })
        # Commit timeline
        commit_dates = [
            cm.commit.author.date for cm in commits
            if cm.commit.author and cm.commit.author.date
        ]
        stats["commit_timeline"] = _bucket_timeline(commit_dates, days)
    except GithubException:
        stats["commit_count"] = 0
        stats["commits"] = []
        stats["commit_timeline"] = {}

    # Pull request counts by state (queried separately for accuracy)
    try:
        merged_prs = list(repo.get_pulls(state="closed", sort="updated", direction="desc"))
        stats["merged_pr_count"] = sum(1 for p in merged_prs if p.merged)
        stats["closed_pr_count"] = len(merged_prs) - stats["merged_pr_count"]
    except GithubException:
        stats["merged_pr_count"] = 0
        stats["closed_pr_count"] = 0

    stats["generated_at"] = datetime.now(timezone.utc).isoformat()

    return stats


def _bucket_timeline(dates: list[datetime], days: int) -> dict[str, int]:
    """
    Bucket a list of datetime objects into daily counts for the last N days.

    Returns a dict of 'YYYY-MM-DD' -> count, with zero counts for gaps.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    timeline: dict[str, int] = {}

    # Initialise all days with zero
    for i in range(days):
        day = (cutoff + timedelta(days=i)).strftime("%Y-%m-%d")
        timeline[day] = 0

    for dt in dates:
        # Ensure datetime is timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt >= cutoff:
            key = dt.strftime("%Y-%m-%d")
            if key in timeline:
                timeline[key] += 1

    return timeline


def render_dashboard(stats: dict, title: str) -> str:
    """
    Render the stats dictionary through a Jinja2 template and return HTML.
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("dashboard.html.j2")

    # Pass timeline data as sorted lists for Chart.js
    timeline_dates = sorted(stats.get("star_timeline", {}).keys())
    stats["chart_labels"] = json.dumps(timeline_dates)
    stats["chart_stars"] = json.dumps([stats["star_timeline"].get(d, 0) for d in timeline_dates])
    stats["chart_issues"] = json.dumps([stats["issue_timeline"].get(d, 0) for d in timeline_dates])
    stats["chart_prs"] = json.dumps([stats["pr_timeline"].get(d, 0) for d in timeline_dates])
    stats["chart_commits"] = json.dumps([stats["commit_timeline"].get(d, 0) for d in timeline_dates])

    return template.render(stats=stats, title=title)


def main() -> None:
    args = parse_args(sys.argv)

    gh = Github(args["token"])
    owner = args["owner"]
    repo_name = args["repo"]
    days = args["days"]
    title = args["title"]
    output_dir = args["output_dir"]

    print(f"::group::repo-stats-dashboard")
    print(f"Owner : {owner}")
    print(f"Repo  : {repo_name}")
    print(f"Days  : {days}")
    print(f"Title : {title}")
    print(f"Output: {output_dir}")

    print("Collecting stats from GitHub API...")
    stats = collect_stats(gh, owner, repo_name, days)

    print("Rendering dashboard HTML...")
    html = render_dashboard(stats, title)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    abs_path = os.path.abspath(output_path)
    print(f"Dashboard written to: {abs_path}")
    print(f"Dashboard size: {len(html)} bytes")

    # Set output for GitHub Actions
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"dashboard-path={abs_path}\n")

    # Set step summary for GitHub Actions
    github_step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_step_summary:
        with open(github_step_summary, "a") as f:
            f.write(html)

    print("::endgroup::")


if __name__ == "__main__":
    main()
