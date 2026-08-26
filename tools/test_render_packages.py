"""Tests for the README package-table renderer.

The README is one of three sinks that render the same manifest. This one owns
the Markdown-table house style: CRAN members, the SAS/C code and the book in a
first table, the GitHub-only members in a second, with a family paragraph
between them whose counts are derived rather than typed.
"""
import io
import json
import unittest

from render_packages import (
    MARKER_BEGIN,
    MARKER_END,
    number_word,
    render_block,
    splice,
)

MANIFEST = {
    "generated_from": "hvtiR 9.9.9",
    "counts": {"members": 4, "members_on_cran": 1, "members_github_only": 3},
    "cran_member_names": ["alpha"],
    "packages": [
        {"package": "alpha", "repo": "ehrlinger/alpha", "url": "https://github.com/ehrlinger/alpha",
         "family": "member", "blurb": "First -- on CRAN.", "cran": "alpha", "status": "stable", "role": None},
        {"package": "beta", "repo": "ehrlinger/beta-repo", "url": "https://github.com/ehrlinger/beta-repo",
         "family": "member", "blurb": "Second, GitHub only.", "cran": None, "status": "wip", "role": None},
        {"package": "gamma", "repo": "ehrlinger/gamma", "url": "https://github.com/ehrlinger/gamma",
         "family": "member", "blurb": "Third.", "cran": None, "status": "stable", "role": None},
        {"package": "delta", "repo": "ehrlinger/delta", "url": "https://github.com/ehrlinger/delta",
         "family": "member", "blurb": "Fourth.", "cran": None, "status": "stable", "role": None},
        {"package": "sassy", "repo": "ehrlinger/sassy", "url": "https://github.com/ehrlinger/sassy",
         "family": "standalone", "blurb": "Not an R package.", "cran": None, "status": "stable", "role": "Maintainer"},
        {"package": "The Book", "repo": "ehrlinger/book", "url": "https://example.org/book/",
         "family": "book", "blurb": "A book.", "cran": None, "status": "stable", "role": None},
    ],
}


class TableSplitTests(unittest.TestCase):
    def setUp(self):
        self.block = render_block(MANIFEST)
        self.first, self.second = self._tables()

    def _tables(self):
        tables, cur = [], []
        for line in self.block.splitlines():
            if line.startswith("|"):
                cur.append(line)
            elif cur:
                tables.append(cur); cur = []
        if cur:
            tables.append(cur)
        return tables[0], tables[1]

    def test_first_table_holds_cran_members_standalone_and_book(self):
        names = [r.split("[")[1].split("]")[0] for r in self.first[2:]]
        self.assertEqual(names, ["alpha", "sassy", "The Book"])

    def test_second_table_holds_only_github_only_members(self):
        names = [r.split("[")[1].split("]")[0] for r in self.second[2:]]
        self.assertEqual(names, ["beta", "gamma", "delta"])

    def test_a_cran_member_never_appears_twice(self):
        self.assertEqual(self.block.count("](https://github.com/ehrlinger/alpha)"), 1)


class DecorationTests(unittest.TestCase):
    def setUp(self):
        self.block = render_block(MANIFEST)

    def test_cran_members_link_to_cran(self):
        self.assertIn("[on CRAN](https://CRAN.R-project.org/package=alpha)", self.block)

    def test_wip_renders_as_in_active_development(self):
        beta = next(l for l in self.block.splitlines() if "/beta-repo)" in l)
        self.assertIn("(in active development)", beta)

    def test_stable_carries_no_development_marker(self):
        gamma = next(l for l in self.block.splitlines() if "/gamma)" in l)
        self.assertNotIn("in active development", gamma)

    def test_role_renders_in_parentheses(self):
        sassy = next(l for l in self.block.splitlines() if "/sassy)" in l)
        self.assertIn("(Maintainer)", sassy)

    def test_book_declares_its_licence(self):
        book = next(l for l in self.block.splitlines() if "example.org/book" in l)
        self.assertIn("(Quarto book, CC BY 4.0)", book)

    def test_book_uses_its_homepage_not_the_repo(self):
        book = next(l for l in self.block.splitlines() if "The Book" in l and l.startswith("|"))
        self.assertIn("https://example.org/book/", book)
        self.assertNotIn("github.com/ehrlinger/book", book)

    def test_ascii_dash_becomes_an_em_dash(self):
        # Asserted on an undecorated row, so this isolates the substitution
        # rather than entangling it with the CRAN clause's punctuation.
        m = json.loads(json.dumps(MANIFEST))
        m["packages"][2]["blurb"] = "Third -- with a dash."
        block = render_block(m)
        self.assertIn("Third — with a dash.", block)
        self.assertNotIn(" -- ", block)

    def test_pipes_in_a_blurb_are_escaped_so_the_table_survives(self):
        m = json.loads(json.dumps(MANIFEST))
        m["packages"][2]["blurb"] = "Uses a | pipe."
        row = next(l for l in render_block(m).splitlines() if "/gamma)" in l)
        self.assertIn(r"\|", row)
        self.assertEqual(row.count("|"), row.count(r"\|") + 3)


class FamilySentenceTests(unittest.TestCase):
    def setUp(self):
        self.block = render_block(MANIFEST)

    def test_counts_are_spelled_out_from_the_manifest(self):
        self.assertIn("four member packages, the three below", self.block)

    def test_cran_members_are_named(self):
        self.assertIn("`alpha`", self.block)

    def test_number_word_covers_the_plausible_family_sizes(self):
        self.assertEqual(number_word(9), "nine")
        self.assertEqual(number_word(11), "eleven")
        self.assertEqual(number_word(20), "twenty")

    def test_number_word_falls_back_to_digits_when_out_of_range(self):
        self.assertEqual(number_word(97), "97")


class SpliceTests(unittest.TestCase):
    DOC = f"# Title\n\nintro\n\n{MARKER_BEGIN}\nOLD\n{MARKER_END}\n\ntail\n"

    def test_only_the_marked_region_is_replaced(self):
        out = splice(self.DOC, "NEW")
        self.assertIn("# Title", out)
        self.assertIn("tail", out)
        self.assertIn("NEW", out)
        self.assertNotIn("OLD", out)

    def test_markers_survive_so_the_next_run_can_splice_again(self):
        out = splice(self.DOC, "NEW")
        self.assertIn(MARKER_BEGIN, out)
        self.assertIn(MARKER_END, out)
        self.assertEqual(splice(out, "NEWER").count(MARKER_BEGIN), 1)

    def test_a_missing_begin_marker_is_an_error_naming_it(self):
        with self.assertRaises(ValueError) as ctx:
            splice("no markers here\n", "NEW")
        self.assertIn(MARKER_BEGIN, str(ctx.exception))

    def test_a_missing_end_marker_is_an_error(self):
        with self.assertRaises(ValueError):
            splice(f"{MARKER_BEGIN}\nOLD\n", "NEW")

    def test_markers_out_of_order_is_an_error(self):
        with self.assertRaises(ValueError):
            splice(f"{MARKER_END}\nOLD\n{MARKER_BEGIN}\n", "NEW")


class IdempotenceTests(unittest.TestCase):
    def test_rendering_twice_produces_identical_output(self):
        doc = f"{MARKER_BEGIN}\nOLD\n{MARKER_END}\n"
        once = splice(doc, render_block(MANIFEST))
        twice = splice(once, render_block(MANIFEST))
        self.assertEqual(once, twice)



class PunctuationTests(unittest.TestCase):
    """Blurbs are full sentences; decorations must not read as a second one."""

    def test_the_cran_dash_does_not_follow_a_full_stop(self):
        row = next(l for l in render_block(MANIFEST).splitlines() if "/alpha)" in l)
        self.assertNotIn(". — [on CRAN]", row)
        self.assertIn("First — on CRAN — [on CRAN]", row)

    def test_a_parenthetical_still_follows_a_full_stop(self):
        # "text. (in active development)" is ordinary English; only the em-dash
        # decoration needs the stop removed.
        row = next(l for l in render_block(MANIFEST).splitlines() if "/beta-repo)" in l)
        self.assertIn("GitHub only. (in active development)", row)

    def test_a_blurb_without_a_full_stop_is_left_alone(self):
        m = json.loads(json.dumps(MANIFEST))
        m["packages"][0]["blurb"] = "No stop here"
        row = next(l for l in render_block(m).splitlines() if "/alpha)" in l)
        self.assertIn("No stop here — [on CRAN]", row)


class NetworkFailureTests(unittest.TestCase):
    """A blip in the network is not a defect in this repository.

    Drift must fail the build; an unreachable manifest must not, or every
    unrelated PR becomes hostage to raw.githubusercontent's availability.
    """

    def test_fetch_is_retried_before_giving_up(self):
        import render_packages as rp
        calls = []

        def flaky(url, timeout=0):
            calls.append(url)
            if len(calls) < 3:
                raise OSError("transient")
            return json.dumps(MANIFEST)

        rp.fetch_text = flaky
        try:
            self.assertEqual(rp.load_manifest("https://example.org/m.json")["counts"]["members"], 4)
            self.assertEqual(len(calls), 3)
        finally:
            rp.fetch_text = rp._fetch_text

    def test_exhausted_retries_raise_network_error_not_value_error(self):
        import render_packages as rp

        def always_fails(url, timeout=0):
            raise OSError("down")

        rp.fetch_text = always_fails
        try:
            with self.assertRaises(rp.NetworkError):
                rp.load_manifest("https://example.org/m.json")
        finally:
            rp.fetch_text = rp._fetch_text

    def test_a_malformed_manifest_is_not_treated_as_a_network_problem(self):
        import render_packages as rp
        rp.fetch_text = lambda url, timeout=0: json.dumps({"packages": []})
        try:
            with self.assertRaises(ValueError):
                rp.load_manifest("https://example.org/m.json")
        finally:
            rp.fetch_text = rp._fetch_text


class NoCranMemberTests(unittest.TestCase):
    """The family need not always contain a CRAN member."""

    def _manifest(self):
        m = json.loads(json.dumps(MANIFEST))
        for p in m["packages"]:
            p["cran"] = None
        m["cran_member_names"] = []
        m["counts"] = {"members": 4, "members_on_cran": 0, "members_github_only": 4}
        return m

    def test_the_sentence_does_not_dangle_a_plus_with_nothing_after_it(self):
        block = render_block(self._manifest())
        self.assertNotIn("plus\n above", block)
        self.assertNotIn(" above.", block)

    def test_the_sentence_says_all_members_are_listed_below(self):
        self.assertIn("four member packages, listed below.", render_block(self._manifest()))

    def test_both_tables_remain_since_the_book_and_sas_code_still_exist(self):
        # The first table is not "the CRAN table" -- it also carries the SAS/C
        # code and the book, which exist regardless of any CRAN membership.
        block = render_block(self._manifest())
        self.assertEqual(block.count("| Package | Description |"), 2)
        self.assertIn("/sassy)", block)
        self.assertIn("The Book", block)


class CountDriftTests(unittest.TestCase):
    """Manifest counts must agree with its own package list."""

    def test_a_members_count_that_contradicts_the_packages_is_an_error(self):
        m = json.loads(json.dumps(MANIFEST))
        m["counts"]["members"] = 99
        with self.assertRaises(ValueError) as ctx:
            render_block(m)
        self.assertIn("members", str(ctx.exception))

    def test_a_cran_name_absent_from_the_packages_is_an_error(self):
        m = json.loads(json.dumps(MANIFEST))
        m["cran_member_names"] = ["nonexistent"]
        with self.assertRaises(ValueError) as ctx:
            render_block(m)
        self.assertIn("nonexistent", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
