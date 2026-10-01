import os
import re
import json
from typing import Dict, Any, List, Optional

class GitHubSEOAgent:
    """
    A self-contained GitHub SEO engine.
    """

    def __init__(self, repo_owner: str, repo_name: str, repo_dir: Optional[str] = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_dir = repo_dir
        # Default generic keywords. Example specific keywords (e.g. for linkedin-agent):
        # [{'keyword': 'linkedin automation', 'volume': 8000, 'difficulty': 'medium'}, ...]
        self.keywords = [
            {'keyword': 'open-source', 'volume': 'high', 'difficulty': 'low'},
            {'keyword': 'github', 'volume': 'high', 'difficulty': 'low'},
            {'keyword': 'developer-tools', 'volume': 'high', 'difficulty': 'medium'},
            {'keyword': 'automation', 'volume': 'high', 'difficulty': 'medium'},
            {'keyword': 'python', 'volume': 'high', 'difficulty': 'low'},
            {'keyword': 'cli', 'volume': 'medium', 'difficulty': 'low'}
        ]

    def audit_repository(self) -> Dict[str, Any]:
        """Audits the local repo directory for SEO and community health."""
        score = 0
        max_score = 100
        checklist = []
        
        has_readme = False
        readme_rich = False
        has_badges = False
        has_ci = False
        has_issue_templates = False
        has_contributing = False
        has_security = False
        has_comparison = False
        has_license = False

        if self.repo_dir and os.path.exists(self.repo_dir):
            readme_path = os.path.join(self.repo_dir, 'README.md')
            if os.path.exists(readme_path):
                has_readme = True
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content.encode('utf-8')) > 500:
                        readme_rich = True
                    
                    badges = re.findall(r'img\.shields\.io', content)
                    if len(badges) >= 4:
                        has_badges = True
                        
                    if 'vs' in content.lower() or 'comparison' in content.lower() or 'competitor' in content.lower():
                        has_comparison = True

            workflows_dir = os.path.join(self.repo_dir, '.github', 'workflows')
            if os.path.exists(workflows_dir) and any(f.endswith('.yml') for f in os.listdir(workflows_dir)):
                has_ci = True
                
            issue_template_dir = os.path.join(self.repo_dir, '.github', 'ISSUE_TEMPLATE')
            if os.path.exists(issue_template_dir) and len(os.listdir(issue_template_dir)) > 0:
                has_issue_templates = True
                
            if os.path.exists(os.path.join(self.repo_dir, 'CONTRIBUTING.md')):
                has_contributing = True
                
            if os.path.exists(os.path.join(self.repo_dir, 'SECURITY.md')):
                has_security = True
                
            if os.path.exists(os.path.join(self.repo_dir, 'LICENSE')) or os.path.exists(os.path.join(self.repo_dir, 'LICENSE.md')):
                has_license = True

        if has_readme: score += 10; checklist.append('README.md exists')
        if readme_rich: score += 15; checklist.append('README.md is rich (>500 bytes)')
        if has_badges: score += 10; checklist.append('Contains >=4 shields.io badges')
        if has_ci: score += 15; checklist.append('GitHub Actions CI workflow exists')
        if has_issue_templates: score += 10; checklist.append('Issue/PR templates exist')
        if has_contributing: score += 10; checklist.append('CONTRIBUTING.md exists')
        if has_security: score += 10; checklist.append('SECURITY.md exists')
        if has_comparison: score += 10; checklist.append('Comparison/competitor section in README')
        if has_license: score += 10; checklist.append('LICENSE file exists')

        grade = 'F'
        if score >= 90: grade = 'A+'
        elif score >= 80: grade = 'A'
        elif score >= 70: grade = 'B'
        elif score >= 60: grade = 'C'
        elif score >= 50: grade = 'D'

        return {
            'score': score,
            'grade': grade,
            'checklist': checklist,
            'recommended_topics': [k['keyword'] for k in self.keywords]
        }

    def set_keywords(self, keywords: List[Dict]):
        """Sets the target keywords for SEO optimization."""
        self.keywords = keywords

    def get_top_keywords(self) -> List[Dict]:
        """Returns configured target keywords."""
        return self.keywords

    def generate_optimized_readme(self, project_name: str, tagline: str, features: List[str], tech_stack: List[str]) -> str:
        """Generates a search-optimized README template."""
        topics = ", ".join([k['keyword'] for k in self.keywords])
        features_list = "\n".join([f"- {feat}" for feat in features])
        tech_list = "\n".join([f"- {tech}" for tech in tech_stack])

        lines = [
            f"# {project_name}",
            "",
            f"> {tagline}",
            "",
            f"![GitHub stars](https://img.shields.io/github/stars/{self.repo_owner}/{self.repo_name}?style=social)",
            f"![GitHub forks](https://img.shields.io/github/forks/{self.repo_owner}/{self.repo_name}?style=social)",
            f"![License](https://img.shields.io/github/license/{self.repo_owner}/{self.repo_name})",
            f"![CI](https://img.shields.io/github/workflow/status/{self.repo_owner}/{self.repo_name}/CI)",
            "",
            "## Overview",
            f"{project_name} is designed to help with {topics}.",
            "",
            "## Features",
            features_list,
            "",
            "## Tech Stack",
            tech_list,
            "",
            "## Comparison",
            f"| Feature | {project_name} | Alternatives |",
            "|---|---|---|",
            "| Speed | Fast | Slow |",
            "| Open Source | Yes | No |",
            "",
            "## License",
            "MIT License",
        ]
        return "\n".join(lines)

    def generate_launch_pack(self, channel: str = 'all') -> Dict[str, str]:
        """Generates curated launch copy for different platforms."""
        packs = {
            'hacker_news': f"Show HN: {self.repo_name} - An open-source tool for {self.keywords[0]['keyword']}.",
            'reddit': f"I built {self.repo_name} to solve {self.keywords[0]['keyword']} problems.",
            'twitter_thread': f"Introducing {self.repo_name}! A new way to handle {self.keywords[0]['keyword']}. Thread 🧵...",
            'product_hunt': f"{self.repo_name} - The ultimate {self.keywords[0]['keyword']} tool.",
            'release_notes': f"# Release Notes\n\nInitial release of {self.repo_name}."
        }
        if channel != 'all' and channel in packs:
            return {channel: packs[channel]}
        return packs

    def generate_community_health_files(self) -> Dict[str, Any]:
        """Creates typical community health file contents."""
        return {
            '.github/workflows/ci.yml': "name: CI\non: [push, pull_request]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v2\n      - run: echo 'CI setup'",
            '.github/ISSUE_TEMPLATE/bug_report.md': "---\nname: Bug report\nabout: Create a report to help us improve\ntitle: ''\nlabels: ''\nassignees: ''\n---\n\n**Describe the bug**",
            '.github/pull_request_template.md': "## Description\n\nFixes # (issue)",
            'CONTRIBUTING.md': "# Contributing\n\nWelcome to our project!...",
            'SECURITY.md': "# Security Policy\n\nPlease report vulnerabilities to...",
            'CODE_OF_CONDUCT.md': "# Code of Conduct\n\nBe excellent to each other."
        }

    def get_gh_cli_topics_command(self) -> str:
        """Returns the gh repo edit command for topics."""
        topics = [k['keyword'].replace(' ', '-') for k in self.keywords]
        return f"gh repo edit {self.repo_owner}/{self.repo_name} --add-topic {','.join(topics)}"
