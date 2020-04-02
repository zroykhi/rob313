import numpy as np
import cv2


#cap = cv2.VideoCapture('../Sequences/Antoine_Mug.mp4')
cap = cv2.VideoCapture('../Sequences/VOT-Ball.mp4')

cpt = 1
while(1):
    ret ,frame = cap.read()
    if ret == True:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Calculate gradient
        grad_x = cv2.Sobel(frame_gray, cv2.CV_32F, 1, 0)
        grad_y = cv2.Sobel(frame_gray, cv2.CV_32F, 0, 1)
        # Calculate orientations (result between -pi and +pi)
        orientation = np.arctan2(grad_x, grad_y)
        # Normalise the orientations between 0 and 1
        orientation = (orientation + np.pi) / (2 * np.pi)
        cv2.imshow('Orientation', orientation)
        # Calculate gradient norm
        norm = np.sqrt(grad_x**2 + grad_y**2)
        # Normalise the norm between 0 and 1
        cv2.imshow('Norm', norm / norm.max())
        # Set the threshold to quantile 80%
        threshold = np.quantile(norm, 0.8)
        # Convert to colour for displaying mask
        orient_mask = cv2.cvtColor(orientation, cv2.COLOR_GRAY2BGR)
        orient_mask[np.where(norm < threshold)] = [0,0,1]
        cv2.imshow('Significant Orientations', orient_mask)
        
        k = cv2.waitKey(60) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('Orientation_%04d.png'%cpt,255*orientation)
            cv2.imwrite('Norm_%04d.png'%cpt,norm)
            cv2.imwrite('Masked_Orientation_%04d.png'%cpt,255*orient_mask)
        cpt += 1
    else:
        break

cv2.destroyAllWindows()
cap.release()
