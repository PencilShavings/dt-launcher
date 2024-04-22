# How to use dtl

## Create a project
A project is a directory with a custom darktable configdir.
This includes the darktable data.db & library.db files along with a cache dir.
Ideally all images related to the project should be housed there too.

Creating a project is a good way to store, organize and isolate your jobs from one another.
Why does your freelance wedding photos have to be mixed in with your road tip across the country!

To create a new project:
```
dtl create /path/to/project
```
dtl will create all missing directories in the given path, so be careful!.

By default, dtl will not create a project in an existing folder.
To use an existing folder, use the `--init` option.

```
dtl create --init /path/to/project
```
## Open a project
Now that a project is created / initialized, you can open the project in darktable with the following:
```
dtl open /path/to/project
```

Give it a second and darktable should launch using the custom parameters.

### Darktable
By default, dtl will look for `darktable` in your PATH. If `darktable` is not found, dtl wont launch.
You can use `--darktable /path/to/darktable` to point to a different binary in or outside your PATH, such as an AppImage.

You can also use the Flatpak version of darktable. You can either pass `--darktable org.darktable.Darktable`,
OR you can simply pass `--use-flatpak`, which will set it internally.
If you for some reason decided to set both options , `--darktable` & `--use-flatpak`, `--darktable` is ignored.

### Flatpak permissions
This is just a reminder that Flatpaks dont always have access to the entire filesystem.
If you are like me and have secondary hard drives installed, make sure org.darktable.Darktable has access to the mount points.
This can be done on the command line via flatpak or through the GUI with [Flatseal](https://flathub.org/apps/com.github.tchx84.Flatseal).

```
flatpak override org.darktable.Darktable --filesystem=/path/to/wherever
```

## Moving project locations
The magic of dtl is not being a shortcut to running darktable with a custom launch options,
but being able to update the library.db file using a new location.

If you just moved a project and reopened it manually with custom launch options, you would find that your images would be missing!
This is because all the references to your images will still be pointing to the original location.

When opening projects with dtl, dtl keeps track of where the project is & where it has been.
It compares the two locations and updates the references in library.db automatically upon launch.
Therefor, you can easily and quickly move projects to new locations without the worry of loosing or breaking references.

### Example
Create a new project pertaining to a particular job or subject.
Place your images inside the project folder.
I don't want to dictate how you organize you projects, but I like to create an image folder to house the images.
```
dtl create ~/Pictures/Road_Trip_2024
mkdir ~/Pictures/Road_Trip_2024/images

# *puts iamges in ~/Pictures/Road_Trip_2024/images

dtl open ~/Pictures/Road_Trip_2024

# *imports images from ~/Pictures/Road_Trip_2024/images
# *does some editing or sorting
# *closes darktable
```

Now move your project to somewhere else and re-open!
You can even rename the root project directory if you want.

```
mv ~/Pictures/Road_Trip_2024 ~/Desktop/
dtl open ~/Desktop/Road_Trip_2024
```
Voila! Everything should be right where you left it like nothing ever happened.

