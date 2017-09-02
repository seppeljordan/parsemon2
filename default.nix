{ buildPythonPackage, pytest, mypy, lib }:
buildPythonPackage {
  name = "parsemon2";
  buildInputs = [ pytest mypy ];
  src = lib.cleanSource ./.;
  checkPhase = ''
    sh run-tests.sh
  '';
  shellHook = ''
    export PYTHONPATH=$PWD/src:$PYTHONPATH
  '';
}
