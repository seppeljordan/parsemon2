with (import <nixpkgs> {});

(callPackage ./default.nix {
  buildPythonPackage = python3Packages.buildPythonPackage;
  pytest = python3Packages.pytest;
})
