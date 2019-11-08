{ pythonVersion ? "3" }:

let
  nixpkgs-host = import <nixpkgs> {};
  nixos-stable = with builtins; nixpkgs-host.fetchFromGitHub (
    fromJSON (readFile ./nixpkgs.json)
  );
in

let
  nixpkgs = import nixos-stable { overlays = []; };
  f =
    { buildPythonPackage
    , lib
    , graphviz
    , git

    , attrs
    , flake8
    , hypothesis
    , mypy
    , pylint
    , pytest
    , pytest-benchmark
    , pytest-profiling
    , pytestcov
    , sphinx
    , setuptools_scm
    }:
    let
    sourceFilter = path: type: with lib;
      let
        baseName = with builtins; baseNameOf (toString path);
        ignoreDirectories = all (directory: baseName != directory);
        ignoreEggInfo = ! (hasSuffix ".egg-info" baseName);
      in
      ignoreDirectories [
        "tmp"
        "__pycache__"
        ".pytest_cache"
        "testenv"
        "htmlcov"
        "build"
        "prof"
        "dist"
      ] &&
      ignoreEggInfo;
    in
    buildPythonPackage {
      name = "parsemon2";
      checkInputs = [
        flake8
        graphviz
        hypothesis
        mypy
        pylint
        pytest
        pytest-benchmark
        pytest-profiling
        pytestcov
        sphinx
      ];
      buildInputs = [ setuptools_scm ];
      nativeBuildInputs = [ git ];
      propagatedBuildInputs = [ attrs ];
      src = lib.cleanSourceWith {
        filter = sourceFilter;
        src = ./.;
      };
      checkPhase = ''
        sh run-tests.sh
      '';
      shellHook = ''
        export SOURCE_DATE_EPOCH=315532800
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
    in nixpkgs."python${pythonVersion}".override {inherit packageOverrides;};
  drv = python.pkgs.callPackage f {};
in
drv
