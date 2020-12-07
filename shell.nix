let
  lock = builtins.fromJSON (builtins.readFile ./flake.lock);
  system = builtins.currentSystem;
  flake-compat-source = fetchTarball {
    url =
      "https://github.com/edolstra/flake-compat/archive/${lock.nodes.flake-compat.locked.rev}.tar.gz";
    sha256 = lock.nodes.flake-compat.locked.narHash;
  };
  flake-compat = import flake-compat-source;
  parsemon2 = (flake-compat {
    src = ./.;
  }).shellNix.packages."${system}".python.pkgs.parsemon2;
  maybeAttrs = attributeSet: name: default:
    if builtins.hasAttr name attributeSet then
      attributeSet."${name}"
    else
      default;
in parsemon2.overridePythonAttrs (old: {
  nativeBuildInputs = maybeAttrs old "nativeBuildInputs" [ ]
    ++ maybeAttrs old "checkInputs" [ ];
})
