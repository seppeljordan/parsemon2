from hypothesis import strategies as st

from parsemon.stream import IOStream, StringStream


@st.composite
def stream_implementation(draw):
    return draw(st.sampled_from([StringStream, IOStream]))


@st.composite
def stream(draw, min_size=0):
    characters = draw(st.text(min_size=min_size))
    stream_class = draw(stream_implementation())
    return stream_class.from_string(characters)
