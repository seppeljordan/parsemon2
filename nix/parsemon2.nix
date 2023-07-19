{ buildPythonPackage
, hypothesis
, pytest
, pytest-benchmark
, pytest-profiling
, pytestcov
, sphinx
, setuptools-rust
, pytestCheckHook
, rustPlatform
, rustc
, cargo
}:
buildPythonPackage rec {
  pname = "parsemon2";
  version = "dev";
  src = ../.;
  cargoDeps = rustPlatform.fetchCargoTarball {
    inherit src;
    name = "parsemon2-3.2.2";
    hash = "sha256-I7pETxQTkxB8c1sVrs2h9yvhsCuMu3TFh3m1kznMu7k=";
  };

  # building
  nativeBuildInputs = [
    sphinx
    cargo
    rustc
    setuptools-rust
    rustPlatform.cargoSetupHook
    pytestCheckHook
  ];
  preInstallPhases = [ "buildDocsPhase" ];
  buildDocsPhase = ''
    make man 
  '';

  # installing
  postPhases = [ "installDocsPhase" ];
  installDocsPhase = ''
    mkdir -p $out/share/man/man3
    cp build/man/parsemon2.3 $out/share/man/man3/parsemon2.3
  '';

  # tests
  pytestFlagsArray = [ "--benchmark-skip" ];
  checkInputs =
    [ hypothesis pytest pytest-benchmark pytest-profiling pytestcov ];
}
