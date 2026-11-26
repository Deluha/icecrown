"""The shared checker helpers: Markdown, frontmatter and tables."""

from _toolkit import Violation, heading_slugs, iter_links, split_frontmatter, table_rows


def test_links_outside_code_are_found() -> None:
    text = "See [a](a.md#x) and `[b](b.md)`.\n```\n[c](c.md)\n```\n![img](i.png) [d](https://x.y)\n"
    assert list(iter_links(text)) == [(1, "a.md#x"), (5, "https://x.y")]


def test_heading_slugs_follow_github_rules() -> None:
    text = "# Project Icecrown — operating contract\n## Hard rules\n## Hard rules\n## C1: print()\n"
    assert heading_slugs(text) == {
        "project-icecrown--operating-contract",
        "hard-rules",
        "hard-rules-1",
        "c1-print",
    }


def test_headings_inside_code_fences_are_ignored() -> None:
    assert heading_slugs("```\n# not a heading\n```\n# Real\n") == {"real"}


def test_frontmatter_scalars_and_lists() -> None:
    text = (
        '---\nname: x\nquoted: "y z"\npaths:\n  - "src/**"\n  - tests/**\n'
        "inline: [a, b]\n---\n\nBody\n"
    )
    meta, body = split_frontmatter(text)
    assert meta == {
        "name": "x",
        "quoted": "y z",
        "paths": ["src/**", "tests/**"],
        "inline": ["a", "b"],
    }
    assert [line for line in body if line[1]] == [(10, "Body")]


def test_text_without_frontmatter_is_all_body() -> None:
    meta, body = split_frontmatter("no front\nmatter\n")
    assert meta == {}
    assert body == [(1, "no front"), (2, "matter")]


def test_unterminated_frontmatter_is_all_body() -> None:
    meta, body = split_frontmatter("---\nname: x\n")
    assert meta == {}
    assert len(body) == 2


def test_table_rows_skip_header_and_separator_and_respect_heading() -> None:
    text = (
        "# One\n| h | i |\n|---|---|\n| `a` | b |\n\n"
        "# Two\n| h | i |\n|---|---|\n| c | d |\n| e | f |\n"
    )
    assert table_rows(text) == [(4, ["`a`", "b"]), (9, ["c", "d"]), (10, ["e", "f"])]
    assert table_rows(text, heading="Two") == [(9, ["c", "d"]), (10, ["e", "f"])]


def test_violation_renders_as_path_line_code() -> None:
    assert str(Violation("a.py", 3, "C1", "msg")) == "a.py:3: C1 msg"
