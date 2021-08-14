{ buildPythonPackage, hypothesis, pytest, pytest-benchmark, pytest-profiling
, pytestcov, sphinx, setuptools-rust, pytestCheckHook, rustPlatform }:
buildPythonPackage rec {
  pname = "parsemon2";
  version = "dev";
  src = ../.;
  cargoDeps = rustPlatform.fetchCargoTarball {
    inherit src;
    name = "parsemon2-3.2.1";
    sha256 = "zGvgA3m7FQxwq+3+DvnDp2n5Tpydnt83iQBOHmVj1C4=";
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
