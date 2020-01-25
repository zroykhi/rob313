import numpy as np
import cv2

roi_defined = False
 
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

cap = cv2.VideoCapture('./data/video/VOT-Woman.mp4')

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
# conversion to Hue-Saturation-Value space
# 0 < H < 180 ; 0 < S < 255 ; 0 < V < 255
hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
# hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
# computation mask of the histogram:
# Pixels with S<60 or V<32 are ignored 
mask = cv2.inRange(hsv_roi, np.array((15.,30.,55.)), np.array((180.,235.,235.)))
# Marginal histogram of the Hue component
# roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
# Q2
roi_hist = cv2.calcHist([hsv_roi],[1],mask,[180],[0,180])
# Histogram values are normalised to [0,255]
cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

# Setup the termination criteria: either 10 iterations,
# or move by less than 1 pixel
term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

cpt = 1
while(1):
	ret ,frame = cap.read()
	if ret == True:
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		# hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		# Backproject the model histogram roi_hist onto the 
		# current image hsv, i.e. dst(x,y) = roi_hist(hsv(0,x,y))
		# dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
		dst = cv2.calcBackProject([hsv],[1],roi_hist,[0,180],1)
		# apply meanshift to dst to get the new location
		ret, track_window = cv2.meanShift(dst, track_window, term_crit)
		# Q2
		cv2.imshow('dst', dst)
		# Draw a blue rectangle on the current image
		x,y,h,w = track_window
		frame_tracked = cv2.rectangle(frame, (x,y), (x+h,y+w), (255,0,0) ,2)
		cv2.imshow('Sequence',frame_tracked)
		# =========
		# ==========
		# Question 3:
		# ==========

		# grey scale
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# 3x3 sobel filters for edge detection
		sobel_x = np.array([[-1, 0, 1],
							[-2, 0, 2],
							[-1, 0, 1]])

		sobel_y = np.array([[-1, -2, -1],
							[0, 0, 0],
							[1, 2, 1]])

		# Filter the blurred grayscale images using filter2D # TODO sobel functions ?
		filtered_x = cv2.filter2D(frame, cv2.CV_32F, sobel_x)
		filtered_y = cv2.filter2D(frame, cv2.CV_32F, sobel_y)

		# Compute the orientation of the image
		orien = cv2.phase(np.array(filtered_x, np.float32),
						  np.array(filtered_y, np.float32),
						  angleInDegrees=True)
		# print("orientation array", orien)
		# item = orien[20]
		# print("shape of item inside orien", item.shape)  # (384,)
		# print("shape of orien", orien.shape)  # (288, 384)

		mag = cv2.magnitude(filtered_x, filtered_y)

		# thresholding of the magnitude values, play with the thresh value adjust it too your liking
		thresh = 50
		_, mask = cv2.threshold(mag, thresh, 255, cv2.THRESH_BINARY)

		image_map = np.zeros((orien.shape[0], orien.shape[1], 3),
							 dtype=np.float32)

		# Define RGB colours
		red = np.array([0, 0, 1])
		cyan = np.array([0, 1, 1])
		green = np.array([0, 1, 0])
		yellow = np.array([1, 1, 0])
		blue = np.array([1, 0, 0])

		# Set colours corresponding to angles
		image_map[(mask == 0)] = red
		image_map[(mask == 255) & (orien < 90)] = blue
		image_map[(mask == 255) & (orien > 90) & (orien < 180)] = cyan
		image_map[(mask == 255) & (orien > 180) & (orien < 270)] = green
		image_map[(mask == 255) & (orien > 270)] = yellow

		cv2.imwrite('color_img.jpg', image_map)
		# cv2.imshow("orientation", image_map)
		# cv2.waitKey(60)
		# input()

		# print("shape image map", image_map.shape)  # (288, 384, 3)
		# print("ROI.shape", roi.shape)  # (49, 101, 3)
		# print("mag.shape", mag.shape)  # (288, 384)

		# ==========
		# ==========
		k = cv2.waitKey(60) & 0xff
		if k == 27:
			break
		elif k == ord('s'):
			cv2.imwrite('Frame_%04d.png'%cpt,frame_tracked)
			cv2.imwrite('Frame_dst_%04d.png'%cpt,dst)
		cpt += 1
	else:
		break

cv2.destroyAllWindows()
cap.release()
