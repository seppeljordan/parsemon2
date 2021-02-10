#!/bin/bash
set -e -x

source $HOME/.cargo/env
export PATH="$HOME/rust/bin:$PATH"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/rust/lib"

# Compile wheels
for PYBIN in /opt/python/cp{36,37,38,39}*/bin; do
    rm -f /io/build/lib.*
    "${PYBIN}/pip" install -U  setuptools setuptools-rust wheel
    "${PYBIN}/pip" wheel /io/ -w /io/dist/
done

# Bundle external shared libraries into the wheels
for whl in /io/dist/parsemon2*.whl; do
    auditwheel show "$whl"
    auditwheel repair "$whl" -w /io/dist/ --plat manylinux_2_24_x86_64
done
