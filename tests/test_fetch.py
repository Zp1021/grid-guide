from ragbot.chunking import read_article
from ragbot.fetch import article_url, clean_text, save_article, slug

def test_slug_makes_a_safe_file_name():
    assert slug("Regional transmission organization (North America)") == "regional-transmission-organization-north-america"

def test_article_url_uses_underscores():
    assert article_url("Base load") == "https://en.wikipedia.org/wiki/Base_load"

def test_clean_text_cuts_off_link_sections():
    text = "Useful facts here.\n\n== History ==\nMore facts.\n\n== See also ==\nA list of links.\n\n== References ==\nMore links."
    cleaned = clean_text(text)
    assert "More facts." in cleaned
    assert "See also" not in cleaned
    assert "References" not in cleaned

def test_saved_article_can_be_read_back(tmp_path):
    path = save_article("Base load", "Base load is the minimum demand.", tmp_path)
    title, url, text = read_article(path)
    assert title == "Base load"
    assert url == "https://en.wikipedia.org/wiki/Base_load"
    assert text == "Base load is the minimum demand."