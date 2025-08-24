self:
{
    config,
    pkgs,
    lib,
    ...
}:
with lib;
{
    options = {
        programs.ngb = {
            enable = mkOption {
                type = types.bool;
                default = false;
                description = "Enable ngb";
            };
            package = mkOption {
                type = types.package;
                default = pkgs.ngb;
                description = "Set the package to use for ngb";
            };
            settings = {
                bars = mkOption {
                    type = types.listOf (
                        types.submodule {
                            options = {
                                output = mkOption {
                                    type = types.str;
                                    description = "Set the output to show bar on";
                                };
                                gaps = mkOption {
                                    type = types.int;
                                    description = "Set the size of gap around the bar";
                                };
                                layer = mkOption {
                                    type = types.enum [
                                        "background"
                                        "bottom"
                                        "overlay"
                                        "top"
                                    ];
                                    description = "Set which layer shell layer to show the bar";
                                };
                                widgets = mkOption {
                                    type = types.submodule {
                                        options = {
                                            center = mkOption {
                                                type = types.listOf (
                                                    types.submodule {
                                                        options = {
                                                            config = mkOption {
                                                                type = types.attrs;
                                                                description = "Settings for widget";
                                                                default = { };
                                                            };
                                                            module = mkOption {
                                                                type = types.str;
                                                                description = "Name of widget";
                                                            };
                                                        };
                                                    }
                                                );
                                                default = [ ];
                                            };
                                            left = mkOption {
                                                type = types.listOf (
                                                    types.submodule {
                                                        options = {
                                                            config = mkOption {
                                                                type = types.attrs;
                                                                description = "Settings for widget";
                                                                default = { };
                                                            };
                                                            module = mkOption {
                                                                type = types.str;
                                                                description = "Name of widget";
                                                            };
                                                        };
                                                    }
                                                );
                                                default = [ ];
                                            };
                                            right = mkOption {
                                                type = types.listOf (
                                                    types.submodule {
                                                        options = {
                                                            config = mkOption {
                                                                type = types.attrs;
                                                                description = "Settings for widget";
                                                                default = { };
                                                            };
                                                            module = mkOption {
                                                                type = types.str;
                                                                description = "Name of widget";
                                                            };
                                                        };
                                                    }
                                                );
                                                default = [ ];
                                            };
                                        };
                                    };
                                };
                            };
                        }
                    );
                    default = [ ];
                };
                icon_size = mkOption {
                    type = types.int;
                    default = 20;
                    description = "Set font size of icons";
                };
                spacing = mkOption {
                    type = types.int;
                    default = 5;
                    description = "Set spacing to use in widgets";
                };
                corner_radius = mkOption {
                    type = types.int;
                    default = 0;
                    description = "Set corner radius to all bars";
                };
            };
        };
    };
    config = lib.mkIf config.programs.ngb.enable {
        home.packages = [
            (optionalString (config.programs.ngb.package != null) config.programs.ngb.package)
        ];
        xdg.configFile."ngb/config.json".text = ''
            ${builtins.toJSON config.programs.ngb.settings}
        '';
    };
}
