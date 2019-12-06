% HOMOGRAPHY2D - computes 2D homography
%
% Usage:   H = homography2d(x1, x2)
%          H = homography2d(x)
%
% Arguments:
%          x1  - 3xN set of homogeneous points
%          x2  - 3xN set of homogeneous points such that x1<->x2
%         
%           x  - If a single argument is supplied it is assumed that it
%                is in the form x = [x1; x2]
% Returns:
%          H - the 3x3 homography such that x2 = H*x1
%
% This code follows the normalised direct linear transformation 
% algorithm given by Hartley and Zisserman "Multiple View Geometry in
% Computer Vision" p92.
%

% Peter Kovesi
% School of Computer Science & Software Engineering
% The University of Western Australia
% pk at csse uwa edu au
% http://www.csse.uwa.edu.au/~pk
%
% May 2003  - Original version.
% Feb 2004  - Single argument allowed for to enable use with RANSAC.
% Feb 2005  - SVD changed to 'Economy' decomposition (thanks to Paul O'Leary)

function H = homography2d(varargin)
    
    [x1, x2] = checkargs(varargin(:));

    % Attempt to normalise each set of points so that the origin 
    % is at centroid and mean distance from origin is sqrt(2).
    [x1, T1] = normalise2dpts(x1);
    [x2, T2] = normalise2dpts(x2);
    
    % Note that it may have not been possible to normalise
    % the points if one was at infinity so the following does not
    % assume that scale parameter w = 1.
    
    
    % TODO : Create matrix A
    
    num_points = length(x1);
    A= ones(3*num_points, 9);
    for i=1:num_points
        O = [0 0 0];
        X = x1(:,i)';
        x = x2(1, i), w = x2(3, i), y = x2(2, i);
        A(3*i-2, :) = [O   -w*X   y*X];
        A(3*i-1, :) = [w*X   O   -x*X];
        A(3*i, :)   = [-y*X  x*X    O];
    end
    
    
    
    % TODO : perform SVD
    [U, S, V] = svd(A, 0)
    
    
    % TODO : Extract homography from SVD result

    H = reshape(V(:,9),3,3)';
    
    
    
    % Denormalise
    H = T2\H*T1;
    

%--------------------------------------------------------------------------
% Function to check argument values and set defaults

function [x1, x2] = checkargs(arg);
    
    if length(arg) == 2
	x1 = arg{1};
	x2 = arg{2};
	if ~all(size(x1)==size(x2))
	    error('x1 and x2 must have the same size');
	elseif size(x1,1) ~= 3
	    error('x1 and x2 must be 3xN');
	end
	
    elseif length(arg) == 1
	if size(arg{1},1) ~= 6
	    error('Single argument x must be 6xN');
	else
	    x1 = arg{1}(1:3,:);
	    x2 = arg{1}(4:6,:);
	end
    else
	error('Wrong number of arguments supplied');
    end
    