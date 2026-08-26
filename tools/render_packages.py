"""Render the Open-Source Software tables in README.md from hvtiR's manifest.

This README is one of three sinks that render the same manifest; the other two
are the CV Quarto source and the personal site. Each owns its own house style,
so this module turns the shared blurb plus the status/cran/role fields into
Markdown table rows, and derives the family sentence's counts rather than
restating them.

Standard library only -- no pip install step on the runner.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

MANIFEST_URL = "https://ehrlinger.github.io/hvtiR/members.json"
MARKER_BEGIN = "<!-- BEGIN:packages -->"
MARKER_END = "<!-- END:packages -->"
INSTALLER_URL = "https://github.com/ehrlinger/hvtiR"

_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
)


def number_word(n: int) -> str:
    """Spell out a small count; fall back to digits outside the family's range."""
    return _WORDS[n] if 0 <= n < len(_WORDS) else str(n)


def _join(names: list[str]) -> str:
    """Join backticked names as prose: 'a', 'a and b', 'a, b and c'."""
    ticked = [f"`{n}`" for n in names]
    if len(ticked) <= 1:
        return "".join(ticked)
    return f"{', '.join(ticked[:-1])} and {ticked[-1]}"


def _row(pkg: dict) -> str:
    """One Markdown table row. Pipes are escaped so a blurb cannot break the table."""
    text = pkg["blurb"].replace(" -- ", " — ").replace("|", r"\|")

    if pkg["cran"]:
        # The blurb is a full sentence; an em-dash clause must not follow its
        # full stop, so drop the stop rather than reading as a second sentence.
        text = text.rstrip().removesuffix(".")
        text += f" — [on CRAN](https://CRAN.R-project.org/package={pkg['cran']})"
    if pkg["family"] == "book":
        text += " (Quarto book, CC BY 4.0)"
    if pkg["status"] == "wip":
        text += " (in active development)"
    if pkg["role"]:
        text += f" ({pkg['role']})"

    return f"| [{pkg['package']}]({pkg['url']}) | {text} |"


def _table(packages: list[dict]) -> str:
    header = "| Package | Description |\n|---|---|"
    return "\n".join([header, *(_row(p) for p in packages)])


def render_block(manifest: dict) -> str:
    """Build the generated region: two tables around the family paragraph."""
    pkgs = manifest["packages"]
    counts = manifest["counts"]

    cran_members = [p for p in pkgs if p["family"] == "member" and p["cran"]]
    github_only = [p for p in pkgs if p["family"] == "member" and not p["cran"]]
    standalone = [p for p in pkgs if p["family"] == "standalone"]
    book = [p for p in pkgs if p["family"] == "book"]

    # The counts below are derived, never authored: this sentence used to be
    # maintained by hand in three repositories and drifted from the lists.
    sentence = (
        f"[`hvtiR`]({INSTALLER_URL}) — a one-command installer, version status\n"
        "table, and environment diagnostic — resolves the family from public GitHub repositories\n"
        f"and version-checks it as a unit: {number_word(counts['members'])} member packages, "
        f"the {number_word(counts['members_github_only'])} below plus\n"
        f"{_join(manifest['cran_member_names'])} above."
    )

    return "\n".join([
        _table(cran_members + standalone + book),
        "",
        "### The HVTI R package family",
        "",
        sentence,
        "",
        _table(github_only),
    ])


def splice(document: str, block: str) -> str:
    """Replace the marked region, leaving everything outside it untouched."""
    start = document.find(MARKER_BEGIN)
    if start < 0:
        raise ValueError(f"{MARKER_BEGIN} not found; cannot splice")
    end = document.find(MARKER_END, start)
    if end < 0:
        raise ValueError(f"{MARKER_END} not found after {MARKER_BEGIN}; cannot splice")

    head = document[: start + len(MARKER_BEGIN)]
    tail = document[end:]
    return f"{head}\n{block}\n{tail}"


class NetworkError(RuntimeError):
    """The manifest could not be fetched. Distinct from a malformed manifest.

    Drift is a defect in this repository; an unreachable host is not. Keeping
    the two apart lets --check fail on the former and tolerate the latter.
    """


def _fetch_text(url: str, timeout: int = 30) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        if resp.status != 200:
            raise OSError(f"{url} returned HTTP {resp.status}")
        return resp.read().decode()


# Indirection so tests can substitute a transport without touching the network.
fetch_text = _fetch_text


def load_manifest(source: str, attempts: int = 3) -> dict:
    if source.startswith(("http://", "https://")):
        last = None
        for attempt in range(1, attempts + 1):
            try:
                body = fetch_text(source, timeout=30)
                break
            except Exception as exc:  # transport-level only
                last = exc
                if attempt < attempts:
                    time.sleep(2 ** (attempt - 1))
        else:
            raise NetworkError(f"could not fetch {source} after {attempts} attempts: {last}")
        manifest = json.loads(body)
    else:
        manifest = json.loads(Path(source).read_text())

    for key in ("packages", "counts", "cran_member_names"):
        if key not in manifest:
            raise ValueError(f"manifest is missing required key: {key}")
    if not manifest["packages"]:
        raise ValueError("manifest lists no packages; refusing to publish an empty table")
    return manifest


def main(argv=None) -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=MANIFEST_URL, help="URL or local path")
    parser.add_argument("--target", type=Path, default=root / "README.md")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the target is out of date; write nothing")
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
    except NetworkError as exc:
        # Never fail an unrelated PR because a host was briefly unreachable.
        # Writing from no data would be worse still, so that path exits 1.
        if args.check:
            print(f"skipping check: {exc}", file=sys.stderr)
            return 0
        print(f"error: {exc}", file=sys.stderr)
        return 1

    current = args.target.read_text()
    rendered = splice(current, render_block(manifest))

    if args.check:
        if rendered != current:
            print(f"{args.target} is out of date with {args.manifest}", file=sys.stderr)
            return 1
        print(f"{args.target} is up to date")
        return 0

    if rendered == current:
        print(f"{args.target} already up to date")
        return 0
    args.target.write_text(rendered)
    print(f"updated {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
