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
          default = pybar;
          pybar = import ./. { inherit (pkgs) pkgs stdenv; };
        };
        apps = rec {
          default = pybar;
          pybar = flake-utils.lib.mkApp { drv = self.packages.${system}.pybar; };
        };
        devShells = rec {
          default = pkgs.mkShell {
            packages = with pkgs; [
              gobject-introspection
              gtk4
              gtk4-layer-shell
              hatch
              makeWrapper
              python3Packages.psutil
              python3Packages.pygobject3
              python3Packages.screeninfo
              wrapGAppsHook
            ];
            shellHook = ''
              export PS1='\n\[\033[1;32m\][nix-shell:\w]\[\033[1;31m\](Dev)\[\033[1;32m\]\$\[\033[0m\]'
            '';
            env = {
              "LD_LIBRARY_PATH" = "$out/lib:${pkgs.gtk4-layer-shell}/lib:$LD_LIBRARY_PATH";
            };
          };
        };
      }
    );
}
