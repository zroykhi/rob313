import cv2
import numpy as np
from matplotlib import pyplot as plt
import random
import math

###### Read images
img1 = cv2.imread('POP01.jpg',0)  #queryimage # left image
img2 = cv2.imread('POP02.jpg',0) #trainimage # right image
#img1 = cv2.imread('DeathStar1.jpg',0)  #queryimage # left image
#img2 = cv2.imread('DeathStar2.jpg',0) #trainimage # right image


###### Detect and match keypoints
kaze = cv2.KAZE_create(upright = False,#Par défaut : false
                      threshold = 0.0012,#Par défaut : 0.001
                      nOctaves = 6,#Par défaut : 4
                      nOctaveLayers = 4,#Par défaut : 4
                      diffusivity = 2)#Par défaut : 2


# find the keypoints and descriptors with KAZE
kp1, des1 = kaze.detectAndCompute(img1,None)
kp2, des2 = kaze.detectAndCompute(img2,None)

print('Nb of keypoints: ' + str(len(kp1)) + ' ' + str(len(kp2)))
#imgd=img1
#imgd = cv2.drawKeypoints(img1, kp1, imgd,-1,flags=4)
#cv2.imshow('Keypoints', imgd)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


# match keypoints using FLANN library
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)

# m_image = np.array([])
# m_image = cv2.drawMatches(
#    img1, kp1,
#    img2, kp2,
#    [match[0] for match in matches],
#    m_image)
# cv2.imshow('Match', m_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

pts1 = []
pts2 = []

# filter matching using threshold and ratio test as per Lowe's paper
for i,(m,n) in enumerate(matches):
    if (m.distance < 0.9) & (m.distance < 0.6*n.distance):
        pts2.append(kp2[m.trainIdx].pt)
        pts1.append(kp1[m.queryIdx].pt)

pts1 = np.float32(pts1)
pts2 = np.float32(pts2)

print('Number of matched points : ' + str(pts1.shape[0]))


##### Definition of some helper functions
def drawlines(img1,img2,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color=tuple(cv2.cvtColor(np.asarray([[[np.random.randint(0,180),255,255]]],dtype=np.uint8),cv2.COLOR_HSV2BGR)[0,0,:].tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,2)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2

def drawFundamental(img1,img2,pts1,pts2,F):
    # Find epilines corresponding to some points in right image (second image) and
    # drawing its lines on left image
    indexes = np.random.randint(0, pts1.shape[0], size=(10))
    indexes=range(pts1.shape[0])
    samplePt1 = pts1[indexes,:]
    samplePt2 = pts2[indexes,:]

    lines1 = cv2.computeCorrespondEpilines(samplePt2.reshape(-1,1,2), 2,F)
    lines1 = lines1.reshape(-1,3)
    img5,img6 = drawlines(img1,img2,lines1,samplePt1,samplePt2)

    # Find epilines corresponding to points in left image (first image) and
    # drawing its lines on right image
    lines2 = cv2.computeCorrespondEpilines(samplePt1.reshape(-1,1,2), 1,F)
    lines2 = lines2.reshape(-1,3)
    img3,img4 = drawlines(img2,img1,lines2,samplePt2,samplePt1)

    plt.figure(figsize=(15, 5))
    plt.subplot(121),plt.imshow(img5)
    plt.subplot(122),plt.imshow(img3)
   
   

###### Compute Fundamental Matrix using OpenCV RANSAC
FRansac, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_RANSAC)
print('Number of RANSAC inliers : ' + str(mask.sum()))

# select inlier points
inlierpts1 = pts1[mask.ravel()==1]
inlierpts2 = pts2[mask.ravel()==1]

# plot epipolar lines
drawFundamental(img1,img2,inlierpts1,inlierpts2,FRansac)




###### Compute Fundamental Matrix using hand-made RANSAC

# TODO
def calcDist(a, b, c, x, y):
    return abs(a*x+b*y+c)/math.sqrt(a*a+b*b)

N = 33
ransac_thredhold = 2
bestF = []
inliersPt1 = []
inliersPt2 = []
for i in range(N):
    # select randomly 7 points from pts1 and pts2
    index = random.sample(range(pts1.shape[0]), 7)
    pts1_tmp = pts1[index]
    pts2_tmp = pts2[index]
    FRansac, mask = cv2.findFundamentalMat(pts1_tmp, pts2_tmp, cv2.FM_7POINT, 1)
    # FRansac, mask = cv2.findFundamentalMat(pts1_tmp, pts2_tmp, cv2.FM_7POINT)
    # select one of the three solutions
    FRansac = FRansac[:3]
    lines2 = cv2.computeCorrespondEpilines(pts1_tmp.reshape(-1,1,2), 1, FRansac)
    lines2 = lines2.reshape(-1,3)  
    # select inlier points
    inliersPt1_tmp = []
    inliersPt2_tmp = []
    index_taken = []
    for l in lines2:
        for i in range(len(pts2)):
            if (calcDist(l[0], l[1], l[2], pts2[i][0], pts2[i][1]) < ransac_thredhold) and \
            i not in index_taken:
                inliersPt1_tmp.append(pts1[i])
                inliersPt2_tmp.append(pts2[i])
                index_taken.append(i)
    if len(inliersPt1_tmp) > len(inliersPt1):
        bestF = FRansac
        inliersPt1 = inliersPt1_tmp
        inliersPt2 = inliersPt2_tmp
        print('num of inliers', len(inliersPt1))

drawFundamental(img1, img2, np.array(inliersPt1), np.array(inliersPt2), bestF)
# drawFundamental(img1, img2, inlierpts1, inlierpts2, bestF)

plt.show()
