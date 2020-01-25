import numpy as np
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from matplotlib.pyplot import imread
from scipy.ndimage.filters import sobel

roi_defined = False

# Good for the b/w test images used
MIN_CANNY_THRESHOLD = 10
MAX_CANNY_THRESHOLD = 50
	
def gradient_orientation(image):
	'''
	Calculate the gradient orientation for edge point in the image
	'''
	dx = sobel(image, axis=0, mode='constant')
	dy = sobel(image, axis=1, mode='constant')
	gradient = np.arctan2(dy,dx) * 180 / np.pi
	
	return gradient
	
def build_r_table(image, origin):
	'''
	Build the R-table from the given shape image and a reference point
	'''
	edges = cv2.Canny(image, MIN_CANNY_THRESHOLD,
				  MAX_CANNY_THRESHOLD)
	gradient = gradient_orientation(edges)
	
	r_table = defaultdict(list)
	for (i,j),value in np.ndenumerate(edges):
		if value:
			r_table[gradient[i,j]].append((origin[0]-i, origin[1]-j))

	return r_table

def accumulate_gradients(r_table, grayImage):
	'''
	Perform a General Hough Transform with the given image and R-table
	'''
	edges = cv2.Canny(grayImage, MIN_CANNY_THRESHOLD, 
				  MAX_CANNY_THRESHOLD)
	gradient = gradient_orientation(edges)
	
	accumulator = np.zeros(grayImage.shape)
	for (i,j),value in np.ndenumerate(edges):
		if value:
			for r in r_table[gradient[i,j]]:
				accum_i, accum_j = i+r[0], j+r[1]
				if accum_i < accumulator.shape[0] and accum_j < accumulator.shape[1]:
					accumulator[int(accum_i), int(accum_j)] += 1
					
	return accumulator

def n_max(a, n):
	'''
	Return the N max elements and indices in a
	'''
	indices = a.ravel().argsort()[-n:]
	indices = (np.unravel_index(i, a.shape) for i in indices)
	return [(a[i], i) for i in indices]

def define_ROI(event, x, y, flags, param):
	global r,c,w,h,roi_defined
	# if the left mouse button was clicked, 
	# record the starting ROI coordinates 
	if event == cv2.EVENT_LBUTTONDOWN:
		r, c = x, y
		roi_defined = False
	# if the left mouse button was released,
	# record the ROI coordinates and dimensions
	elif event == cv2.EVENT_LBUTTONUP:
		r2, c2 = x, y
		h = abs(r2-r)
		w = abs(c2-c)
		r = min(r,r2)
		c = min(c,c2)  
		roi_defined = True

cap = cv2.VideoCapture('./data/video/Antoine_Mug.mp4')

# take first frame of the video
ret,frame = cap.read()
# load the image, clone it, and setup the mouse callback function
clone = frame.copy()
cv2.namedWindow("First image")
cv2.setMouseCallback("First image", define_ROI)
 
# keep looping until the 'q' key is pressed
while True:
	# display the image and wait for a keypress
	cv2.imshow("First image", frame)
	key = cv2.waitKey(1) & 0xFF
	# if the ROI is defined, draw it!
	if (roi_defined):
		# draw a green rectangle around the region of interest
		cv2.rectangle(frame, (r, c), (r+h, c+w), (0, 255, 0), 2)
	# else reset the image...
	else:
		frame = clone.copy()
	# if the 'q' key is pressed, break from the loop
	if key == ord("q"):
		break
 
track_window = (r,c,h,w)
# set up the ROI for tracking
roi = frame[c:c+w, r:r+h]

# Setup the termination criteria: either 10 iterations,
# or move by less than 1 pixel
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

cpt = 1
reference_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
referencePoint = (reference_image.shape[0]/2, reference_image.shape[1]/2)
r_table = build_r_table(reference_image, referencePoint)    
while(1):
	ret ,frame = cap.read()
	if ret == True:
		gray_query_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		accumulator = accumulate_gradients(r_table, gray_query_img)
		# Q4 
		m = n_max(accumulator, 1)
		# print(m)
		# print(accumulator)
		y_point = [pt[1][0] for pt in m][0]
		x_point = [pt[1][1] for pt in m][0]
		# print("max voting is: ", accumulator.max())
		# frame_tracked = cv2.rectangle(frame, (int(x_point-h/2),int(y_point-w/2)), (int(x_point+h/2),int(y_point+w/2)), (255,0,0) ,2)

		# Q5  
		ret, track_window = cv2.meanShift(accumulator, track_window, term_crit)
		x,y,h,w = track_window
		frame_tracked = cv2.rectangle(frame, (x,y), (x+h,y+w), (255,0,0) ,2)

		cv2.imshow('Sequence',frame_tracked)
		k = cv2.waitKey(60) & 0xff
		if k == 27:
			break
		elif k == ord('s'):
			cv2.imwrite('Frame_%04d.png'%cpt,frame_tracked)
		cpt += 1
	else:
		break

cv2.destroyAllWindows()
cap.release()
