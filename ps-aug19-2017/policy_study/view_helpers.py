import validation
from utils import find_key


def remove_duplicate_titles(page, responses):
    """If a page has only one question and the question's title is equal
    to the page title, remove the question's title. From issue #36"""
    ptitle = find_key("title", page)

    for name,item in page:
        if name == "question" and validation.would_be_displayed(item, responses):
            if item.get("title") == ptitle:
                del item["title"]
            break
