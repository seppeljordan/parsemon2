{
  description = "parsemon2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    let
      packageOverrides = import nix/package-overrides.nix;
      overlay = final: prev: {
        python3 = prev.python3.override { inherit packageOverrides; };
        python3Packages = final.python3.pkgs;
        python36 = prev.python36.override { inherit packageOverrides; };
        python36Packages = final.python36.pkgs;
        python37 = prev.python37.override { inherit packageOverrides; };
        python37Packages = final.python37.pkgs;
        python38 = prev.python38.override { inherit packageOverrides; };
        python38Packages = final.python38.pkgs;
        python39 = prev.python39.override { inherit packageOverrides; };
        python39Packages = final.python39.pkgs;
      };
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ overlay ];
          };
          python = pkgs.python3;
        in {
          devShell = pkgs.mkShell {
            buildInputs = [
              (python.withPackages (ps:
                with ps; [
                  attrs
                  black
                  hypothesis
                  flake8
                  mypy
                  pytest-benchmark
                  pytest-profiling
                  pytestcov
                  sphinx
                  bumpv
                  twine
                  wheel
                  isort
                ]))
              pkgs.git
              pkgs.graphviz
              pkgs.nix-linter
            ];
          };
          defaultPackage = python.pkgs.parsemon2;
          packages = { inherit python; };
          checks = {
            python36 = pkgs.python36.pkgs.parsemon2;
            python37 = pkgs.python37.pkgs.parsemon2;
            python38 = pkgs.python38.pkgs.parsemon2;
            python39 = pkgs.python39.pkgs.parsemon2;
            nixfmt-check = pkgs.runCommand "nixfmt-parsemon2" { } ''
              ${pkgs.nixfmt}/bin/nixfmt --check \
                $(find ${self} -type f -name '*.nix')
              mkdir $out
            '';
            black-check = pkgs.runCommand "black-parsemon2" { } ''
              cd ${self}
              ${python.pkgs.black}/bin/black --check .
              mkdir $out
            '';
            mypy-check = pkgs.runCommand "mypy-parsemon2" { } ''
              cd ${self}
              ${python.pkgs.mypy}/bin/mypy parsemon
              mkdir $out
            '';
            isort-check = pkgs.runCommand "isort-parsemon2" { } ''
              cd ${self}
              ${python.pkgs.isort}/bin/isort \
                  --settings-path setup.cfg \
                  --check-only \
                  -df \
                  . \
                  test-pypi-install
              mkdir $out
            '';
            flake8-check = pkgs.runCommand "flake8-parsemon2" { } ''
              cd ${self}
              ${python.pkgs.flake8}/bin/flake8
              mkdir $out
            '';
            nix-linter-check = pkgs.runCommand "nix-linter-parsemon2" { } ''
              cd ${self}
              ${pkgs.nix-linter}/bin/nix-linter -r .
              mkdir $out
            '';
          };
        });
      systemIndependent = { inherit overlay; };
    in systemDependent // systemIndependent;
}
