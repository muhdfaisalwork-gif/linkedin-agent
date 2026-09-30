import os
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
DB_PATH = os.path.join(DB_DIR, "linkedin_agent.db")

os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_connection()
    conn.execute("PRAGMA journal_mode = WAL;")
    cursor = conn.cursor()

    # Posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            hook_formula TEXT,
            founder_angle TEXT,
            content TEXT NOT NULL,
            image_url TEXT,
            image_type TEXT,
            image_prompt TEXT,
            status TEXT DEFAULT 'draft',
            scheduled_time TEXT,
            published_time TEXT,
            linkedin_urn TEXT,
            flesch_score REAL,
            ai_tell_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Post Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            impressions INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            reposts INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
        )
    ''')

    # Story Bank (Brain Knowledge & Receipts)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS story_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            metrics_receipts TEXT,
            url TEXT,
            year_or_date TEXT,
            tags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Voice Profile & Fingerprint
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tone TEXT DEFAULT 'Direct, knowledgeable, candid, builder-focused',
            cadence TEXT DEFAULT 'Natural variation, 1-2 sentence paragraphs for mobile clarity',
            preferred_phrases TEXT DEFAULT 'built, shipped, measured, cut, tested, broke',
            banned_phrases TEXT DEFAULT 'delve, pivotal, robust, game-changer, landscape, foster, leverage',
            cta_style TEXT DEFAULT 'Specific questions or flat closing receipts, no generic engagement bait',
            author_bio TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Brain Heuristics (Evolution Weights for Hook Formulas & Angles)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heuristics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formula_code TEXT UNIQUE NOT NULL,
            formula_name TEXT NOT NULL,
            category TEXT DEFAULT 'hook',
            weight REAL DEFAULT 1.0,
            usage_count INTEGER DEFAULT 0,
            avg_engagement_rate REAL DEFAULT 0.0,
            notes TEXT,
            last_evolved TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Brain Reflection Log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            learnings TEXT NOT NULL,
            strategy_shifts TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Comment Sweeps & Replies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_urn TEXT,
            comment_urn TEXT UNIQUE,
            author_name TEXT,
            author_title TEXT,
            text TEXT,
            depth INTEGER DEFAULT 1,
            top_level_urn TEXT,
            suggested_reaction TEXT,
            reply_draft TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Inbox Messages & DMs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inbox_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            sender_name TEXT,
            sender_title TEXT,
            message_text TEXT,
            intent_category TEXT,
            suggested_reply TEXT,
            status TEXT DEFAULT 'unread',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Profile Optimization Records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            current_content TEXT,
            optimized_content TEXT NOT NULL,
            scorecard JSON,
            status TEXT DEFAULT 'recommended',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # System Settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()

    # Pre-seed defaults and user's rich Story Bank & Heuristics
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Seed Story Bank with User's specific projects if empty
    cursor.execute("SELECT COUNT(*) FROM story_bank")
    if cursor.fetchone()[0] == 0:
        initial_stories = [
            (
                "Product / Systems",
                "Sultrix Trade OS",
                "Built and engineered Sultrix Trade OS, a high-performance trading operating system for automated execution and market analytics.",
                "Real-time order routing, custom trade execution engine, risk controls",
                "https://sultrixtrade.com",
                "2025-2026",
                "trading, fintech, architecture, execution"
            ),
            (
                "Product / Media",
                "Shadow Stream Video Platform & App",
                "Designed and deployed the Shadow Stream high-concurrency video streaming website and cross-platform mobile application.",
                "Sub-second video delivery, adaptive bitrate streaming, multi-platform app",
                "https://ssmovietvs.site",
                "2025-2026",
                "streaming, video, mobile-app, scalability"
            ),
            (
                "Enterprise Systems",
                "Enterprise CRM Dashboard",
                "Architected and built full-stack CRM dashboard system for real-time customer pipeline management, analytics, and operational automation.",
                "Automated lead pipeline, dynamic role-based dashboards, integrated reports",
                "https://crm.rmsol.org/preview",
                "2025-2026",
                "crm, enterprise, b2b, automation"
            ),
            (
                "Client Platform",
                "Relyguru Corporate Platform",
                "Engineered and launched Relyguru's primary digital web platform with optimized performance and conversion funnels.",
                "High-conversion UI/UX, responsive architecture, sub-second TTFB",
                "https://relygurus.com",
                "2025-2026",
                "web-architecture, conversion, client-delivery"
            ),
            (
                "Company / Agency",
                "The Raulf International LLC Platform & Services",
                "Built and launched The Raulf International LLC corporate web platform and complete enterprise services catalog (custom software development, AI solutions, web/cloud engineering).",
                "Full-cycle development, cloud deployments, bespoke engineering",
                "https://raulfinternational.com",
                "2025-2026",
                "enterprise, services, engineering, software"
            ),
            (
                "AI Agents",
                "Shadow Voice AI Agent",
                "Architected and deployed Shadow Voice, a real-time conversational voice AI agent system with sub-500ms voice-to-voice latency.",
                "Real-time telephony/WebRTC, low-latency audio processing, context tracking",
                "https://raulfinternational.com",
                "2026",
                "voice-ai, real-time, llm-agents, telephony"
            ),
            (
                "AI Agents",
                "Autonomous SEO Agents",
                "Developed autonomous AI agents that conduct keyword clustering, programmatic content engineering, internal linking optimization, and ranking telemetry.",
                "Zero-fluff programmatic SEO, content engineering at scale, ranking monitors",
                "https://raulfinternational.com",
                "2026",
                "seo-agents, autonomous-agents, ranking, growth"
            )
        ]
        cursor.executemany('''
            INSERT INTO story_bank (category, title, detail, metrics_receipts, url, year_or_date, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', initial_stories)

    # Seed Voice Profile if empty
    cursor.execute("SELECT COUNT(*) FROM voice_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO voice_profile (tone, cadence, preferred_phrases, banned_phrases, cta_style, author_bio)
            VALUES (
                'Direct, experienced founder and builder, concrete facts, no marketing fluff',
                '1-2 sentence paragraphs with whitespace, natural rhythm, zero artificial staccato',
                'built, shipped, engineered, measured, latency, deployed, architecture',
                'delve, pivotal, robust, game-changer, landscape, foster, leverage, tapestry, seamless',
                'One sharp question or a closing numbered receipt, never engagement-bait tags',
                'Founder & Software Architect. Creator of Sultrix Trade OS, Shadow Stream, Shadow Voice, and SEO Agents. Managing Member at Raulf International LLC.'
            )
        ''')

    # Seed Hook Formulas F1-F20 with baseline weights
    cursor.execute("SELECT COUNT(*) FROM heuristics")
    if cursor.fetchone()[0] == 0:
        formulas = [
            ("F1", "Platform Risk Anaphora", "hook", 1.1, 0, 0.0, "Category/platform shifts, product-as-fix"),
            ("F2", "R.I.P. Obituary", "hook", 1.0, 0, 0.0, "Era-ending claims, industry pivots"),
            ("F3", "Year-over-Year Pivot", "hook", 1.2, 0, 0.0, "Identity shifts, founder reflection"),
            ("F4", "Time-Anchor Confession", "hook", 1.0, 0, 0.0, "Specific dated lessons, scars"),
            ("F5", "Self-Proving Meta", "hook", 1.1, 0, 0.0, "Public tests, commitment posts"),
            ("F6", "Comment-Gate Lead Magnet", "hook", 0.9, 0, 0.0, "Real deliverable, high caution in 2026"),
            ("F7", "Odd-Precision Money Ledger", "hook", 1.4, 0, 0.0, "+34% reach, strongest opener, number-first"),
            ("F8", "Paid-vs-Free Reversal", "hook", 1.3, 0, 0.0, "Free framework giveaway, high multiplier"),
            ("F9", "Curiosity-Gap Teaser", "hook", 1.0, 0, 0.0, "Behind the scenes, pays off in 2 lines"),
            ("F10", "Contrarian + Historical Receipts", "hook", 1.2, 0, 0.0, "Sacred-cow takes, engineering cycles"),
            ("F11", "Emotional Cold-Open", "hook", 1.0, 0, 0.0, "Real story with emotional stakes"),
            ("F12", "Permission Slip", "hook", 0.9, 0, 0.0, "Dated facts only, anti-platitude"),
            ("F13", "Bait-and-Switch Reversal", "hook", 1.1, 0, 0.0, "Policy or process upgrade"),
            ("F14", "Named Gratitude / Tribute", "hook", 1.0, 0, 0.0, "Team and mentor tributes"),
            ("F15", "Explain-to-Kids", "hook", 1.2, 0, 0.0, "Demystifying tech jargon into plain words"),
            ("F16", "Status-Strip Humility", "hook", 1.0, 0, 0.0, "Senior voice wanting warmth not distance"),
            ("F17", "Controlled A/B Anecdote", "founder", 1.3, 0, 0.0, "One-variable engineering comparison"),
            ("F18", "False-Binary Dissolve", "founder", 1.2, 0, 0.0, "Both obvious answers fail"),
            ("F19", "Anecdote-Meets-Evidence Bridge", "founder", 1.3, 0, 0.0, "Personal noticing + data stack"),
            ("F20", "Diverging-Curves Close", "founder", 1.2, 0, 0.0, "Two trajectories that diverge")
        ]
        cursor.executemany('''
            INSERT INTO heuristics (formula_code, formula_name, category, weight, usage_count, avg_engagement_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', formulas)

    # Seed default Reflection Log
    cursor.execute("SELECT COUNT(*) FROM reflections")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO reflections (title, learnings, strategy_shifts)
            VALUES (
                'Initial Brain Calibration: 2026 LinkedIn Heuristics',
                'Posts starting with odd-precision numbers (F7) outperform questions by +34%. The first 210 characters dictate the fold click-through. AI buzzword density above 2 markers triggers the July 2026 LinkedIn slop filter penalty.',
                'Prioritizing F7 (Money Ledger), F17 (Controlled A/B), and F19 (Evidence Bridge). Injecting real project receipts from Sultrix Trade, Shadow Stream, and Shadow Voice.'
            )
        ''')

    conn.commit()
