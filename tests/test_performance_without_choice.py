import pytest

from parsemon import chain, do, literal, run_parser, unit


@pytest.fixture
def document(request):
    return "0123456789" * 2000


@pytest.fixture(
    params=(
        "do",
        "chain",
    )
)
def implementation(request):
    if request.param == "do":

        def wrapper(document):
            @do
            def parser():
                for letter in document:
                    yield literal(letter)
                return True

            return parser()

    else:

        def wrapper(document):
            parser = unit(True)
            for character in document:
                parser = chain(parser, literal(character))
            return parser

    return wrapper


@pytest.mark.benchmark(group="linear-performance")
def test_performance_without_choice(document, benchmark, implementation):
    parser = implementation(document)
    assert benchmark(run_parser, parser, document)
