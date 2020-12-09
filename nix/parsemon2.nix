{ buildPythonPackage, attrs, hypothesis, pytest, pytest-benchmark
, pytest-profiling, pytestcov, sphinx }:
buildPythonPackage {
  name = "parsemon2";
  checkInputs =
    [ hypothesis pytest pytest-benchmark pytest-profiling pytestcov ];
  nativeBuildInputs = [ sphinx ];
  propagatedBuildInputs = [ attrs ];
  src = ../.;
  checkPhase = ''
    pytest --benchmark-skip
  '';
  postPhases = [ "buildDocsPhase" "installDocsPhase" ];
  buildDocsPhase = ''
    make man
  '';
  installDocsPhase = ''
    mkdir -p $out/share/man/man3
    cp build/man/parsemon2.3 $out/share/man/man3/parsemon2.3
  '';
}
