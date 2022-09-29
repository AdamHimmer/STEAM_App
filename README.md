Programs for the vision system demonstration for the STEAM summit

The system consists of a webcam run by a Raspberry Pi, viewing a gray colored beam (roughly the size of a 2x4, 12" long). A screen connected to the Pi will have a GUI that displays the screen and prompts the user to place colored washers at certain locations along the beam. When the user believes they have them in the right location, they select the 'Measure' button, which triggers the Pi to detect the corners of the beam, the location of the washers, and determine how close the user was to the correct location. The GUI will highlight the detected corners of the beam, the centerline of the beam, the detected centers of the washers, and the desired nominal location of the washers, to demonstrate how a system like this is capable of making real-time physical measurements.

STEAM_app_class defines the SteamApp class, and contains the brunt of the
code for doing the vision measuring.

STEAM_App defines the camera and initiates the class. Run this to
start the program.
