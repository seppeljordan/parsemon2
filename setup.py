from setuptools import setup
from setuptools_rust import RustExtension

setup(
    rust_extensions=[
        RustExtension("parsemon.result", "Cargo.toml", debug=False, args=["--offline"])
    ]
)
