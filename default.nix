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
    }:
    let
    sourceFilter = name: type:
      let
        baseName = with builtins; baseNameOf (toString name);
        ignoreDirectoryBy = operation: lib.foldl
          (accu: element: accu || (type == "directory" && operation element))
          false;
        ignoreDirectoryNames = ignoreDirectoryBy (x: x == baseName);
        ignoreDirectoryByPrefix = ignoreDirectoryBy (x: lib.hasSuffix x baseName);
      in
      lib.cleanSourceFilter name type &&
      ignoreDirectoryNames [ "tmp" "__pycache__" ".pytest_cache" ] &&
      ignoreDirectoryByPrefix [ ".egg-info" ] ;
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
      pytest = self.pytest_3;
      pytest-profiling = super.callPackage nix/pytest-profiling.nix {};
    };
    in nixpkgs."python${pythonVersion}".override {inherit packageOverrides;};
  drv = python.pkgs.callPackage f {};
in
drv
