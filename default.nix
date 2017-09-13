with (import <nixpkgs> {});

let
  f =
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
    };
in
(callPackage f {
  buildPythonPackage = python3Packages.buildPythonPackage;
  pytest = python3Packages.pytest;
  flake8 = python3Packages.flake8;
})
