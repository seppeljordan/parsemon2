{ buildPythonPackage, attrs, hypothesis, pytest, pytest-benchmark
, pytest-profiling, pytestcov, sphinx, setuptools-rust, cargo, rustc
, pytestCheckHook }:
buildPythonPackage {
  pname = "parsemon2";
  version = "dev";
  nativeBuildInputs = [ sphinx rustc cargo ];
  propagatedBuildInputs = [ attrs cargo rustc ];
  buildInputs = [ setuptools-rust pytestCheckHook ];
  src = ../.;
  postPhases = [ "buildDocsPhase" "installDocsPhase" ];
  buildDocsPhase = ''
    make man 
  '';
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
