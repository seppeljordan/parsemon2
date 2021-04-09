{ buildPythonPackage, fetchPypi, setuptools-scm

, semantic-version, toml, setuptools }:
buildPythonPackage rec {
  pname = "setuptools-rust";
  version = "0.12.1";
  nativeBuildInputs = [ setuptools-scm ];
  propagatedBuildInputs = [ setuptools semantic-version toml ];
  src = fetchPypi {
    inherit pname version;
    sha256 = "ZHAJ6STwrkOcfz4BQaGEpprSR+y5BExRHaveIy09Vw4=";
  };
}
