{
  description = "parsemon2";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      supportedSystems = [
        "aarch64-linux"
        # pyopenssl is broken
        # "aarch64-darwin" 
        "i686-linux"
        "x86_64-darwin"
        "x86_64-linux"
      ];
      systemDependent = flake-utils.lib.eachSystem supportedSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ self.overlays.default ];
          };
          python = pkgs.python3;
          runCodeAnalysis = name: command:
            pkgs.runCommand "${name}-parsemon2" { } ''
              cd ${self}    
              ${command}
              mkdir $out
            '';
        in
        {
          formatter = pkgs.nixpkgs-fmt;
          devShells.default = pkgs.mkShell {
            buildInputs = [
              (python.withPackages (ps:
                with ps; [
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
                  twine
                ]))
              pkgs.rustc
              pkgs.rustfmt
              pkgs.cargo
              pkgs.git
              pkgs.graphviz
              python.pkgs.gprof2dot
            ];
          };
          packages = {
            inherit python;
            default = python.pkgs.parsemon2;
          };
          checks = {
            python38 = pkgs.python38.pkgs.parsemon2;
            python39 = pkgs.python39.pkgs.parsemon2;
            python310 = pkgs.python310.pkgs.parsemon2;
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
          packageOverrides = import nix/package-overrides.nix;
          package = import nix/parsemon2.nix;
        };
        overlays.default = final: prev:
          let packageOverrides = self.lib.packageOverrides;
          in
          {
            python3 = prev.python3.override { inherit packageOverrides; };
            python3Packages = final.python3.pkgs;
            python38 = prev.python38.override { inherit packageOverrides; };
            python38Packages = final.python38.pkgs;
            python39 = prev.python39.override { inherit packageOverrides; };
            python39Packages = final.python39.pkgs;
            python310 = prev.python310.override { inherit packageOverrides; };
            python310Packages = final.python310.pkgs;
          };
      };
    in
    systemDependent // systemIndependent;
}
