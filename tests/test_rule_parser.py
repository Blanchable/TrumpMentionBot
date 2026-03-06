from app.parsing.rule_parser import parse_rule


def test_parse_threshold():
    rule = parse_rule("China 5+")
    assert rule.canonical_term == "china"
    assert rule.threshold_value == 5
    assert rule.threshold_type == "at_least"


def test_parse_single():
    rule = parse_rule("economy")
    assert rule.threshold_value == 1
    assert "economy" in rule.aliases
