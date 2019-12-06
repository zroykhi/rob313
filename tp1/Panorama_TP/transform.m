imrgb = double(imread('Pompei.jpg'))/255;
imagesc(imrgb);

PtO = [142.44, 44.894, 1; 356.15, 45.761, 1; 111.86, 253.53, 1;370.59, 260.03, 1]'
PtD = [120, 20, 1; 120, 320, 1; 320, 20, 1; 320, 320, 1]'
H = homography2d(PtO,PtD);
imagesc(vgg_warp_H(imrgb,H))