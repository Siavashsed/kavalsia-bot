# © 2026 Kavalsia Inc. [Siavash Sadighi]
"""
Reddit Auto-Poster for Kavalsia Network
========================================
Reads already-generated backlink content (backlinks/{slug}.md in each site repo)
and posts to relevant subreddits automatically.

DISABLED BY DEFAULT — set settings.reddit.enabled = true after completing setup below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL SETUP GUIDE — READ BEFORE ENABLING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STEP 1 — Create Reddit account(s)
────────────────────────────────
→ Go to reddit.com and create a new account
→ Use a believable username — NOT "cryptobot_2026" or anything robotic
  Good examples: "market_breakdown", "the_real_trader", "danielwrites"
→ Verify email address
→ Add a profile picture (use a real photo or AI-generated face)
→ Write a short bio that matches your niche

Recommended account groupings (1 account per cluster):
  Account A → crypto, finance, wealth, business
  Account B → fitness, sport, health, supplements
  Account C → pets, baby, home decor, gifts
  Account D → makeup, dating, lifestyle
  Account E → AI/tech, ecommerce, marketing, travel, insurance, cars


STEP 2 — 30-DAY WARMING PERIOD (CRITICAL — skip this and get banned)
────────────────────────────────────────────────────────────────────
Reddit's spam filter and mods watch new accounts closely.
Post links too early = shadowban or account removal.

  DAYS 1-7 (Comment only, no links at all):
    ✓ Subscribe to 15-20 relevant subreddits for your niche cluster
    ✓ Leave 3-4 genuine helpful comments per day — answer questions, share knowledge
    ✓ Upvote 15-20 posts and comments per day
    ✓ Never mention your sites — pure community participation
    Target: 15+ comment karma by end of week 1

  DAYS 8-14 (Text posts, no links):
    ✓ Post 1-2 text-only discussions per day ("What's everyone's take on X?")
    ✓ Keep commenting (2-3/day)
    ✓ Respond to replies on your posts
    Target: 40+ karma, mix of posts and comments

  DAYS 15-21 (Occasional link posts — carefully):
    ✓ Post ONE link to your BEST article in the MOST relevant subreddit
    ✓ Wait 48 hours — if it stays up and gets engagement, you're on track
    ✓ If removed: go back to comments-only for one more week
    ✓ Continue text posts and commenting
    Target: 75+ karma, first link post live

  DAYS 22-30 (Light automation):
    ✓ Post 1 link per day, manually
    ✓ Mix with 2-3 comments per day so your profile isn't 100% self-promotion
    ✓ Read each subreddit's sidebar rules before posting
    Target: 100+ karma before enabling this bot

  MINIMUM BEFORE ENABLING BOT:
    → Account age: 30+ days
    → Karma: 100+ (mix of comment and post karma)
    → At least 2 successful manual link posts that weren't removed


STEP 3 — Create Reddit API app
───────────────────────────────
→ Log in to Reddit → go to: https://www.reddit.com/prefs/apps
→ Scroll to bottom → click "create another app"
→ Fill in:
    Name: anything (e.g. "personal script")
    Type: "script" ← important
    Description: leave blank
    Redirect URI: http://localhost:8080
→ Click "create app"
→ Note your:
    client_id:     the string UNDER your app name (looks like: aBcDeFgHiJ)
    client_secret: the "secret" field


STEP 4 — Add to network-config.json
─────────────────────────────────────
Under settings.reddit, set:

  "reddit": {
    "enabled": false,          ← change to true when ready
    "dry_run": true,           ← test with true first, then set false
    "max_posts_per_day": 2,    ← stay conservative to avoid filters
    "subreddit_cooldown_days": 7,
    "accounts": [
      {
        "id": "account-a",
        "client_id": "your_client_id_here",
        "client_secret": "your_client_secret_here",
        "username": "your_reddit_username",
        "password": "your_reddit_password",
        "user_agent": "KavalsiaBot/1.0 by u/your_reddit_username",
        "site_ids": ["crypto-insights", "trading-tech", "grow-wealth"],
        "min_age_days": 30,
        "min_karma": 100
      }
    ]
  }

STEP 5 — Test dry run
──────────────────────
→ python reddit_bot.py
→ Review what it WOULD post (no actual posts made while dry_run = true)
→ When satisfied: set dry_run = false, run again


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULES TO STAY UNBANNED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Max 1 link post per subreddit per 7 days (enforced by this bot)
• Max 2-3 link posts per account per day (enforced by this bot)
• Never post the same URL twice in the same subreddit (enforced)
• Your profile should be <50% self-promotional posts
• Always read subreddit rules before the bot posts there
• Best posting times: 9am-12pm EST weekdays for most niches
• If posts keep getting removed from a subreddit: remove it from the list
• Never buy upvotes or use vote manipulation


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAFE STARTER SUBREDDITS BY NICHE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crypto / Finance / Wealth:
  CryptoCurrency, Bitcoin, ethereum, algotrading, CryptoMarkets,
  personalfinance, investing, financialindependence, passive_income, dividends

Fitness / Sport / Health:
  fitness, running, weightlifting, bodyweightfitness, loseit,
  nutrition, xxfitness, gainit

Supplements:
  Supplements, nootropics, bodybuilding, veganfitness

Pets:
  dogs, cats, pets, AskVet, puppy101, DogAdvice, CatAdvice

Baby / Parenting:
  NewParents, beyondthebump, predaddit, Parenting, BabyBumps

Home Decor:
  HomeDecorating, malelivingspace, femalelivingspace,
  InteriorDesign, malelivingspace, cozyplaces

AI / Marketing / Business:
  artificial, Entrepreneur, smallbusiness, marketing,
  digitalnomad, startups, SideProject

E-commerce:
  ecommerce, shopify, dropship, Entrepreneur, Flipping

Travel:
  travel, solotravel, shoestring, backpacking, digitalnomad

Dating / Relationships:
  dating_advice, socialskills (read rules — self-promo limits vary)

Makeup / Beauty:
  MakeupAddiction, SkincareAddiction, BeautyGuruChatter

Insurance / Finance:
  personalfinance, Insurance, financialplanning

Cars:
  cars, whatcarshouldIbuy, AutoMechanics, askcarsales

Music / Education:
  piano, musictheory, WeAreTheMusicMakers, learnmusic
"""

import os, re, json, time, base64, random
from pathlib import Path
from datetime import datetime, timedelta
import requests

BASE_DIR   = Path(__file__).parent.resolve()
STATE_FILE = BASE_DIR / "reddit_state.json"

try:
    import praw
    import prawcore
except ImportError:
    raise SystemExit("praw not installed. Run: pip install praw")


# ─────────────────────────────────────────────────────────────────────────────
# State helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_config():
    cfg_path = BASE_DIR / "network-config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"posted": [], "subreddit_last_posted": {}, "account_posts_today": {}}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def reset_daily_counts(state):
    today = datetime.now().strftime("%Y-%m-%d")
    state.setdefault("account_posts_today", {})
    for acc_id in list(state["account_posts_today"].keys()):
        entry = state["account_posts_today"][acc_id]
        if entry.get("date") != today:
            state["account_posts_today"][acc_id] = {"date": today, "count": 0}


def can_post_to_subreddit(subreddit, state, cooldown_days):
    last = state["subreddit_last_posted"].get(subreddit.lower())
    if not last:
        return True
    return (datetime.now() - datetime.fromisoformat(last)).days >= cooldown_days


def already_posted_url_to_sub(url, subreddit, state):
    return any(
        p["url"] == url and p["subreddit"].lower() == subreddit.lower()
        for p in state["posted"]
    )


def account_posts_today(acc_id, state):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = state.get("account_posts_today", {}).get(acc_id, {})
    if entry.get("date") != today:
        return 0
    return entry.get("count", 0)


def increment_account_posts(acc_id, state):
    today = datetime.now().strftime("%Y-%m-%d")
    state.setdefault("account_posts_today", {})
    state["account_posts_today"][acc_id] = {
        "date": today,
        "count": account_posts_today(acc_id, state) + 1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GitHub helpers
# ─────────────────────────────────────────────────────────────────────────────

def github_get_json(path, token):
    url = f"https://api.github.com/repos/{path}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers, timeout=12)
    if r.status_code == 200:
        return r.json()
    return None


def fetch_backlink_md(repo, slug, token):
    data = github_get_json(f"{repo}/contents/backlinks/{slug}.md", token)
    if not data:
        return None
    try:
        return base64.b64decode(data["content"]).decode("utf-8")
    except Exception:
        return None


def fetch_articles(repo, token):
    data = github_get_json(f"{repo}/contents/articles.json", token)
    if not data:
        return []
    try:
        return json.loads(base64.b64decode(data["content"]).decode("utf-8"))
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Markdown parsers
# ─────────────────────────────────────────────────────────────────────────────

def parse_article_url(md):
    m = re.search(r'\*\*URL:\*\*\s*(\S+)', md)
    return m.group(1).strip() if m else None


def parse_reddit_section(md):
    m = re.search(r'## REDDIT\n(.*?)(?:\n---|\Z)', md, re.DOTALL)
    if not m:
        return None
    section = m.group(1).strip()

    subs_m = re.search(r'\*\*Post to:\*\*\s*(.+)', section)
    if not subs_m:
        return None
    subs_raw = subs_m.group(1).strip()
    subreddits = [s.strip().lstrip('r/') for s in re.split(r'[,\s]+', subs_raw) if s.strip().lstrip('r/')]

    title_m = re.search(r'\*\*Title:\*\*\s*(.+)', section)
    title = title_m.group(1).strip() if title_m else ""

    body = section
    body = re.sub(r'\*\*Post to:\*\*.*\n?', '', body)
    body = re.sub(r'\*\*Title:\*\*.*\n?', '', body).strip()

    return {"subreddits": subreddits, "title": title, "body": body}


# ─────────────────────────────────────────────────────────────────────────────
# Reddit account helpers
# ─────────────────────────────────────────────────────────────────────────────

def connect_account(acc_cfg):
    try:
        reddit = praw.Reddit(
            client_id=acc_cfg["client_id"],
            client_secret=acc_cfg["client_secret"],
            username=acc_cfg["username"],
            password=acc_cfg["password"],
            user_agent=acc_cfg.get("user_agent", f"KavalsiaBot/1.0 by u/{acc_cfg['username']}"),
        )
        redditor = reddit.redditor(acc_cfg["username"])
        _ = redditor.id  # force network call to validate credentials

        age_days = (datetime.utcnow() - datetime.utcfromtimestamp(redditor.created_utc)).days
        karma    = redditor.link_karma + redditor.comment_karma

        min_age   = int(acc_cfg.get("min_age_days", 30))
        min_karma = int(acc_cfg.get("min_karma", 100))

        if age_days < min_age:
            print(f"  @{acc_cfg['username']}: {age_days} days old (need {min_age}) — not eligible yet")
            return None
        if karma < min_karma:
            print(f"  @{acc_cfg['username']}: {karma} karma (need {min_karma}) — keep warming")
            return None

        print(f"  @{acc_cfg['username']}: {age_days}d old, {karma} karma — eligible ✓")
        return reddit

    except prawcore.exceptions.OAuthException:
        print(f"  @{acc_cfg['username']}: wrong credentials — check client_id / secret / password")
        return None
    except Exception as e:
        print(f"  @{acc_cfg['username']}: connection failed — {e}")
        return None


def post_to_subreddit(reddit, subreddit, title, body, dry_run=False):
    try:
        if dry_run:
            print(f"    [DRY RUN] r/{subreddit} ← {title[:70]}")
            return f"https://reddit.com/r/{subreddit}/dry_run"
        sub = reddit.subreddit(subreddit)
        submission = sub.submit(title=title, selftext=body, send_replies=False)
        time.sleep(2)  # small pause after posting
        return f"https://reddit.com{submission.permalink}"
    except prawcore.exceptions.Forbidden:
        print(f"    r/{subreddit}: posting not allowed (banned, private, or karma gate)")
        return None
    except Exception as e:
        print(f"    r/{subreddit}: post failed — {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Telegram
# ─────────────────────────────────────────────────────────────────────────────

def notify_telegram(settings, text):
    tg = settings.get("telegram", {})
    if not tg.get("enabled") or not tg.get("bot_token"):
        return
    for chat_id in tg.get("allowed_chat_ids", []):
        try:
            requests.post(
                f"https://api.telegram.org/bot{tg['bot_token']}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML",
                      "disable_web_page_preview": True},
                timeout=10,
            )
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def run(site_filter=None, slug_filter=None):
    cfg          = load_config()
    settings     = cfg.get("settings", {})
    reddit_cfg   = settings.get("reddit", {})

    if not reddit_cfg.get("enabled", False):
        print(
            "\nReddit bot is DISABLED.\n"
            "Complete the 30-day account warming first (see instructions at top of file),\n"
            "then set settings.reddit.enabled = true in network-config.json.\n"
        )
        return

    github_token  = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        raise SystemExit("GITHUB_TOKEN not set")

    dry_run       = reddit_cfg.get("dry_run", True)
    cooldown_days = int(reddit_cfg.get("subreddit_cooldown_days", 7))
    max_per_day   = int(reddit_cfg.get("max_posts_per_day", 2))
    accounts_cfg  = reddit_cfg.get("accounts", [])
    sites         = [s for s in cfg.get("sites", []) if s.get("active", True)]
    state         = load_state()

    reset_daily_counts(state)

    print(f"\n{'='*60}")
    print(f"  Reddit Bot  {'[DRY RUN]' if dry_run else '[LIVE]'}")
    print(f"{'='*60}\n")

    # Connect all eligible accounts
    live_accounts = {}
    for acc in accounts_cfg:
        client = connect_account(acc)
        if client:
            live_accounts[acc["id"]] = (acc, client)

    if not live_accounts:
        print("No eligible accounts — all failed age/karma checks or credentials wrong.")
        return

    results = []

    for site in sites:
        if site_filter and site["id"] not in site_filter:
            continue

        print(f"\n  Site: {site['domain']}")

        # Find assigned account for this site
        assigned = None
        for acc in accounts_cfg:
            if site["id"] in acc.get("site_ids", []) and acc["id"] in live_accounts:
                assigned = live_accounts[acc["id"]]
                break
        if not assigned:
            print(f"    No eligible account assigned to {site['id']}")
            continue

        acc_cfg, reddit = assigned

        if account_posts_today(acc_cfg["id"], state) >= max_per_day:
            print(f"    @{acc_cfg['username']} hit daily limit ({max_per_day}) — skipping")
            continue

        articles = fetch_articles(site["repo"], github_token)
        if not articles:
            print(f"    No articles found")
            continue

        # Newest-first; if specific slug requested, filter to it
        candidates = list(reversed(articles))
        if slug_filter:
            candidates = [a for a in candidates if a.get("slug") == slug_filter]

        posted_this_site = False
        for article in candidates[:10]:
            slug = article.get("slug", "")
            if not slug or posted_this_site:
                continue

            md = fetch_backlink_md(site["repo"], slug, github_token)
            if not md:
                continue

            article_url  = parse_article_url(md)
            reddit_data  = parse_reddit_section(md)

            if not article_url or not reddit_data or not reddit_data["subreddits"]:
                continue

            # Try each suggested subreddit in order
            for subreddit in reddit_data["subreddits"]:
                if account_posts_today(acc_cfg["id"], state) >= max_per_day:
                    break
                if already_posted_url_to_sub(article_url, subreddit, state):
                    print(f"    r/{subreddit}: already posted — skipping")
                    continue
                if not can_post_to_subreddit(subreddit, state, cooldown_days):
                    print(f"    r/{subreddit}: on {cooldown_days}d cooldown — skipping")
                    continue

                post_url = post_to_subreddit(
                    reddit, subreddit,
                    reddit_data["title"], reddit_data["body"],
                    dry_run=dry_run,
                )

                if post_url:
                    if not dry_run:
                        state["posted"].append({
                            "url":        article_url,
                            "subreddit":  subreddit,
                            "reddit_url": post_url,
                            "site_id":    site["id"],
                            "slug":       slug,
                            "account":    acc_cfg["username"],
                            "posted_at":  datetime.now().isoformat(),
                        })
                        state["subreddit_last_posted"][subreddit.lower()] = datetime.now().isoformat()
                        increment_account_posts(acc_cfg["id"], state)
                        save_state(state)

                    results.append({
                        "domain":    site["domain"],
                        "title":     article["title"],
                        "subreddit": subreddit,
                        "url":       post_url,
                    })
                    print(f"    ✓ Posted to r/{subreddit}")
                    posted_this_site = True
                    break  # one subreddit per article per run

    # Summary
    print(f"\n{'='*60}")
    if results:
        print(f"  {'Simulated' if dry_run else 'Posted'}: {len(results)} post(s)\n")
        for r in results:
            print(f"  r/{r['subreddit']} ← {r['domain']}")
            print(f"    {r['title'][:70]}")
            print(f"    {r['url']}\n")

        if not dry_run:
            text = (
                f"🔴 <b>Reddit — {len(results)} post(s) live</b>\n\n" +
                "\n\n".join(
                    f"r/{r['subreddit']} ← {r['domain']}\n"
                    f"<i>{r['title'][:60]}</i>\n"
                    f"{r['url']}"
                    for r in results
                )
            )
            notify_telegram(settings, text)
    else:
        print("  Nothing posted — no new articles with unposted backlink content, or all subreddits on cooldown.")


if __name__ == "__main__":
    import sys
    site_f = sys.argv[1] if len(sys.argv) > 1 else None
    slug_f = sys.argv[2] if len(sys.argv) > 2 else None
    run(site_filter=[site_f] if site_f else None, slug_filter=slug_f)
