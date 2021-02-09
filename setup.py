from setuptools import setup
from setuptools_rust import RustExtension

cargo_arguments = ["--offline"]

setup(
    rust_extensions=[
        RustExtension(
            "parsemon.result", "Cargo.toml", debug=False, args=cargo_arguments
        ),
        RustExtension(
            "parsemon.internals.parsers",
            "Cargo.toml",
            debug=False,
            args=cargo_arguments,
        ),
    ]
)
