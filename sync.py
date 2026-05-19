#!/usr/bin/env python3
"""
sync.py  -  Kavalsia Network propagation command.

The homepage of every site (templates/<stem>-index.html) is the single source of
truth for that site's header, footer, fonts and colors. Whenever you edit a
homepage, run this once to push the change everywhere:

    python3 sync.py TOKEN                 # all sites: static pages + articles
    python3 sync.py TOKEN --only cryptopulse,carverge
    python3 sync.py TOKEN --static-only   # skip article re-wrap
    python3 sync.py TOKEN --articles-only # skip static pages

It first validates that every homepage has the four SHELL markers (so new sites
are never silently skipped), then runs push-sites.py (static pages) and
rebuild-articles.py (live articles).
"""

import sys, os, glob, argparse, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import layout_shell

BASE = Path(__file__).parent


def validate_all(only):
    stems = [os.path.basename(f)[:-len("-index.html")]
             for f in glob.glob(str(BASE / "templates" / "*-index.html"))]
    bad = []
    for stem in sorted(stems):
        if only and stem not in only:
            continue
        try:
            layout_shell.validate_markers(stem)
        except Exception as e:
            bad.append(str(e))
    return bad


def main():
    p = argparse.ArgumentParser()
    p.add_argument("token", help="GitHub token with repo access to every site repo")
    p.add_argument("--only", default="", help="Comma-separated template stems")
    p.add_argument("--static-only", action="store_true", help="Only push static pages")
    p.add_argument("--articles-only", action="store_true", help="Only re-wrap articles")
    args = p.parse_args()
    only = {x.strip() for x in args.only.split(",") if x.strip()}

    print("Validating homepage shell markers...")
    bad = validate_all(only)
    if bad:
        print("ABORT - homepage template(s) missing shell markers:")
        for b in bad:
            print(f"  - {b}")
        print("Every templates/<stem>-index.html must contain SHELL:HEADER and "
              "SHELL:FOOTER markers. See SYSTEM-GUIDE.md.")
        sys.exit(1)
    print("  all homepages have valid shell markers.\n")

    rc = 0
    if not args.articles_only:
        print("=== Static pages  (push-sites.py) ===")
        cmd = [sys.executable, str(BASE / "push-sites.py"), "--push", args.token]
        if only:
            cmd += ["--sites", ",".join(only)]
        rc |= subprocess.call(cmd)

    if not args.static_only:
        print("\n=== Articles  (rebuild-articles.py) ===")
        cmd = [sys.executable, str(BASE / "rebuild-articles.py"), "--gh-token", args.token]
        if only:
            cmd += ["--only", ",".join(only)]
        rc |= subprocess.call(cmd)

    print("\nSync complete." if rc == 0 else "\nSync finished with errors.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
