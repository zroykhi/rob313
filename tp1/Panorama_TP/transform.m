% Q1
imrgb = double(imread('Pompei.jpg'))/255;
imagesc(imrgb);

PtO = [142.44, 44.894, 1; 356.15, 45.761, 1; 111.86, 253.53, 1;370.59, 260.03, 1]'
PtD = [120, 20, 1; 320, 20, 1; 120, 320, 1; 320, 320, 1]'
H = homography2d(PtO,PtD);
imagesc(vgg_warp_H(imrgb,H))

% Q2.1
PtO = [404.08, 154.16, 1;424.04, 154.16, 1;404.08, 186.18, 1;424.04, 186.18, 1]';
PtD = [22.609, 152.03, 1;43.007, 152.03, 1;22.609, 184.82, 1;43.007, 184.82, 1]';
H1 = homography2d(PtO,PtD);
% bbox = [-1000 500 -100 500];
bbox = [-1500 500 -100 500];
img = double(imread('Amst-2.jpg'))/255;
ima=vgg_warp_H(img,H1,'linear',bbox);
imagesc(ima);
H2 = eye(3);
img = double(imread('Amst-3.jpg'))/255;
imb=vgg_warp_H(img,H2,'linear',bbox);
imagesc(imb);
im_fused = max(ima,imb); % find new coodinate of Amst-2 as PtD
imagesc(im_fused);

% Q2.2
img3 = double(imread('Amst-1.jpg'))/255;
% PtO = [472.18, 135.74, 1;486.42, 139.97, 1;472.18, 146.31, 1;486.42, 149.13, 1]';
% PtD = [151.51, 136.34, 1;165.96, 141.96, 1;151.51, 146.46, 1;165.96, 149.83, 1]';
% PtD = [651.51, 236.34, 1;665.96, 241.96, 1;651.51, 246.46, 1;665.96, 249.83, 1]'; % coodinate in im_fused

PtO = [472.18, 135.74, 1;486.42, 139.97, 1;465.74, 247.23, 1;496.36, 247.92, 1]';
PtD = [151.51, 136.34, 1;165.96, 141.96, 1;141.29, 250.84, 1;172.31, 248.33, 1]';
% PtD = [1151.51, 236.34, 1;1165.96, 241.96, 1;1141.29, 350.84, 1;1172.31, 348.33, 1]'; % coodinate in im_fused
% PtD = [651.51, 236.34, 1;665.96, 241.96, 1;641.29, 350.84, 1;672.31, 348.33, 1]'; % coodinate in im_fused
H3 = homography2d(PtO,PtD);
% bbox1 = [-500 1000 -100 500];
bbox1 = [-1000 1000 -100 500];
imc=vgg_warp_H(img3,H3,'linear',bbox1);
imagesc(imc);
im_final = max(imc, im_fused)
imagesc(im_final)