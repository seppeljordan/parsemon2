{ buildPythonPackage, attrs, hypothesis, pytest, pytest-benchmark
, pytest-profiling, pytestcov, sphinx, setuptools-rust, cargo, rustc, python }:
buildPythonPackage {
  pname = "parsemon2";
  version = "dev";
  checkInputs = [
    hypothesis
    pytest
    pytest-benchmark
    pytest-profiling
    pytestcov
    setuptools-rust
  ];
  nativeBuildInputs = [ sphinx rustc cargo ];
  propagatedBuildInputs = [ attrs cargo rustc ];
  buildInputs = [ setuptools-rust ];
  # buildPhase = ''
  #   ${python.interpreter} setup.py bdist_wheel
  # '';
  src = ../.;
  postPhases = [ "buildDocsPhase" "installDocsPhase" ];
  buildDocsPhase = ''
    make man
  '';
  doCheck = false;
  installDocsPhase = ''
    mkdir -p $out/share/man/man3
    cp build/man/parsemon2.3 $out/share/man/man3/parsemon2.3
  '';
}
