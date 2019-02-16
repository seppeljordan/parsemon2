{ buildPythonPackage, fetchPypi}:
buildPythonPackage rec {
  pname = "gprof2dot";
  version = "2017.9.19";
  src = fetchPypi {
    inherit pname version;
    sha256 = "17ih23ld2nzgc3xwgbay911l6lh96jp1zshmskm17n1gg2i7mg6f";
  };
}
