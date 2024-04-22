# Darktable Launcher
A CLI for creating and opening multiple Darktable libraries.

Requires
- Python 3
  - click
  - osutil
- Darktable

## Install

1. Download `dtl.py` and place it somewhere in your PATH (_$HOME/bin_ for example)
2. Install Python dependencies 

```
pip3 install --user click osutil
```
3. Install Darktable, via the package manager or flatpak
```
{apt/dnf/pamac} install darktable
flatpak install flathub org.darktable.Darktable
```

## Usage

### Create project
```
dtl.py create /path/to/project
```

### Open project
```
dtl.py open /path/to/project
```

If you happen to move your project to a new location, `dtl open PROJECT` 
will automatically update the `library.db` file to match the new location.

Note: It's recommended to keep image files inside the project folder, say in _PROJECT/images_.
This will help with full portability when moving project locations, due to _/path/to/PROJECT_ being the only location that is updated.