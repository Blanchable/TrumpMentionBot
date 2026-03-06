from app.parsing.matcher import run_match
from app.parsing.rule_parser import parse_rule


def test_matcher_counts():
    rule = parse_rule("economy 2+")
    text = "the economy is strong. economy policy and economy plans"
    res = run_match(rule, text)
    assert res.raw_count == 3
    assert res.adjusted_count == 3


def test_short_term_ambiguity():
    rule = parse_rule("usa")
    text = "usa usa"
    res = run_match(rule, text)
    assert res.raw_count == 2
    assert res.adjusted_count == 1
