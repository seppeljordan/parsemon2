let
  nixpkgs-host = import <nixpkgs> {};
  nixos-stable = with builtins; nixpkgs-host.fetchFromGitHub (
    fromJSON (readFile ./nixpkgs.json)
  );
in
with (import nixos-stable {});

let
  f =
    { buildPythonPackage, pytest, mypy, sphinx, lib, pytestcov, attrs
    , pylint, pytest-benchmark, pyrsistent, hypothesis, flake8
    }:
    let
    sourceFilter = name: type:
      let baseName = with builtins; baseNameOf (toString name); in
      lib.cleanSourceFilter name type &&
      !(
        (type == "directory" && lib.hasSuffix ".egg-info" baseName)||
        (type == "directory" && baseName == "tmp")||
        (type == "directory" && baseName == "__pycache__")||
        (type == "directory" && baseName == ".pytest_cache")
      );
    in
    buildPythonPackage {
      name = "parsemon2";
      checkInputs = [
        pytest
        mypy
        sphinx
        pytestcov
        pylint
        pytest-benchmark
        hypothesis
        flake8
      ];
      propagatedBuildInputs = [ attrs pyrsistent ];
      src = lib.cleanSourceWith {
        filter = sourceFilter;
        src = ./.;
      };
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
  drv = python36.pkgs.callPackage f {};
in
drv
