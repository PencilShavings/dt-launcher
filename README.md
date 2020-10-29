# Darktable Launcher
A CLI for creating and opening multiple Darktable libraries.

Requires
- Python 3
  - click
  - osutil
- Darktable

## Usage

### Create project
```
dtl.py create /path/to/project
```

### Open project
```
dtl.py open /path/to/project
```

If you happen to move your project to a new location `dtl open PROJECT` 
will automatically update the `library.db` file to match the new location.