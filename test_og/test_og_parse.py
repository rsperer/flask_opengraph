from flaskog.og_parse import parse_canonical


def test_parse_canonical_href():
    content = bytes('<link rel="canonical" href="https://example.com/wordpress/seo-plugin/" />', 'utf-8')
    result = parse_canonical("stub", content)
    assert result == "https://example.com/wordpress/seo-plugin/"


def test_parse_canonical_og():
    content = bytes('<meta property="og:url" content="https://ogp.me/">', 'utf-8')
    result = parse_canonical("stub", content)
    assert result == "https://ogp.me/"
