{ buildPythonPackage, pytest, mypy, lib }:
buildPythonPackage {
  name = "parsemon2";
  buildInputs = [ pytest mypy ];
  src = lib.cleanSource ./.;
  checkPhase = ''
    mypy src/
    PYTHONPATH=src/:$PYTHONPATH pytest
  '';
  shellHook = ''
    export PYTHONPATH=$PWD/src:$PYTHONPATH
  '';
}
