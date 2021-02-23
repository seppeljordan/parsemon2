{ buildPythonPackage, parseSetupCfg }:

with builtins;

let
in { src, ... }@arguments:

let
  parsedSetupCfg = parseSetupCfg (readFile (src + "/setup.cfg"));
  pname = parsedSetupCfg.metadata.name;
  version = parsedSetupCfg.metadata.version;

in buildPythonPackage ({ inherit pname version; } // arguments)
