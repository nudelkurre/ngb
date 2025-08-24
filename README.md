# ngb


## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
  - [Bars](#bars)
    - [Output](#output)
    - [Widgets](#widgets)
    - [Widget modules](#widget-modules)
      - [Bluetooth](#bluetooth)
      - [Clock](#clock)
      - [Cpu](#cpu)
      - [Disk](#disk)
      - [Headset](#headset)
      - [Network](#network)
      - [Volume](#volume)
      - [Weather](#weather)
      - [Workspace](#workspace)
  - [Icon_size](#icon_size)
  - [Spacing](#spacing)
- [License](#license)

## Installation

### Install dependenices
Install all dependencies needed to build ngb.

#### Arch Linux
```console
sudo pacman -S python python-pip git gtk4 gtk4-layer-shell glib2 gobject-introspection
```
#### Fedora
```console
sudo dnf install python3 python3-pip git gtk4-devel gtk4-layer-shell-devel glib2-devel gobject-introspection-devel
```

### Install ngb
Build from source and install.
```console
pip install git+https://github.com/nudelkurre/ngb.git
```

### Nixos

#### Run from terminal
To run latest version from main branch without installing ngb
```console
nix run github:nudelkurre/ngb#ngb
```

To run latest commits
```console
nix run github:nudelkurre/ngb/develop#ngb
```

To run specific release
```console
nix run github:nudelkurre/ngb/<version>
```

#### Add to nix flake
Add flake as input to flake.nix

```nix
inputs = {
    # Use this for latest release
    ngb.url = "github:nudelkurre/ngb";

    # Use this for latest commits
    ngb.url = "github:nudelkurre/ngb/develop#ngb"

    # Use this to pin to specific version
    ngb.url = "github:nudelkurre/ngb/<version>";
  };
```

Add the ngb overlay to nixpkgs.overlays to be able to get the package inside nixpkgs
```nix
nixpkgs.overlays = [
    ngb.overlay
];
```

To be able to configure ngb via home manager, import the module inside your home manager modules
```nix
homeConfigurations = {
  myUser = home-manager.lib.homeManagerConfiguration {
      modules = [
          ngb.outputs.homeManagerModules.ngb
      ];
  };
};
```

## Configuration
The configuration is a json formated file stored in $XDG_CONFIG_HOME/ngb/config.json if XDG_CONFIG_HOME is set, else it is stored in $HOME/.config/ngb/config.json

If a configuration file is not found when ngb first run, it will create one in the right location specified above and looks like this:

```json
{
  "bars": [
      {
          "output": "DP-1",
          "gaps": 2,
          "widgets": {
              "left": [
                  {
                      "config": {},
                      "module": "workspace"
                  }
              ],
              "center": [],
              "right": [
                  {
                      "config": {
                          "mountpoint": "/"
                      },
                      "module": "disk"
                  },
                  {
                      "config": {
                          "interface": "eth0"
                      },
                      "module": "network"
                  },
                  {
                      "config": {},
                      "module": "volume"
                  },
                  {
                      "config": {
                          "timeformat_normal": "%H:%M:%S",
                          "timeformat_revealer": "%Y-%m-%d"
                      },
                      "module": "clock"
                  }
              ]
          }
      }
  ],
  "icon_size": 20,
  "spacing": 5
  }
```
### bars
Bars is a list of bars containing objects with settings for each bar.

#### output
Output sets the output to show the bar on.

#### gaps
Set spacing to use around the bar. Set per bar and can be different for each bar.

#### widgets
Widgets is an object that keeps three lists, center, left and right. The lists contains the widgets to show on respective position of the bar.

#### widget modules
Each widget module contain an object with a module name and config object.
```json
{
  "config": {},
  "module": "module_name"
}
```
Every widget can set the following for each module.
|configureation key|description|data type|
|---|---|---|
|icon_size|Set the icons font size|Integer|
|spacing|Number of pixels to set as spacing between icon and text|Integer|
|timer|How often the module should be updated in seconds|Integer|
If icon_size and spacing is not set in the module, it will use the global set value or if not set at all, will use the default value (icon_size=20, spacing=5)

##### Bluetooth
Show battery level of all connected bluetooth devices.
Bluetoothctl is needed to be in $PATH to work.

##### Clock
Show a clock and can be configured to show different formats and also show additional format if clicked on. If right click on clock, a calendar is shown in a dropdown.
|configureation key|description|data type|
|---|---|---|
|timeformat_normal||String using date format|
|timeformat_revealer||String using date format|
|show_heading||Boolean|
|show_day_names||Boolean|
|show_week_numbers||Boolean|

##### Cpu
Show current cpu usage in percent

##### Disk
Show the percentage used of the chosen mountpoint, and if clicked on will show a dropdown with which mountpoint it shows, a bar visualize disk usage and text showing amount used/total space.
|configureation key|description|data type|
|---|---|---|
|mountpoint|Mountpoint to use|String|

##### Headset
Use the command headsetcontrol to show current battery level of compatible headset.
headsetcontrol is needed to be in $PATH to work.

##### Network
Show ipv4 address of chosen interface. When clicked on show a dropdown with interface name, mac address, ipv4 address and ipv6 addresses of interface.
|configureation key|description|data type|
|---|---|---|
|interface|Set interface name to show|String|

##### Volume
Show the current volume of default sink. By default, click on widget will show a dropdown with all sinks and be able to use slider to set volume, middle click will mute and right click will change default sink to the next in the list. Left click and middle click action can be swapped in config.
wpctl is needed to be in $PATH to work.
|configureation key|description|data type|
|---|---|---|
|click_to_mute|Swap left and middle click action, to make left click toggle mute|Boolean|

##### Weather
Show current temperature of specified city. Left click will show a dropdown with city name, current temperature, current wind speed and current weather description.
Currently only gets the data from SMHI API and only work in Sweden. YR.no (for nordic countries) and OpenWeatherMap (for global) is planned for future.
|configureation key|description|data type|
|---|---|---|
|city|City to show weather info for|String|

##### Workspace
Show active workspaces and highlight the focused one. Can be set to show only a specific monitor or show all workspaces from all monitors.
Works with SwayWM, Hyprland and Niri (requires xwayland-satellite for the moment).
|configureation key|description|data type|
|---|---|---|
|monitor|Set either specific monitor or "all" for all workspaces|String|
|names|Can be used if workspace names is numbers but want to change to icons|Object of key-value pairs with strings as value|

### Icon_size
Set icon size for every widget in all bars.

### Spacing
Set spacing to use for every bar. Spacing is used between each widget, between label and icon for each widget (can be overridden in each widget module, described [above](#widget-modules)) and as margin in top and bottom of dropdowns.

### Corner_radius
Set the corner radius to use for all bars. Set in pixels.

## License

`ngb` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
