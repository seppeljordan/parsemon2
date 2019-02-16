{buildPythonPackage
, fetchPypi

, gprof2dot
, six
, pytest
, setuptools-git
}:
buildPythonPackage rec {
  pname = "pytest-profiling";
  version = "1.6.0";
  propagatedBuildInputs = [
    gprof2dot six pytest
  ];
  buildInputs = [
    setuptools-git
  ];
  doCheck = false;
  src = fetchPypi {
    inherit pname version;
    sha256 = "07zc6n8w6skwgp2nljywfn0w4zhxx5h4zrmwk5d1p3m6zzfqqkz4";
  };
}
