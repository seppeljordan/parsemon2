{
  description = "parsemon2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    let
      systemDependent = flake-utils.lib.eachDefaultSystem (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlay ];
          };
          python = pkgs.python3;
          runCodeAnalysis = name: command:
            pkgs.runCommand "${name}-parsemon2" { } ''
              cd ${self}    
              ${command}
              mkdir $out
            '';
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
                  twine
                  wheel
                  isort
                  setuptools-rust
                  virtualenv
                ]))
              pkgs.bump2version
              pkgs.rustc
              pkgs.cargo
              pkgs.git
              pkgs.graphviz

              # nix linter is broken in the current version of nixpkgs
              # pkgs.nix-linter
            ];
          };
          defaultPackage = python.pkgs.parsemon2;
          packages = { inherit python; };
          checks = {
            python38 = pkgs.python38.pkgs.parsemon2;
            python39 = pkgs.python39.pkgs.parsemon2;
            nixfmt-check = runCodeAnalysis "nixfmt" ''
              ${pkgs.nixfmt}/bin/nixfmt --check \
                  $(find . -type f -name '*.nix')
            '';
            black-check = runCodeAnalysis "black" ''
              ${python.pkgs.black}/bin/black --check .
            '';
            mypy-check = runCodeAnalysis "mypy" ''
              ${python.pkgs.mypy}/bin/mypy src/parsemon
            '';
            isort-check = runCodeAnalysis "isort" ''
              ${python.pkgs.isort}/bin/isort \
                  --settings-path setup.cfg \
                  --check-only \
                  --diff \
                  setup.py \
                  . \
                  test-pypi-install
            '';
            flake8-check = runCodeAnalysis "flake8" ''
              ${python.pkgs.flake8}/bin/flake8
            '';
          };
        });
      systemIndependent = {
        lib = { package = import nix/parsemon2.nix; };
        overlay = final: prev:
          let
            packageOverrides = final.callPackage nix/package-overrides.nix { };
          in {
            python3 = prev.python3.override { inherit packageOverrides; };
            python3Packages = final.python3.pkgs;
            python38 = prev.python38.override { inherit packageOverrides; };
            python38Packages = final.python38.pkgs;
            python39 = prev.python39.override { inherit packageOverrides; };
            python39Packages = final.python39.pkgs;
          };
      };
    in systemDependent // systemIndependent;
}
