{
  description = "parsemon2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nix-setuptools.url = "github:seppeljordan/nix-setuptools";
  };

  outputs = { self, nixpkgs, flake-utils, nix-setuptools }:
    let
      modules = import nix/modules.nix {
        inherit (nix-setuptools.lib.setuptools) parseSetupCfg;
        inherit (nixpkgs) lib;
      };
      supportedSystems = flake-utils.lib.defaultSystems;
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
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
                with ps;
                [
                  black
                  flake8
                  hypothesis
                  isort
                  mypy
                  pip
                  pytest-benchmark
                  pytest-profiling
                  pytestcov
                  setuptools-rust
                  sphinx
                  virtualenv
                  wheel
                ] ++
                # as of april 2021 pandas does not support i686
                # architecture.  Since this is a dependency of twine,
                # we cannot support the release infrastructure on
                # those machines.
                nixpkgs.lib.optional (system != "i686-linux") twine))
              pkgs.rustc
              pkgs.rustfmt
              pkgs.cargo
              pkgs.git
              pkgs.graphviz
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
            rustfmt-check = runCodeAnalysis "rustfmt" ''
              ${pkgs.rustfmt}/bin/rustfmt \
                  --check \
                  $(find src/ -type f -name '*.rs')
            '';
          };
        });
      systemIndependent = {
        lib = {
          inherit (modules) packageOverrides;
          package = import nix/parsemon2.nix;
        };
        overlay = final: prev:
          let packageOverrides = modules.packageOverrides;
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
