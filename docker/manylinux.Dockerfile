FROM quay.io/pypa/manylinux2014_x86_64

RUN mkdir ~/rust-installer
RUN curl \
    --proto '=https' \
    --tlsv1.2 \
    -sSf https://sh.rustup.rs \
    -o ~/rust-installer/rustup.sh
RUN sh ~/rust-installer/rustup.sh -y --default-toolchain stable
