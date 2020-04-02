import numpy as np
import cv2

roi_defined = False


def define_ROI(event, x, y, flags, param):
    global r, c, w, h, roi_defined
    # if the left mouse button was clicked,
    # record the starting ROI coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        r, c = x, y
        roi_defined = False
    # if the left mouse button was released,
    # record the ROI coordinates and dimensions
    elif event == cv2.EVENT_LBUTTONUP:
        r2, c2 = x, y
        h = abs(r2 - r)
        w = abs(c2 - c)
        r = min(r, r2)
        c = min(c, c2)
        roi_defined = True


def gradient(image):
    dx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    dy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    # Argument is normalised between 0 and 1
    arg = (np.arctan2(dy, dx) + np.pi)/(2*np.pi)
    module = np.sqrt(dx ** 2 + dy ** 2)
    return arg, module


def create_r_table(roi, track_window):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    r, c, h, w = track_window
    centre = (int(w / 2), int(h / 2))

    arg, grad_module = gradient(gray)
    # Only consider the pixels from the top 20% gradient magnitude
    mask_grad = cv2.inRange(grad_module, np.quantile(grad_module, 0.8), grad_module.max())    
    # 180 labels in the R-table (i.e. 1 bin corresponds to 2°)
    r_table = []
    for i in range(180):
        r_table.append([])
    for (i, j), value in np.ndenumerate(mask_grad):
        if value:
            index = int(arg[i, j]*179)
            r_table[index].append((centre[0] - i, centre[1] - j))

    return r_table


def Hough(r_table, image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    arg, grad_module = gradient(gray)
    mask_grad = cv2.inRange(grad_module, np.quantile(grad_module, 0.8), grad_module.max())    

    accumulator = np.zeros(gray.shape)
    for (i, j), value in np.ndenumerate(mask_grad):
        if value:
            for r in r_table[int(arg[i, j]*179)]:
                accum_i, accum_j = i + r[0], j + r[1]
                if accum_i < accumulator.shape[0] and accum_j < accumulator.shape[1] and accum_i >= 0 and accum_j >= 0:
                    accumulator[accum_i, accum_j] += 1

    return accumulator


cap = cv2.VideoCapture('../Sequences/Antoine_Mug.mp4')

# take first frame of the video
ret, frame = cap.read()
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
        cv2.rectangle(frame, (r, c), (r + h, c + w), (0, 255, 0), 2)
    # else reset the image...
    else:
        frame = clone.copy()
    # if the 'q' key is pressed, break from the loop
    if key == ord("q"):
        break

track_window = (r, c, h, w)
# set up the ROI for tracking
roi = frame[c:c + w, r:r + h]
# get r-table
r_table = create_r_table(roi, track_window)

cpt = 1
while (1):
    ret, frame = cap.read()
    if ret == True:
        grad_arg, grad_module = gradient(frame)
        accumulator = Hough(r_table, frame)
        ind = np.unravel_index(np.argmax(accumulator, axis=None), accumulator.shape)
        r, c = ind[1], ind[0]
        frame_tracked = cv2.rectangle(frame, (r - h // 2, c - w // 2), (r + h // 2, c + w // 2), (255, 0, 0), 2)
        cv2.imshow('Sequence', frame_tracked)
        accumulator = accumulator/accumulator.max()
        cv2.imshow('Hough Transform', accumulator)

        # Save images
        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('Hough_%04d.png' % cpt, 255*accumulator)
            cv2.imwrite('Frame_%04d.png' % cpt, frame_tracked)
        cpt += 1
    else:
        break

cv2.destroyAllWindows()
cap.release()
