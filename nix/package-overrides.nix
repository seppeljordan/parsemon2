self: super: {
  gprof2dot = self.callPackage ./gprof2dot.nix { };
  pytest-profiling = self.callPackage ./pytest-profiling.nix { };
  parsemon2 = self.callPackage ./parsemon2.nix { };
}
