# markers
There are situations when you do not have full control on camera software, but you need to:
1. find a center of an image
2. find a center of an image portion based on the image content (certain shape)
3. indicate to other people certain special positions (location of laser spot and etc.)

This program 'markers' is created as an overlay allowing the final user to perform these tasks.

This program supports multiple profile - settings files.
Default profile is called markers.ini and is saved into the directory location of the program.
Make sure, the program has sufficient rights to save file. It was never indended to run under superuser rights.

Usage:
python program_file.py profile_name.ini

if no profile name is given - program uses markers.ini as a default profile name.