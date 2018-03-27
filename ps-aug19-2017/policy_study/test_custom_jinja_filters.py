from custom_jinja_filters import regexreplace, count_dots


def test_regexreplace():
    assert regexreplace("asdf", "sd", "qr") == "aqrf"

def test_count_dots():
    assert count_dots("a.fesd.sdfe.fj") == 3
