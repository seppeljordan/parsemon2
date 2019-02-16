let
  nixpkgs-host = import <nixpkgs> {};
  nixos-stable = with builtins; nixpkgs-host.fetchFromGitHub (
    fromJSON (readFile ./nixpkgs.json)
  );
in

let
  nixpkgs = import nixos-stable {};
  f =
    { buildPythonPackage, pytest, mypy, sphinx, lib, pytestcov, attrs
    , pylint, pytest-benchmark, hypothesis, flake8, pytest-profiling, graphviz
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
        pytest-profiling
        graphviz
      ];
      propagatedBuildInputs = [ attrs ];
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
  python = let
    packageOverrides = self: super: {
      gprof2dot = super.callPackage nix/gprof2dot.nix {};
      pytest-profiling = super.callPackage nix/pytest-profiling.nix {};
    };
    in nixpkgs.python36.override {inherit packageOverrides;};
  drv = python.pkgs.callPackage f {};
in
drv
