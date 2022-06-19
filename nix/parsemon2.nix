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
}:
buildPythonPackage rec {
  pname = "parsemon2";
  version = "dev";
  src = ../.;
  cargoDeps = rustPlatform.fetchCargoTarball {
    inherit src;
    name = "parsemon2-3.2.2";
    sha256 = "GvSNOhLrNZ+E50z1ThF/ZD3I6mL6SDj7lhwQsPiRjmg=";
  };

  # building
  nativeBuildInputs = [
    sphinx
    rustPlatform.rust.cargo
    rustPlatform.rust.rustc
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
