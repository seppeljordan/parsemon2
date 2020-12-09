{ buildPythonPackage, lib, attrs, hypothesis, pytest, pytest-benchmark
, pytest-profiling, pytestcov, sphinx }:
let
  sourceFilter = path: type:
    with lib;
    let
      baseName = with builtins; baseNameOf (toString path);
      ignoreDirectories = all (directory: baseName != directory);
      ignoreEggInfo = !(hasSuffix ".egg-info" baseName);
    in ignoreDirectories [
      "tmp"
      "__pycache__"
      ".pytest_cache"
      "testenv"
      "htmlcov"
      "build"
      "prof"
      "dist"
    ] && ignoreEggInfo;
in buildPythonPackage {
  name = "parsemon2";
  checkInputs =
    [ hypothesis pytest pytest-benchmark pytest-profiling pytestcov ];
  nativeBuildInputs = [ sphinx ];
  propagatedBuildInputs = [ attrs ];
  src = lib.cleanSourceWith {
    filter = sourceFilter;
    src = ./..;
  };
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
