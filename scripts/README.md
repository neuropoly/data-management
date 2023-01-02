# GmSegChallenge2016

This is an MRI dataset acquired in the context of the GmSegChallenge2016 project.

It contains data of healthy spinal cords acquired at 4 different sites (University College London (UCL), Ecole Polytechnique de Montreal (EPM), Vanderbilt University (VDB), and University Hospital Zurich (UHZ)).

Data have been split into two sets (training and testing) of 40 images each, with 10 images from each site.
The training dataset contains manual segmentation of SC, WM, and GM from four expert raters located under the derivatives folder.
Note: The originally provided manual labels contained WM (pixel value 2) and GM (pixel value 1) segmentations within a single NIfTI image. To allow easier DL model training, three separate segmentations (SC, WM, and GM) were re-created. For details, see the curation script located under the /code folder.

## Contact Person

Dataset shared by: <NAME AND EMAIL>
<IF THERE WAS EMAIL COMM>Email communication: <DATE OF EMAIL AND SUBJECT>

Details:
 - Prados et al., 2017: https://www.sciencedirect.com/science/article/pii/S1053811917302185
 - http://niftyweb.cs.ucl.ac.uk/program.php?p=CHALLENGE
