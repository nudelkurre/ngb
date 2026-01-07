{
    description = "Flake utils demo";

    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    };

    outputs =
        { self, nixpkgs }:
        let
            inherit (nixpkgs) lib;
            systems = [
                "x86_64-linux"
            ];

            devSystems = [
                "x86_64-linux"
            ];

            forAllSystems = lib.genAttrs systems;
            forAllDevSystems = lib.genAttrs devSystems;
        in
        {
            packages = forAllSystems (
                system:
                let
                    pkgs = nixpkgs.legacyPackages.${system};
                in
                {
                    default = self.packages.${system}.ngb;
                    ngb = import ./. { inherit (pkgs) pkgs stdenv; };
                }
            );
            apps = forAllSystems (system: {
                default = self.apps.${system}.ngb;
                ngb = {
                    type = "app";
                    program = "${self.packages.${system}.ngb}/bin/ngb";
                };
            });
            devShells = forAllDevSystems (
                system:
                let
                    pkgs = nixpkgs.legacyPackages.${system};
                in
                {
                    default = pkgs.mkShell {
                        packages = with pkgs; [
                            gobject-introspection
                            gtk4
                            gtk4-layer-shell
                            hatch
                            makeWrapper
                            (python3.withPackages (
                                python-pkgs: with python-pkgs; [
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
                                    tomli
                                    tomli-w
                                    tzlocal
                                ]
                            ))
                            wrapGAppsHook4
                        ];
                        shellHook = ''
                            export PS1='\[\e[1;32m\][\u@\h:\w]\[\e[1;31m\](dev)\[\e[1;32m\]$\[\e[0m\] '
                        '';
                        env = {
                            "LD_LIBRARY_PATH" = "$out/lib:${pkgs.gtk4-layer-shell}/lib:$LD_LIBRARY_PATH";
                        };
                    };
                }
            );
            overlay = final: prev: {
                ngb = final.callPackage ./default.nix { };
            };
            homeManagerModules = {
                ngb = import ./hm-module.nix {
                    inherit self;
                    inherit (nixpkgs) ngb;
                };
            };
        };
}
