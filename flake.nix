{
  description = "Flake utils demo";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages = rec {
          default = ngb;
          ngb = import ./. { inherit (pkgs) pkgs stdenv; };
        };
        apps = rec {
          default = ngb;
          ngb = flake-utils.lib.mkApp { drv = self.packages.${system}.ngb; };
        };
        devShells = rec {
          default = pkgs.mkShell {
            packages = with pkgs; [
              gobject-introspection
              gtk4
              gtk4-layer-shell
              hatch
              makeWrapper
              (python3.withPackages (python-pkgs: with python-pkgs; [
                i3ipc
                meson
                meson-python
                ninja
                psutil
                pygobject3
                pyyaml
                screeninfo
                shutilwhich
              ]))
              wrapGAppsHook
            ];
            shellHook = ''
              export PS1='\[\e[1;32m\][\u@\h:\w]\[\e[1;31m\](dev)\[\e[1;32m\]$\[\e[0m\] '
            '';
            env = {
              "LD_LIBRARY_PATH" = "$out/lib:${pkgs.gtk4-layer-shell}/lib:$LD_LIBRARY_PATH";
            };
          };
        };
      }
    );
}
