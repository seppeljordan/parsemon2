{ buildPythonPackage, pytest, mypy, flake8, lib }:
buildPythonPackage {
  name = "parsemon2";
  buildInputs = [ pytest mypy flake8 ];
  src = lib.cleanSource ./.;
  checkPhase = ''
    sh run-tests.sh
  '';
  shellHook = ''
    export PYTHONPATH=$PWD/src:$PYTHONPATH
  '';
}
