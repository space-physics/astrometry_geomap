function [Xind, Yind, RAdeg, DECdeg ] = modifyFITSheaderAstrometry(WCSfn,xPix,yPix,debugp)
% used with Astrometry.net program to make a FITS file with the desired data
% inputs: 
% -------
% WCSfn: the .wcs file astrometry solve-field makes
% xPix: number of pixels in x-dimension
% yPix: number of pixels in y-dimension
% debugp: print verbose messages
% 
% Michael Hirsch
% GPL v3+ license
%
% example:
% modifyFITSheaderAstrometry('../Meteor/HST1_1secNoEM.wcs',512,512)
% modifyFITSheaderAstrometry('../Meteor/HST2_1secNoEM.wcs',512,512)
%------------
if nargin<4, debugp = false; end
binpath = '/usr/bin/'
%% setup filenames
[dataDir,fnStem] = fileparts(WCSfn);
if strcmp(dataDir(1),'~')
    dataDir = [getenv('HOME'),dataDir(2:end)];
end
XYfn = [dataDir,'/',fnStem,'.CamXY'];
OutFN = [dataDir,'/',fnStem,'.CamRaDec'];

if strcmp(WCSfn(1),'~') %replace tilde if present 
  WCSfn = [getenv('HOME'),WCSfn(2:end)];
end %if

if exist(XYfn,'file')
    newCamXY = tempname;
    display(['Moving existing ',XYfn,' to ',newCamXY])
    movefile(XYfn,newCamXY);
end
%% setup the FITS table
import matlab.io.*
FPTR = fits.createFile(XYfn);
TBLTYPE = 'binary';
NROWS = 0; 

TTYPE = {'X',   'Y'};
TFORM = {'1D','1D'}; %using double precision float for coordinates
TUNIT = {'pixel','pixel'};

fits.createTbl(FPTR,TBLTYPE,NROWS,TTYPE,TFORM,TUNIT,'Image plane x-y coordinates');
%% create data to write to table
% we're going to put in all possible x-y coordinates
[xData,yData] = meshgrid(1:1:xPix,1:1:yPix); 

%to save time verifying program behavior, for a first pass I'm going to reshape
%everything into columns -- sorry if that's annoying ...
xData = xData(:);
yData = yData(:);
%% insert data into FITS table
% 1,1 means write into column 1, STARTING at row 1.
fits.writeCol(FPTR,1,1,xData);

% 2,1 means write into column 2, STARTING at row 1.
fits.writeCol(FPTR,2,1,yData);

%% write FITS to file
fits.closeFile(FPTR);

%% get RA/DEC from Astrometry.net
ucmd = [binpath,'wcs-xy2rd -w ',WCSfn,' -i ',XYfn,' -o ',OutFN,' -X X -Y Y -v'];
display(ucmd)
[uerr,umsg] = unix(ucmd);
if uerr, 
    display(umsg)
    error('problem with wcs-xy2rd  -- does "which wcs-xy2rd" return anything?'), 
end

%% test reading table
if debugp
    fitsdisp(XYfn) %get the header
end

XYind = cell2mat(fitsread(XYfn,'binarytable')); %get the data
Xind = XYind(:,1);
Yind = XYind(:,2);

RADECdeg = cell2mat(fitsread(OutFN,'binarytable')); %get the data
RAdeg = RADECdeg(:,1);
DECdeg = RADECdeg(:,2);

%cleanup
if nargout==0, clear, end
end 
