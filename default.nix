with (import <nixpkgs> {});

let
  f =
    { buildPythonPackage, pytest, mypy, flake8, sphinx, lib }:
    buildPythonPackage {
      name = "parsemon2";
      buildInputs = [ pytest mypy flake8 sphinx];
      src = lib.cleanSource ./.;
      checkPhase = ''
        sh run-tests.sh
      '';
      shellHook = ''
        export PYTHONPATH=$PWD/src:$PYTHONPATH
      '';
      postPhases = [ "buildDocsPhase" "installDocsPhase" ];
      buildDocsPhase = ''
        make man
      '';
      installDocsPhase = ''
        mkdir -p $out/share/man/man3
        cp build/man/parsemon2.3 $out/share/man/man3/parsemon2.3
      '';
    };
  drv = callPackage f {
    buildPythonPackage = python3Packages.buildPythonPackage;
    pytest = python3Packages.pytest;
    flake8 = python3Packages.flake8;
    sphinx = python3Packages.sphinx;
  };
in
drv
