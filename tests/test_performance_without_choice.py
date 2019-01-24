import pytest

from parsemon import chain, do, literal, run_parser, unit


@pytest.fixture(
    params=[
        1, 2, 3, 4, 5, 10, 20,
    ]
)
def document(request):
    document_length = request.param
    return '0123456789' * 1000 * document_length


@pytest.fixture(
    params=(
        'do', 'chain',
    )
)
def implementation(request):
    if request.param == 'do':
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


@pytest.mark.benchmark(
    group='linear-performance'
)
def test_performance_without_choice(document, benchmark, implementation):
    parser = implementation(document)
    assert benchmark(run_parser, parser, document)
