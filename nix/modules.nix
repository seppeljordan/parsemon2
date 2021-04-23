{ lib, nixSetuptools }:
lib.fix (self:
  let callPackage = lib.callPackageWith self;
  in {
    inherit lib nixSetuptools;
    packageOverrides = callPackage ./package-overrides.nix { };
  })
