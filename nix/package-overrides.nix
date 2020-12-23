{ fetchFromGitHub }:
self: super: {
  gprof2dot = self.callPackage ./gprof2dot.nix { };
  pytest-profiling = self.callPackage ./pytest-profiling.nix { };
  bumpv = self.callPackage ./bumpv.nix { };
  parsemon2 = self.callPackage ./parsemon2.nix { };
  setuptools-rust = super.setuptools-rust.overridePythonAttrs (_old: {
    src = fetchFromGitHub {
      owner = "seppeljordan";
      repo = "setuptools-rust";
      rev = "12c96f0539189d560e09f6338ea1c1a23ee9ff3e";
      sha256 = "g7r7KamiYyagx7kvLW9Iwuv5MSAAm7w964RXXXtGJCc=";
    };
  });
}
