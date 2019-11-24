{ buildPythonPackage
, fetchFromGitHub
, pyaml
, click
}:

buildPythonPackage rec {
  pname = "bumpv";
  version = "0.3.0";
  src = with builtins; fetchFromGitHub (fromJSON (readFile ./bumpv.json));
  propagatedBuildInputs = [
    pyaml
    click
  ];
}
