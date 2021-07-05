Markers by K. Glazyrin (lorcat@gmail.com, konstantin.glazyrin@gmail.com)
v. 0.6

Program creating an overlay on top of a live camera feed - marker.
Main purpose - indication of the position of interest (X-ray beam, laser beam).

Program may use a profile configuration name as a parameter - to keep track of different configurations.
The default profile configuration file is called 'markers.ini'. Please edit it to adjust starting positions if needed (e.g. multi-monitor setup - if you do not see the window).
You can delete the corresponding.ini file in order to start from scratch.

The most useful shortcuts (with overlay window selected):
Left, right, up, down arrows - move the overlay (add ALT keypress for small steps)
Shift + Left, right, up, down arrows - resize the overlay window (add ALT keypress for small steps)
CTRL + Left, right, up, down arrows - move the additional cross (offset cross)

c - show/hide cental cross indicating the center of the marker
CTRL+c - show/hide the additional cross use to indicate an offset

F2-F7 - selection of different marker windows as shown in the Style Tab of the main gui window.
TAB - use to cycle through different marker styles, add CTRL to cycle through different colors.

etc. - please see the code

Licenses: PyQt4 - GPL (v2 or v3) - more details at https://wiki.python.org/moin/PyQt/PyQtLicensing
Python - see the corresponding https://www.python.org/download/releases/2.7/license/ page
Other modules - see the corresponding descriptions.

K. Glazyrin code - LGPL v. 3, source code can be found at https://github.com/lorcat/markers

Installation:
1. Install vcredist_x86.exe (https://www.microsoft.com/en-us/download/details.aspx?id=29)
   This will install msvcm90.dll, msvcp90.dll, msvcr90.dll
2. Run the program

Acknowledgements:
Many thanks to py2exe project (http://www.py2exe.org/), my family for patience:)