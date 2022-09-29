from STEAM_app_class import SteamApp
import cv2
import time

vs = cv2.VideoCapture(0)

hiResWidth = 960 #1280
hiResHeight = 480 #960
vs.set(3,hiResWidth)
vs.set(4,hiResHeight)

time.sleep(2)

steamApp = SteamApp(vs)
steamApp.root.mainloop()