from setuptools import setup
from setuptools_rust import RustExtension

cargo_arguments = ["--offline"]

setup(
    rust_extensions=[
        RustExtension(
            "parsemon.extensions",
            "Cargo.toml",
            debug=False,
            args=cargo_arguments,
        )
    ]
)
