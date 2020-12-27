{ buildPythonPackage, attrs, hypothesis, pytest, pytest-benchmark
, pytest-profiling, pytestcov, sphinx, setuptools-rust, cargo, rustc
, pytestCheckHook }:
buildPythonPackage {
  pname = "parsemon2";
  version = "dev";
  src = ../.;

  # building
  nativeBuildInputs = [ sphinx rustc cargo ];
  propagatedBuildInputs = [ attrs cargo rustc ];
  buildInputs = [ setuptools-rust pytestCheckHook ];
  preBuildPhases = [ "configureCargoPhase" ];
  preInstallPhases = [ "buildDocsPhase" ];
  configureCargoPhase = ''
    mkdir -p .cargo
    cp $src/nix/cargo/config.toml .cargo/config.toml
  '';
  buildDocsPhase = ''
    make man 
  '';

  # installing
  postPhases = [ "installDocsPhase" ];
  installDocsPhase = ''
    mkdir -p $out/share/man/man3
    cp build/man/parsemon2.3 $out/share/man/man3/parsemon2.3
  '';

  # tests
  pytestFlagsArray = [ "--benchmark-skip" ];
  checkInputs = [
    hypothesis
    pytest
    pytest-benchmark
    pytest-profiling
    pytestcov
    setuptools-rust
  ];
}
