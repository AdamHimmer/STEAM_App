from PIL import Image
from PIL import ImageTk
import tkinter as tki
import threading
import cv2
import numpy as np
from random import random

class SteamApp:
    #Define global variables
    global measureBool
    measureBool = False
    
    global yourScore
    yourScore = []
    
    global x1Values,x2Values,x3Values,x1,x2,x3
    #Below values are used to randomize the location of the three washers for every measurement trial
    x1Values = [1,1.5,2,2.5,3]
    x2Values = [4,4.5,5,5.5,6]
    x3Values = [7,7.5,8,8.5,9]
    x1 = x1Values[int(random()*5)]
    x2 = x2Values[int(random()*5)]
    x3 = x3Values[int(random()*5)]
    
    def __init__(self,vs):
        #Define GUI settings
        self.vs = vs
        self.frame = None
        self.thread = None
        self.stopEvent = None
        self.root = tki.Tk()
        self.panel = None
        self.root.attributes('-fullscreen',True)
        self.root.focus_set()
        self.root.update_idletasks()
        self.root.update()
        
        self.root.geometry("1100x700+30+30")
        global btn
        btn = tki.Button(self.root, text = "Measure!",command = self.measure,bg="coral")
        btn.place(x = 100, y = 650, width = 1160, height = 50)
        
        topLabel = tki.Label(self.root)
        topLabel.configure(font=("Courier",16),text = "Try to place the washers, centered on the beam and starting from the left edge, at the locations shown below. The beam is 10 inches long. You'll receive a score based on how close you get. The lower the score, the better!",wraplength=370,justify="center")
        topLabel.place(x=10,y=30)
        
        global resultLabelBlue
        resultLabelBlue = tki.Label(self.root)
        resultLabelBlue.configure(text = "",wraplength=800,justify="left", font=("Courier",16),fg = 'blue')
        resultLabelBlue.place(x=450,y=500)
        
        global resultLabelGreen
        resultLabelGreen = tki.Label(self.root)
        resultLabelGreen.configure(text = "",wraplength = 800,justify = "left", font = ("Courier",16),fg='green')
        resultLabelGreen.place(x=450,y=540)
        
        global resultLabelWhite
        resultLabelWhite = tki.Label(self.root)
        resultLabelWhite.configure(text = "",wraplength = 800,justify = "left", font = ("Courier",16),fg='black')
        resultLabelWhite.place(x=450,y=580)
        
        global resultLabelRed
        resultLabelRed = tki.Label(self.root)
        resultLabelRed.configure(text = "",wraplength = 800,justify = "left", font = ("Courier",16),fg='red')
        resultLabelRed.place(x=450,y=620)
        
        global firstLabel
        firstLabel = tki.Label(self.root)
        firstLabel.configure(text = "1st: " + str(x1) + " inches", font = ("Courier",16))
        firstLabel.place(x=100,y=300)
        
        global secondLabel
        secondLabel = tki.Label(self.root)
        secondLabel.configure(text = "2nd: " + str(x2) + " inches", font = ("Courier",16))
        secondLabel.place(x=100,y=350)
        
        global thirdLabel
        thirdLabel = tki.Label(self.root)
        thirdLabel.configure(text = "3rd: " + str(x3) + " inches", font = ("Courier",16))
        thirdLabel.place(x=100,y=400)
        
        global scoreLabel
        scoreLabel = tki.Label(self.root)
        scoreLabel.configure(text = "Your Score: ", font = ("Courier",20))
        scoreLabel.place(x=30,y=500)
        
        self.stopEvent = threading.Event()
        self.thread=threading.Thread(target=self.videoLoop,args=())
        self.thread.start()
        
        self.root.wm_title("STEAM App")
        self.root.wm_protocol("WM_DELETE_WINDOW",self.onClose)
        
    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                _,image = self.vs.read() #Pull the image data from the video stream
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) #Convert to RGB format
                if measureBool == True:
                    HSVImg = cv2.cvtColor(image, cv2.COLOR_RGB2HSV) #Convert to HSV for image processing
                    HSVImg = cv2.inRange(HSVImg,(0,0,140),(179,255,255)) #Threshold the image to only detect the gray color of the beam
                    im2, contours, hierarchy = cv2.findContours(HSVImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Detect the contours from the threshold image
                    cnt = sorted(contours, key=cv2.contourArea)
                    tlDistance = 1e6
                    tlPt = tuple([1e6,1e6])
                    
                    blDistance = tlDistance
                    brDistance = tlDistance
                    trDistance = tlDistance
                    blPt = tlPt
                    brPt = tlPt
                    trPt = tlPt
                    height,width,_ = image.shape
                    #Loop through all the detected contours, and measure the distance from the contour point to the edges of the image. 
                    #This will determine the four points that are closest to the four edges of the image (the bounding box points of the beam).
                    for pt in cnt[len(cnt)-1]:
                        ptDistanceTL = cv2.norm(pt - tuple([0,0]))
                        ptDistanceBL = cv2.norm(pt - tuple([0,height]))
                        ptDistanceBR = cv2.norm(pt - tuple([width,height]))
                        ptDistanceTR = cv2.norm(pt - tuple([width,0]))
                        if ptDistanceTL < tlDistance:
                            tlDistance = ptDistanceTL
                            tlPt = tuple(pt[0])
                        if ptDistanceBL < blDistance:
                            blDistance = ptDistanceBL
                            blPt = tuple(pt[0])
                        if ptDistanceBR < brDistance:
                            brDistance = ptDistanceBR
                            brPt = tuple(pt[0])
                        if ptDistanceTR < trDistance:
                            trDistance = ptDistanceTR
                            trPt = tuple(pt[0])
                    #Now that we know the detected corners of the beam, calculate the centerline of the beam.
                    leftMid = tuple([int((tlPt[0] + blPt[0])/2),int((tlPt[1] + blPt[1])/2)])
                    rightMid = tuple([int((trPt[0] + brPt[0])/2),int((trPt[1] + brPt[1])/2)])
                    leftPt = np.array(leftMid)
                    rightPt = np.array(rightMid)
                    xSpan = rightMid[0]-leftMid[0]
                    ySpan = rightMid[1] - leftMid[1]                  
                    
                    HSVCircle = cv2.cvtColor(image, cv2.COLOR_RGB2HSV) #Copy the original stored image into a new HSV image for detecting the washer locations
                    HSVCircle = cv2.inRange(HSVCircle,(0,120,60),(179,255,255)) #Threshold the image looking for the red color of the washers
                    im2,contours,hierarch = cv2.findContours(HSVCircle,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #Find the contours of the threshold image
                    cnt = sorted(contours, key=cv2.contourArea)
                    cPts = [] #Array used to store unique points for the detected washers
                    if cnt is not None:
                        for c in cnt:
                            M = cv2.moments(c)
                            if M["m00"] != 0: #Find the moments of the contour
                                cX = int(M["m10"]/M["m00"]) #Determine the x-coordinate of the centroid from the contour moment
                                cY = int(M["m01"]/M["m00"]) #Determine the y-coordinate of the centroid from the contour moment
                                if(len(cPts)==0): #If the array of unique points is empty, then the first point has to be unique, so add it.
                                    cPts.append(tuple([cX,cY]))
                                else: #For all other points after the first one.
                                    uniquePt = True #Assume the point will be unique
                                    for cPtUnique in cPts: #Check uniqueness of current point against all previous points
                                        if abs(cX-cPtUnique[0]) < 10: #If x-coordinate is within 10 pixels of any previous point
                                            uniquePt = False #It is not unique
                                    if uniquePt: #Otherwise, it is unique, so add it to the array
                                        cPts.append(tuple([cX,cY]))
                            else:
                                cX,cY = 0,0
                            cv2.circle(image,(cX,cY),1,(255,255,255),-1) #Draw a dot at the detected center of the washers
                    
                    #Draw circles at the four corners of the beam
                    cv2.circle(image, tlPt,5,(0,0,255),thickness = 2)
                    cv2.circle(image,blPt,5,(0,0,255),thickness =2)
                    cv2.circle(image,brPt,5,(0,0,255),thickness=2)
                    cv2.circle(image,trPt,5,(0,0,255),thickness=2)
                    #Draw circles at the leftmost and rightmost points of the centerline, and draw a line down the centerline of the beam
                    cv2.circle(image,leftMid,5,(0,255,0),thickness = 2)
                    cv2.circle(image,rightMid,5,(0,255,0),thickness = 2)
                    cv2.line(image,leftMid,rightMid,(0,255,0),1)
                    
                    #Given that the beam is 10" long, use the detected length of the beam (in pixels) to determine where the nominal washer centers
                    #should be drawn
                    x1Pt = tuple([int((x1/10)*xSpan)+leftMid[0],int((x1/10)*ySpan) + leftMid[1]])
                    x2Pt = tuple([int((x2/10)*xSpan)+leftMid[0],int((x2/10)*ySpan) + leftMid[1]])
                    x3Pt = tuple([int((x3/10)*xSpan)+leftMid[0],int((x3/10)*ySpan) + leftMid[1]])
                    cv2.circle(image,x1Pt,1,(255,0,0),3)
                    cv2.circle(image,x2Pt,1,(255,0,0),3)
                    cv2.circle(image,x3Pt,1,(255,0,0),3)
                    
                    cPts = sorted(cPts,key=lambda k: [k[0],k[1]])
                    sumDistance = 0
                    desiredPts = [x1Pt,x2Pt,x3Pt]
                    if len(cPts)==3: #If three washers were correctly detected, loop through them and determine how far each was off from nominal
                        for i in range(0,3):
                            array1 = np.array([desiredPts[i][0],desiredPts[i][1]])
                            array2 = np.array([cPts[i][0],cPts[i][1]])
                            sumDistance = sumDistance + abs(np.linalg.norm(array1 - array2)) #Sum each of the three distances together
                    if len(yourScore)<10:
                        yourScore.append(sumDistance)
                    else:
                        global scoreLabel,btn,resultLabelBlue,resultLabelGreen,resultLabelWhite,resultLabelRed
                        scoreAverage = round(sum(yourScore)/len(yourScore),2)
                        scoreText = ""
                        if scoreAverage == 0:
                            scoreText = "Error"
                        else:
                            scoreText = str(scoreAverage)
                        scoreLabel.configure(text="Your Score: " + scoreText + "!")
                        btn.configure(text = "Try Again")
                        resultLabelBlue.configure(text = "Blue Circles: Detected Corners of the Beam Section.",wraplength=800,justify="left", font=("Courier",16))
                        resultLabelGreen.configure(text = "Green Circles and Line: Centerline of the Beam.",wraplength=800,justify="left", font=("Courier",16))
                        resultLabelWhite.configure(text = "White Dot: Center of the Washer.",wraplength=800,justify="left", font=("Courier",16))
                        resultLabelRed.configure(text = "Red Dot: Desired Location of Washer Center.",wraplength=800,justify="left", font=("Courier",16))
                #end of measureBool == True section
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)
                
                if self.panel is None:
                    self.panel = tki.Label(image = image)
                    self.panel.image = image
                    self.panel.place(x=400,y=10)
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
                    
        except RuntimeError:
            print("[INFO] caught a RuntimeError")
    
    def measure(self):
        global measureBool,x1Values,x2Values,x3Values,x1,x2,x3,yourScore,btn,scoreLabel,resultLabelBlue,resultLabelGreen,resultLabelWhite,resultLabelRed
        if measureBool == True:
            scoreLabel.configure(text = "Your Score: ")
            btn.configure(text = "Measure!")
            resultLabelBlue.configure(text = "")
            resultLabelGreen.configure(text = "")
            resultLabelWhite.configure(text = "")
            resultLabelRed.configure(text = "")
            x1 = x1Values[int(random()*5)]
            x2 = x2Values[int(random()*5)]
            x3 = x3Values[int(random()*5)]
            firstLabel.configure(text = "1st: " + str(x1) + " inches")
            secondLabel.configure(text = "2nd: " + str(x2) + " inches")
            thirdLabel.configure(text = "3rd: " + str(x3) + " inches")
            yourScore = []
        else:
            btn.configure(text = "Averaging...")
        measureBool = not measureBool

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()
        
