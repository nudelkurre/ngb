{ pkgs, ... }:
with pkgs.python3Packages;

buildPythonApplication {
    pname = "ngb";
    version = "0.5.0";
    pyproject = true;
    src = ./.;

    build-system = [
        hatchling
    ];

    nativeBuildInputs = with pkgs; [
        wrapGAppsHook4
        gobject-introspection
        pkg-config
        makeWrapper
    ];

    buildInputs = with pkgs; [
        gtk4
        gtk4-layer-shell
    ];

    dependencies = [
        geopy
        meson
        meson-python
        ninja
        psutil
        pydbus
        pygobject3
        pyyaml
        requests
        screeninfo
        shutilwhich
        tzlocal
    ];

    doCheck = false;

    makeWrapperArgs = [
        ''--set LD_LIBRARY_PATH "$out/lib:${pkgs.gtk4-layer-shell}/lib:$LD_LIBRARY_PATH"''
    ];
}
