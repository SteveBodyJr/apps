"""
Publish a new app version on Digital Beaver Apps.

    py tools/publish.py until 1.3.0 "C:/Users/user/Downloads/My APKs/Until/Until-v1.3.0.apk" ^
        --note "First thing that's new." --note "Second thing."

What it does:
  1. Uploads the APK as a GitHub Release in this repo (tag "<app>-v<version>"), so anyone can download it.
  2. Adds the version at the top of the app's list in releases.json (replacing a note-only entry
     for the same version, if there is one).
  3. Commits releases.json and pushes, so the page shows it a minute later.

Add --no-push to stop after step 2 (to look first), and --date YYYY-MM-DD to set the date.
A new app needs an entry in releases.json first (id, name, icon, tagline...).
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "releases.json")


def gh() -> str:
    found = shutil.which("gh")
    if found:
        return found
    default = r"C:\Program Files\GitHub CLI\gh.exe"
    if os.path.exists(default):
        return default
    sys.exit("GitHub CLI (gh) not found. Install it and run: gh auth login")


def run(args, **kw):
    print("> " + " ".join(f'"{a}"' if " " in a else a for a in args))
    subprocess.run(args, check=True, cwd=ROOT, **kw)


def main():
    p = argparse.ArgumentParser(description="Publish an app version.")
    p.add_argument("app", help="app id in releases.json, e.g. until")
    p.add_argument("version", help="e.g. 1.3.0")
    p.add_argument("apk", help="path to the APK file")
    p.add_argument("--note", action="append", default=[], help="one line of 'what's new' (repeat for more)")
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--important", help="a notice people must read before updating (shown on the page and in the app)")
    p.add_argument("--no-push", action="store_true")
    a = p.parse_args()

    if not os.path.isfile(a.apk):
        sys.exit(f"No such file: {a.apk}")
    if not a.note:
        sys.exit("Add at least one --note so people know what's new.")

    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    app = next((x for x in data["apps"] if x["id"] == a.app), None)
    if app is None:
        sys.exit(f"Unknown app '{a.app}'. Known: {', '.join(x['id'] for x in data['apps'])}")

    tag = f"{a.app}-v{a.version}"
    name = os.path.basename(a.apk)
    if any(r.get("tag") == tag for r in app["releases"]):
        sys.exit(f"{tag} is already published.")

    notes_md = "\n".join(f"- {n}" for n in a.note)
    if a.important:
        notes_md = f"**Before you update:** {a.important}\n\n" + notes_md
    run([gh(), "release", "create", tag, a.apk, "--repo", data["repo"],
         "--title", f"{app['name']} {a.version}", "--notes", notes_md])

    release = {
        "version": a.version, "date": a.date, "tag": tag, "file": name,
        "size": os.path.getsize(a.apk), "notes": a.note,
    }
    if a.important:
        release["important"] = a.important
    app["releases"] = [release] + [r for r in app["releases"] if r["version"] != a.version]
    with open(DATA, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"releases.json: {app['name']} {a.version} added.")

    if not a.no_push:
        run(["git", "add", "releases.json"])
        run(["git", "commit", "-m", f"Release {app['name']} {a.version}"])
        run(["git", "push"])
        print("Pushed. GitHub Pages updates in about a minute.")


if __name__ == "__main__":
    main()
