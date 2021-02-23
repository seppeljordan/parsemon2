{ fetchFromGitHub, lib, parseSetupCfg }:
lib.fix (self:
  let callPackage = lib.callPackageWith self;
  in {
    inherit fetchFromGitHub lib parseSetupCfg;
    packageOverrides = callPackage ./package-overrides.nix { };
  })
