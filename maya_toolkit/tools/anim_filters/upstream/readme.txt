
Animation Curve Filters for Maya 2017+
(c) 2018 Michal Mach

Please report any bugs to michal@michalmach.com and I'll try to fix them as soon as possible.
I will post updates on my Twitter @gameplayAnim.

Thank you Riot Games for sharing their wisdom on animation key reduction algorithm. My thanks also go to
the awesome Python community for creating so many cool scientific projects.


Installation
============
Unzip the script files to your Maya user scripts directory (typically Documents/maya/scripts).

Open a Python tab in the Maya's Script Editor, paste the following code and drag it to a shelf to create a button:

from animFilters import animFilters
reload(animFilters)
animFilters.main()

There's an image in the script folder that you can set as an icon for your shelf button.

How to use
==========
Using the tool is actually really simple.
1) Open the Graph Editor and select animation curves/keys you want to filter
2) Choose one of the filter tabs and hit the Preview button to see the filtered curves
3) Now you can change the numbers or drag the sliders around and the curves will update
4) Once you're satisfied with the result, click Apply
5) If you don't like the result, you can click Cancel and original curves will be restored
6) Closing the tool in Preview mode restores the original curves, so don't forget to hit Apply before closing!

The 'Auto Buffer Curves' checkbox stores the Buffer Curves when you click the Preview button, so you can see
your original curves drawn in grey color with the filtered curves.
You have to enable View / Display Buffer Curves option in the Graph Editor to see them.


Requirements
============
Butterworth and Median filters require SciPy and NumPy Python modules to function.
Publicly available versions of these modules are not compatible with Maya's Python interpreter (mayapy),
but there are good people on the Internet, who compiled them and made them available for download.

Eric Vignola is one of them and here's his Google Drive folder with many interesting modules:
https://drive.google.com/drive/folders/0BwsYd1k8t0lEMjBCa2N1Z25KZXc

You only need to download these two:
scipy-0.19.1-cp27-none-win_amd64.whl
numpy-1.13.1+mkl-cp27-none-win_amd64.whl

After downloading the files, you can simply unzip them to the site-packages folder inside your Maya installation.
Typically "c:\Program Files\Autodesk\Maya20xx\Python\Lib\site-packages" on Windows.
On a Mac, I recommend installing these packages using "pip".

Here's the official guide: https://packaging.python.org/tutorials/installing-packages/

Just remember that you want to use Maya's version of python interpreter (mayapy) and "pip".

Change Log
==========
2018-10-23 (ver 1.0) - original release with Adaptive, Butterworth and Median filters

