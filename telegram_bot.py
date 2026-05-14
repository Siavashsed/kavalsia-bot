# © 2026 Kavalsia Inc. [Siavash Sadighi]
"""
Kavalsia Network — Telegram Bot
---------------------------------
Combines on-demand post commands with a weekly editorial ideas workflow.

SETUP
  1. Create a bot via @BotFather → copy the token
  2. Message @userinfobot to get your chat ID
  3. In network-config.json → settings.telegram:
       "enabled": true,
       "bot_token": "YOUR:TOKEN",
       "allowed_chat_ids": [123456789]
  4. Run: python telegram_bot.py

ON-DEMAND COMMANDS
  /post all                 — post one article to every active site
  /post domain.com          — post to one site (auto-pick topic)
  /post domain.com topic    — post a specific topic to one site
  /status                   — last-post summary for all sites
  /pause domain.com         — mark site inactive
  /resume domain.com        — mark site active
  /help                     — show commands

WEEKLY IDEAS WORKFLOW (runs on Monday or via GitHub Actions)
  /ideas                    — generate 20 ideas per site right now
  Reply with numbers        — "1 4 7 12" → publishes those articles
  Reply "auto"              — bot picks and publishes the 7 best
"""

import os, json, time, re, threading
from pathlib import Path
from datetime import datetime
import requests
import anthropic

BASE_DIR   = Path(__file__).parent.resolve()
STATE_FILE = BASE_DIR / "telegram_state.json"


# ── Config ────────────────────────────────────────────────────────────────────

def load_config():
    cfg_path = BASE_DIR / "network-config.json"
    if cfg_path.exists():
        return json.loads(cfg_path.read_text(encoding="utf-8"))
    return {}


def save_config(cfg):
    cfg_path = BASE_DIR / "network-config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_update_id": 0, "pending_ideas": None, "last_ideas_date": None}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Telegram API helpers ──────────────────────────────────────────────────────

def _tg(token, method, **kwargs):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/{method}",
            json=kwargs, timeout=15
        )
        return r.json()
    except Exception as e:
        print(f"Telegram API error ({method}): {e}")
        return {}


def send(token, chat_id, text, parse_mode="HTML"):
    _tg(token, "sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode)


def get_updates(token, offset=0):
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"offset": offset, "timeout": 30, "allowed_updates": ["message"]},
            timeout=35,
        )
        return r.json().get("result", [])
    except Exception as e:
        print(f"Poll error: {e}")
        return []


# ── Site helpers ──────────────────────────────────────────────────────────────

def find_site(sites, target):
    target = target.lower().strip()
    for s in sites:
        if target == s.get("id", "").lower() or target in s.get("domain", "").lower():
            return s
    return None


# ── Weekly ideas workflow ─────────────────────────────────────────────────────

def generate_ideas(site, claude_client, n=20):
    from bot import _retry
    response = _retry(lambda: claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"""Generate {n} original blog article title ideas for this website:

Site: {site["domain"]}
Category: {site["category"]}
Voice: {site["tone"]}
Persona: {site["persona"]}

Requirements:
- SEO-friendly titles (clear keyword in each)
- Genuine value, not clickbait
- Mix of: how-to, analysis, comparison, opinion, explainer
- Each title distinct from the others
- No AI clichés in the titles

Return a JSON array only, no other text:
["Title 1", "Title 2", ..., "Title {n}"]"""}]
    ))
    text = response.content[0].text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def pick_best_seven(ideas):
    picks = list(range(0, min(20, len(ideas)), 3))[:7]
    while len(picks) < 7 and len(picks) < len(ideas):
        for i in range(len(ideas)):
            if i not in picks:
                picks.append(i)
                break
    return sorted(picks[:7])


def run_weekly_ideas(token, chat_id):
    from bot import load_network_config
    sites, _, _, _, _, _, _ = load_network_config()
    active_sites = [s for s in sites if s.get("active", True)]

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        send(token, chat_id, "❌ ANTHROPIC_API_KEY not set on this machine.")
        return

    claude_client = anthropic.Anthropic(api_key=anthropic_key)
    all_ideas = {}

    send(token, chat_id, f"⏳ Generating 20 ideas for {len(active_sites)} sites… (takes ~60 seconds)")

    for site in active_sites:
        try:
            ideas = generate_ideas(site, claude_client, n=20)
            all_ideas[site["id"]] = ideas
            print(f"  Ideas: {site['domain']}: {len(ideas)}")
        except Exception as e:
            print(f"  Ideas error for {site['domain']}: {e}")
            all_ideas[site["id"]] = []

    lines = ["📋 <b>Weekly Blog Ideas</b>\n"]
    lines.append("Reply with numbers you want published (e.g. <code>1 4 7 12</code>) or reply <code>auto</code> to publish the 7 best.\n")

    for site in active_sites:
        ideas = all_ideas.get(site["id"], [])
        if not ideas:
            continue
        lines.append(f"\n<b>🌐 {site['domain']}</b>")
        for i, idea in enumerate(ideas[:20], 1):
            lines.append(f"  {i}. {idea}")

    message = "\n".join(lines)
    if len(message) > 4000:
        for chunk in [message[i:i+3900] for i in range(0, len(message), 3900)]:
            send(token, chat_id, chunk)
            time.sleep(1)
    else:
        send(token, chat_id, message)

    state = load_state()
    state["pending_ideas"]   = all_ideas
    state["last_ideas_date"] = datetime.now().isoformat()
    save_state(state)


def publish_selected(all_ideas, selections, token, chat_id):
    from bot import load_network_config, generate_article, fetch_image, build_article_page, build_homepage, load_article_index, github_push, send_newsletter, get_author_name, THEMES, _retry, push_comments, push_backlink_content

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    pexels_key    = os.environ.get("PEXELS_API_KEY", "")
    github_token  = os.environ.get("GITHUB_TOKEN")
    brevo_key     = os.environ.get("BREVO_API_KEY", "")

    if not anthropic_key or not github_token:
        send(token, chat_id, "❌ Missing ANTHROPIC_API_KEY or GITHUB_TOKEN on server.")
        return

    sites, global_prompt, settings, global_client, global_negative_prompt, global_header_scripts, global_footer_scripts = load_network_config()
    active_sites = [s for s in sites if s.get("active", True)]
    claude_client = anthropic.Anthropic(api_key=anthropic_key)
    date_str = datetime.now().strftime("%Y-%m-%d")
    published = []

    for site in active_sites:
        site_ideas  = all_ideas.get(site["id"], [])
        chosen_idxs = selections.get(site["id"], [])
        if not site_ideas or not chosen_idxs:
            continue

        for idx in chosen_idxs:
            if idx >= len(site_ideas):
                continue
            topic = site_ideas[idx]
            try:
                print(f"  Publishing '{topic}' on {site['domain']}")
                author_name = get_author_name(site)
                article = generate_article(topic, site, active_sites, claude_client, global_prompt, author_name, global_negative_prompt=global_negative_prompt)
                article["date"]     = datetime.now().strftime("%B %d, %Y")
                article["date_iso"] = date_str
                article["author"]   = article.get("author") or author_name

                image_url, photographer = fetch_image(article.get("image_query", "finance"), pexels_key)
                article["image"] = image_url or ""

                article_html = build_article_page(article, site, image_url, photographer, THEMES, global_header_scripts, global_footer_scripts)
                slug = article["slug"]

                _retry(lambda: github_push(site["repo"], f"{slug}/index.html", article_html,
                            f"Post: {article['title']} [{date_str}]", github_token))

                articles = load_article_index(site["repo"], github_token)
                articles.append({
                    "title": article["title"], "slug": slug,
                    "meta_description": article["meta_description"],
                    "date": article["date"], "date_iso": article["date_iso"],
                    "author": article["author"], "image": article["image"],
                    "outbound_links": article.get("outbound_links", []),
                })

                homepage_html = build_homepage(site, articles, THEMES, global_header_scripts, global_footer_scripts)
                _retry(lambda: github_push(site["repo"], "index.html", homepage_html, f"Index [{date_str}]", github_token))
                _retry(lambda: github_push(site["repo"], "articles.json", json.dumps(articles, indent=2), f"Index data [{date_str}]", github_token))
                send_newsletter(site, article, brevo_key)
                push_backlink_content(article, site, claude_client, github_token, settings)
                push_comments(article, site, claude_client, github_token)
                published.append(f"✅ {site['domain']}: {article['title']}")
                time.sleep(3)
            except Exception as e:
                published.append(f"❌ {site['domain']} — {topic[:50]}: {e}")

    summary = "\n".join(published) if published else "Nothing published."
    send(token, chat_id, f"<b>Publishing complete:</b>\n\n{summary}")


def process_reply(text, state, token, chat_id):
    all_ideas = state.get("pending_ideas")
    if not all_ideas:
        send(token, chat_id, "No pending ideas. Send /ideas to generate some first.")
        return

    text = text.strip().lower()
    if text == "auto":
        send(token, chat_id, "🤖 Auto mode — picking 7 best per site and publishing...")
        selections = {site_id: pick_best_seven(ideas) for site_id, ideas in all_ideas.items()}
    else:
        nums = [int(n) - 1 for n in re.findall(r'\d+', text) if 1 <= int(n) <= 20]
        if not nums:
            send(token, chat_id, "Couldn't parse those numbers. Try: <code>1 3 5 7</code> or <code>auto</code>")
            return
        nums = sorted(set(nums[:7]))
        selections = {site_id: nums for site_id in all_ideas}
        send(token, chat_id, f"✅ Publishing positions {[n+1 for n in nums]} across all sites...")

    publish_selected(all_ideas, selections, token, chat_id)
    state["pending_ideas"] = None
    save_state(state)


# ── Command handlers ──────────────────────────────────────────────────────────

def handle(text, cfg, chat_id, token, state):
    parts = text.strip().split(None, 2)
    cmd   = parts[0].lower().split("@")[0]
    arg1  = parts[1].lower() if len(parts) > 1 else ""
    arg2  = parts[2] if len(parts) > 2 else ""

    sites        = cfg.get("sites", [])
    active_sites = [s for s in sites if s.get("active", True)]

    # ── /help ─────────────────────────────────────────────────────────────────
    if cmd == "/help":
        send(token, chat_id,
            "<b>Kavalsia Network Commands</b>\n\n"
            "<b>On-demand posting</b>\n"
            "  /post all — post to all active sites\n"
            "  /post domain.com — post to one site\n"
            "  /post domain.com custom topic — specific topic\n\n"
            "<b>Site management</b>\n"
            "  /status — last post dates for all sites\n"
            "  /pause domain.com — pause a site\n"
            "  /resume domain.com — resume a site\n\n"
            "<b>Weekly ideas workflow</b>\n"
            "  /ideas — generate 20 ideas per site now\n"
            "  Reply 1 4 7 — publish those ideas\n"
            "  Reply auto — let the bot pick and publish the 7 best\n\n"
            "<b>Backlink tracking</b>\n"
            "  /backlink &lt;source_url&gt; &lt;target_url&gt; &lt;platform&gt;\n"
            "  e.g. /backlink https://reddit.com/... https://mysite.com/article/ reddit\n\n"
            "  /help — show this message"
        )

    # ── /status ───────────────────────────────────────────────────────────────
    elif cmd == "/status":
        lines = ["<b>Site Status</b>\n"]
        for s in sites:
            icon   = "✅" if s.get("active", True) else "⏸"
            domain = s.get("domain", s.get("id", "?"))
            warm   = s.get("warming", {})
            warm_label = f" (warming: {warm.get('phase','?')})" if warm.get("enabled") else ""
            lines.append(f"{icon} {domain}{warm_label}")
        pending = state.get("pending_ideas")
        if pending:
            lines.append(f"\n💡 Ideas pending from {state.get('last_ideas_date', 'unknown')}")
        send(token, chat_id, "\n".join(lines))

    # ── /pause ────────────────────────────────────────────────────────────────
    elif cmd == "/pause":
        if not arg1:
            send(token, chat_id, "Usage: /pause domain.com")
            return
        site = find_site(sites, arg1)
        if not site:
            send(token, chat_id, f"Site not found: {arg1}")
            return
        site["active"] = False
        save_config(cfg)
        send(token, chat_id, f"⏸ Paused {site['domain']}")

    # ── /resume ───────────────────────────────────────────────────────────────
    elif cmd == "/resume":
        if not arg1:
            send(token, chat_id, "Usage: /resume domain.com")
            return
        site = find_site(sites, arg1)
        if not site:
            send(token, chat_id, f"Site not found: {arg1}")
            return
        site["active"] = True
        save_config(cfg)
        send(token, chat_id, f"✅ Resumed {site['domain']}")

    # ── /ideas ────────────────────────────────────────────────────────────────
    elif cmd == "/ideas":
        threading.Thread(
            target=run_weekly_ideas, args=(token, chat_id), daemon=True
        ).start()

    # ── /post ─────────────────────────────────────────────────────────────────
    elif cmd == "/post":
        if not arg1:
            send(token, chat_id, "Usage: /post all  OR  /post domain.com [custom topic]")
            return

        if arg1 == "all":
            site_filter     = None
            label           = "all active sites"
            topic_overrides = {s["id"]: arg2 for s in active_sites} if arg2 else {}
        else:
            matched = find_site(active_sites, arg1)
            if not matched:
                domains = ", ".join(s["domain"] for s in active_sites)
                send(token, chat_id, f"Site not found: {arg1}\nActive: {domains}")
                return
            site_filter     = [matched["id"]]
            label           = matched["domain"]
            topic_overrides = {matched["id"]: arg2} if arg2 else {}

        topic_note = f" → <i>{arg2}</i>" if arg2 else ""
        send(token, chat_id, f"🚀 Starting post run for <b>{label}</b>{topic_note}…")

        def run_job():
            try:
                import bot as content_bot
                content_bot.run(
                    topic_overrides=topic_overrides or None,
                    site_filter=site_filter,
                )
                send(token, chat_id, f"✅ Finished posting to <b>{label}</b>")
            except Exception as e:
                send(token, chat_id, f"❌ Error: <code>{str(e)[:300]}</code>")

        threading.Thread(target=run_job, daemon=True).start()

    # ── /backlink ─────────────────────────────────────────────────────────────
    elif cmd == "/backlink":
        raw = text.strip().split(None, 3)
        if len(raw) < 3:
            send(token, chat_id,
                "Usage: /backlink &lt;source_url&gt; &lt;target_url&gt; &lt;platform&gt;\n"
                "Platforms: reddit, linkedin, quora, medium, guest-post, forum, other\n\n"
                "Example:\n<code>/backlink https://reddit.com/r/... https://mysite.com/article/ reddit</code>")
            return
        source   = raw[1]
        target   = raw[2]
        platform = raw[3].strip().lower() if len(raw) > 3 else "other"
        entry = {
            "source":   source,
            "target":   target,
            "platform": platform,
            "notes":    "via Telegram",
        }
        try:
            r = requests.post(
                "http://localhost:8765/api/backlinks",
                json=entry,
                timeout=5,
            )
            if r.status_code == 200:
                send(token, chat_id, f"✅ Backlink recorded!\n🔗 {source}\n→ {target}\nPlatform: {platform}")
            else:
                raise Exception(f"Server returned {r.status_code}")
        except Exception as e:
            send(token, chat_id, f"⚠️ Could not reach local server ({e}). Make sure server.py is running.\nBacklink was NOT saved.")

    # ── ideas number selection (e.g. "1 4 7 12" or "auto") ───────────────────
    elif re.search(r'\d', text) or text.lower().strip() == "auto":
        process_reply(text, state, token, chat_id)

    else:
        send(token, chat_id, f"Unknown command: {cmd}\nType /help for available commands.")


# ── Main polling loop ─────────────────────────────────────────────────────────

def main():
    cfg    = load_config()
    tg_cfg = cfg.get("settings", {}).get("telegram", {})

    if not tg_cfg.get("enabled"):
        print(
            "Telegram bot is disabled.\n"
            "Enable in network-config.json under settings.telegram:\n"
            '  "enabled": true\n'
            '  "bot_token": "YOUR:TOKEN"\n'
            '  "allowed_chat_ids": [YOUR_CHAT_ID]\n'
            "\nFind your chat ID by messaging @userinfobot on Telegram."
        )
        return

    token = tg_cfg.get("bot_token", "").strip()
    if not token:
        print("No bot_token in settings.telegram")
        return

    allowed_chats = set(str(c) for c in tg_cfg.get("allowed_chat_ids", []))

    print("\n  Kavalsia Network — Telegram Bot")
    print("  ─────────────────────────────────")
    if allowed_chats:
        print(f"  Allowed chat IDs: {', '.join(allowed_chats)}")
    else:
        print("  WARNING: No allowed_chat_ids — any Telegram user can control this bot!")
    print("  Listening for commands... (Ctrl+C to stop)\n")

    state  = load_state()
    offset = state.get("last_update_id", 0) + 1

    while True:
        updates = get_updates(token, offset)
        for update in updates:
            offset = update["update_id"] + 1
            state["last_update_id"] = update["update_id"]
            save_state(state)

            msg     = update.get("message") or update.get("edited_message")
            if not msg:
                continue

            text    = msg.get("text", "").strip()
            chat_id = str(msg.get("chat", {}).get("id", ""))

            if not text or not chat_id:
                continue

            if allowed_chats and chat_id not in allowed_chats:
                send(token, chat_id, "⛔ Unauthorized. Add your chat ID to settings.telegram.allowed_chat_ids.")
                continue

            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {chat_id}: {text}")

            cfg   = load_config()   # reload on every command so config edits are live
            state = load_state()    # reload state too
            handle(text, cfg, chat_id, token, state)

        if not updates:
            time.sleep(1)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "ideas":
        # GitHub Actions: python telegram_bot.py ideas
        cfg    = load_config()
        tg_cfg = cfg.get("settings", {}).get("telegram", {})
        token  = tg_cfg.get("bot_token", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
        chat_id = str(tg_cfg.get("allowed_chat_ids", [os.environ.get("TELEGRAM_CHAT_ID", "")])[0])
        if token and chat_id:
            run_weekly_ideas(token, chat_id)
        else:
            print("Set bot_token and allowed_chat_ids in network-config.json")
    else:
        main()
