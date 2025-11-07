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
        services.ngb = {
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
                                    type = types.nullOr types.int;
                                    default = null;
                                    description = "Set the size of gap around the bar";
                                };
                                height = mkOption {
                                    type = types.nullOr types.int;
                                    default = null;
                                    description = "Set the height to use for the bar (minimum height, if font size is to big bar will get bigger)";
                                };
                                layer = mkOption {
                                    type = types.nullOr (types.enum [
                                        "background"
                                        "bottom"
                                        "overlay"
                                        "top"
                                    ]);
                                    default = null;
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
                gaps = mkOption {
                    type = types.nullOr types.int;
                    default = null;
                    description = "Set the size of gap around the bar";
                };
                height = mkOption {
                    type = types.nullOr types.int;
                    default = null;
                    description = "Set the height to use for the bar (minimum height, if font size is to big bar will get bigger)";
                };
                icon_size = mkOption {
                    type = types.int;
                    default = 20;
                    description = "Set font size of icons";
                };
                layer = mkOption {
                    type = types.nullOr (types.enum [
                        "background"
                        "bottom"
                        "overlay"
                        "top"
                    ]);
                    default = null;
                    description = "Set which layer shell layer to show the bar";
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
    config = lib.mkIf config.services.ngb.enable {
        systemd = {
            user = {
                services = {
                    "ngb" = {
                        Unit = {
                            Description = "ngb status bar";
                            PartOf = "graphical-session.target";
                        };
                        Install = {
                            WantedBy = [ "graphical-session.target" ];
                        };
                        Service = {
                            ExecStart = "${config.programs.ngb.package}/bin/ngb";
                            Restart = "always";
                            RestartSec = "5s";
                        };
                    };
                };
            };
        };
        xdg.configFile."ngb/config.json" = 
            let
                filterNulls = attrs: lib.filterAttrs (key: value: value != null) attrs;
                filtered = filterNulls (config.programs.ngb.settings // { bars = map filterNulls config.programs.ngb.settings.bars; });
            in{
            text = ''
                ${builtins.toJSON filtered}
            '';
        };
    };
}