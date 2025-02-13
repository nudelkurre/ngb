{pkgs, stdenv, ...}:
with pkgs.python3Packages;

buildPythonApplication rec {
  pname = "pybar";
  version = "testing";
  pyproject = true;
  src = ./.;

  build-system = [
    hatchling
  ];

  nativeBuildInputs = with pkgs; [
    wrapGAppsHook
    gobject-introspection
    pkg-config
    makeWrapper
  ];

  buildInputs = with pkgs; [
    gtk4
    gtk4-layer-shell
  ];

  dependencies = [
    pygobject3
    screeninfo
  ];

  doCheck = false;

  makeWrapperArgs = [
    ''--set LD_LIBRARY_PATH "$out/lib:${pkgs.gtk4-layer-shell}/lib:$LD_LIBRARY_PATH"''
  ];
}
