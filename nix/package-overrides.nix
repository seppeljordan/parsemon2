{ nixSetuptools }:
self: super: {
  setuptoolsPackaging = self.callPackage nixSetuptools.lib.packaging { };
  inherit (self.setuptoolsPackaging) buildSetuptoolsPackage;
  gprof2dot = self.callPackage ./gprof2dot.nix { };
  pytest-profiling = self.callPackage ./pytest-profiling.nix { };
  parsemon2 = self.callPackage ./parsemon2.nix { };
  setuptools-rust = self.callPackage ./setuptools-rust.nix { };
}
