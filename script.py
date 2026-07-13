from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
USER_NAME = "aditip149209"
OUTPUT_GIF = ROOT / "output.gif"
README_FILE = ROOT / "README.md"
ASSETS_DIR = ROOT / "assets"
PORTRAIT_FILE = ASSETS_DIR / "profile-portrait.txt"
load_dotenv(ROOT / ".env")

import gifos


DEFAULT_ASCII_PORTRAIT = r"""
        .-''''-.
      .'  .--.  '.
     /   /    \   \
    ;   ;  .--. ;   ;
    |   | (o  o)| |   |
    ;   ;  .--. ;   ;
     \   \ '--' /   /
      '.  '----'  .'
        '-.__.-'
""".strip("\n")


def fallback_stats() -> SimpleNamespace:
	return SimpleNamespace(
		account_name=USER_NAME,
		total_followers=0,
		total_stargazers=0,
		total_issues=0,
		total_commits_all_time=0,
		total_commits_last_year=0,
		total_pull_requests_made=0,
		total_pull_requests_merged=0,
		pull_requests_merge_percentage=0,
		total_pull_requests_reviewed=0,
		total_repo_contributions=0,
		languages_sorted=[("Golang", 0), ("Python", 0), ("Shell", 0)],
		user_rank=SimpleNamespace(level="Explorer"),
	)


def fetch_stats():
	try:
		return gifos.utils.fetch_github_stats(user_name=USER_NAME)
	except SystemExit:
		print("WARN: GITHUB_TOKEN is unavailable; using fallback profile data for local rendering.")
		return fallback_stats()


def format_languages(stats) -> str:
	languages = [language for language, _ in getattr(stats, "languages_sorted", [])[:5]]
	if not languages:
		return "Golang, Python, Shell"
	return ", ".join(languages[:4])


def load_portrait() -> str:
	if PORTRAIT_FILE.exists():
		return PORTRAIT_FILE.read_text(encoding="utf-8").strip("\n")
	return DEFAULT_ASCII_PORTRAIT


def render_profile_text(stats, generated_at: str) -> str:
	top_languages = format_languages(stats)
	return f"""
\x1b[30;102m{USER_NAME}@GitHub\x1b[0m
------------------------------
\x1b[92mName:\x1b[0m             {stats.account_name}
\x1b[92mRole:\x1b[0m             Software engineer / OSS builder
\x1b[92mOSS focus:\x1b[0m        Kyverno / Golang / CEL policy metrics PR #16359
\x1b[92mInternship:\x1b[0m       Sprinklr backend systems / LLM infra
\x1b[92mCP goal:\x1b[0m          Codeforces consistency and speed

\x1b[30;102mGitHub Stats\x1b[0m
------------------------------
\x1b[92mFollowers:\x1b[0m        {stats.total_followers}
\x1b[92mStars earned:\x1b[0m     {stats.total_stargazers}
\x1b[92mCommits (1y):\x1b[0m     {stats.total_commits_last_year}
\x1b[92mPRs made:\x1b[0m         {stats.total_pull_requests_made}
\x1b[92mMerged PRs:\x1b[0m       {stats.total_pull_requests_merged} ({stats.pull_requests_merge_percentage}%)
\x1b[92mRepo contribs:\x1b[0m    {stats.total_repo_contributions}
\x1b[92mTop languages:\x1b[0m    {top_languages}

\x1b[30;102mCurrent Mission\x1b[0m
------------------------------
\x1b[92mRank:\x1b[0m             {stats.user_rank.level}
\x1b[92mBuild time:\x1b[0m       {generated_at}
\x1b[92mStack:\x1b[0m            Golang / Python / systems / LLM
""".strip("\n")


def write_readme(image_source: str, generated_at: str) -> None:
	README_FILE.write_text(
		f"""<div align=\"center\">\n\n<picture>\n  <source media=\"(prefers-color-scheme: dark)\" srcset=\"{image_source}\">\n  <source media=\"(prefers-color-scheme: light)\" srcset=\"{image_source}\">\n  <img alt=\"Animated GitHub profile terminal\" src=\"{image_source}\" width=\"100%\">\n</picture>\n\n</div>\n\n## About\n\nThis profile GIF is generated with [github-readme-terminal](https://github.com/x0rzavi/github-readme-terminal) and updated automatically. It highlights live GitHub stats for [aditip149209](https://github.com/aditip149209) alongside a retro terminal layout tuned for a forest / sage palette.\n\n## Regeneration\n\nRun `python script.py` to rebuild the GIF locally.\n\n## Secrets\n\nIf you want the GitHub stats and upload flow to run in GitHub Actions, add these repository secrets manually:\n\n- `GITHUB_TOKEN` for GitHub API access used by the script\n- `IMGBB_API_KEY` if you want the workflow to publish the GIF to ImgBB before updating the README\n\n<sub>Generated automatically on {generated_at}.</sub>\n""",
		encoding="utf-8",
	)


def render_gif() -> None:
	stats = fetch_stats()
	generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

	terminal = gifos.Terminal(width=780, height=500, xpad=14, ypad=14)
	terminal.toggle_show_cursor(False)

	terminal.gen_text("booting aditip149209@github ...", 1, count=6)
	terminal.gen_text("loading github-readme-terminal profile", 2, count=4)
	terminal.gen_text("checking stats and building neofetch layout", 3, count=4)
	terminal.gen_text("", 5, count=2)
	terminal.gen_typing_text("initializing profile GIF", 6, contin=True)
	terminal.gen_text("", 7, count=2)

	terminal.clear_frame()
	terminal.gen_text("aditip149209@github:~$ neofetch", 1, count=5)
	terminal.gen_text(load_portrait(), 3, 2, contin=True)
	terminal.gen_text(render_profile_text(stats, generated_at), 3, 28, contin=True)
	terminal.gen_text("", 24, count=20, contin=True)

	terminal.gen_gif()


def upload_if_configured() -> str:
	image_url = OUTPUT_GIF.name
	if os.getenv("IMGBB_API_KEY"):
		uploaded = gifos.utils.upload_imgbb(file_name=OUTPUT_GIF.name, expiration=129600)
		image_url = uploaded.url
	return image_url


def main() -> None:
	render_gif()
	image_source = upload_if_configured()
	write_readme(image_source=image_source, generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
	print(image_source)


if __name__ == "__main__":
	main()