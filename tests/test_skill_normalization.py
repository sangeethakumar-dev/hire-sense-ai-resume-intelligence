from backend.agents.candidate_matcher import (
    normalize_skill,
    keyword_match
)


def test_skill_aliases():
    assert normalize_skill("HTML") == "html5"
    assert normalize_skill("HTML5") == "html5"
    assert normalize_skill("CSS") == "css3"
    assert normalize_skill("CSS3") == "css3"


def test_java_and_javascript():
    assert keyword_match("Java", "JavaScript") == 0.0


def test_cpp_and_c():
    assert keyword_match("C++", "C") == 0.0


def test_html_css_matching():
    assert keyword_match("HTML5", "HTML") == 1.0
    assert keyword_match("CSS3", "CSS") == 1.0


if __name__ == "__main__":
    test_skill_aliases()
    test_java_and_javascript()
    test_cpp_and_c()
    test_html_css_matching()

    print("All skill normalization tests passed!")