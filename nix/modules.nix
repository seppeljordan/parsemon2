{ lib, parseSetupCfg }:
lib.fix (self:
  let callPackage = lib.callPackageWith self;
  in {
    inherit lib parseSetupCfg;
    packageOverrides = callPackage ./package-overrides.nix { };
  })
