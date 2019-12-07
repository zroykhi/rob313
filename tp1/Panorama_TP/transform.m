imrgb = double(imread('Pompei.jpg'))/255;
imagesc(imrgb);

PtO = [142.44, 44.894, 1; 356.15, 45.761, 1; 111.86, 253.53, 1;370.59, 260.03, 1]'
PtD = [120, 20, 1; 320, 20, 1; 120, 320, 1; 320, 320, 1]'
H = homography2d(PtO,PtD);
imagesc(vgg_warp_H(imrgb,H))


PtO = [404, 153.67, 1;423.39, 153.57, 1;404.54, 185.37, 1;423.93, 185.37, 1]';
PtD = [22.609, 152.03, 1;43.007, 152.03, 1;22.232, 184.82, 1;43.584, 184.82, 1]';
H1 = homography2d(PtO,PtD);
bbox = [-1000 500 1 500];
img = double(imread('Amst-2.jpg'))/255;
ima=vgg_warp_H(img,H1,'linear',bbox);
imagesc(ima);

H2 = eye(3);
bbox = [-1000 500 1 500];
img = double(imread('Amst-3.jpg'))/255;
imb=vgg_warp_H(img,H2,'linear',bbox);
imagesc(imb);


im_fused = max(ima,imb);
imagesc(im_fused);