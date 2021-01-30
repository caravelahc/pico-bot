from picobot.painter import wrapped_text


def test_wrapped_text():
    samples_and_expected = [
        ('short message', 'short message'),
        ('msg that should have two lines', 'msg that should have two\nlines'),
        (
            'msg with over 50 characters that should have three lines',
            'msg with over 50\ncharacters that should\nhave three lines',
        ),
        ('ABigWordThatDoesntFitInJustOneLine', 'ABigWordThatDoesntFitInJu\nstOneLine'),
        (
            'msg with four lines that also have ABigWordThatDoesntFitInJustOneLine in the 2nd line',
            'msg with four lines that\nalso have ABigWordThatDoe\nsntFitInJustOneLine in\nthe 2nd line',
        ),
    ]
    for sample, expected in samples_and_expected:
        result = wrapped_text(sample)
        assert result == expected
