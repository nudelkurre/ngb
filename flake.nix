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
      }
    );
}
