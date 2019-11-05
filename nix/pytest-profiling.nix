{buildPythonPackage
, fetchPypi

, gprof2dot
, six
, pytest
, setuptools-git
}:
buildPythonPackage rec {
  pname = "pytest-profiling";
  version = "1.7.0";
  propagatedBuildInputs = [
    gprof2dot six pytest
  ];
  buildInputs = [
    setuptools-git
  ];
  doCheck = false;
  src = fetchPypi {
    inherit pname version;
    sha256 = "0abz9gi26jpcfdzgsvwad91555lpgdc8kbymicmms8k2fqa8z4wk";
  };
}
