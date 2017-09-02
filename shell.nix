with (import <nixpkgs> {});

(callPackage ./default.nix {
  buildPythonPackage = python3Packages.buildPythonPackage;
  pytest = python3Packages.pytest;
  flake8 = python3Packages.flake8;
})
