# KS Node Outliner
> Boost productivity with custom Python-powered filters.

This Outliner for Maya allows you to more easily organize your scene with easier access to Maya's built-in filters, and a filter-builder to make your own advanced custom filters.

**Selection Filters** allows the outliner to show nodes related to your selected objects, so you can see shaders, textures and more only relevant to the model you're working on.

**Script Filters** utilizes custom Python functions for more complex filter operations, such as filtering based on attribute values, or only showing geometry with NGons in them.

**Slow Mode** disables all filtering unless a Selection Filter or Script Filter is active, as automatically updating filters can be very unresponsive in larger Maya scenes.

**Filter Manager** allows you to make and organize your own custom filters. Menu presets can be made to only show filters relevant to the task you're working on.

## Trial

An unrestricted Trial version is available for free, and will have a small Trial-label on the bottom of the interface. To remove this label please purchase the tool and support the development.
http://kimstrandli.com/script-nodeoutliner/

## Installation

Copy the "ks_nodeOutliner" folder into a directory where Maya can access scripts and python plugins.
Example - Windows: C:\Users\USERNAME\Documents\maya\2019\scripts

Then run the following Python command inside Maya:

```sh
from ks_nodeOutliner import ksNodeOutliner
ksNodeOutliner.OpenNodeOutliner()
```


