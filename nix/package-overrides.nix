self: super: {
  pytest-profiling = self.callPackage ./pytest-profiling.nix { };
  parsemon2 = self.callPackage ./parsemon2.nix { };
}
