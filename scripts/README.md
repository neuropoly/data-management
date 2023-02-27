# dcm-zurich

This is an MRI dataset acquired in the context of the Pro-DCM study at Balgrist University Hospital, Zurich, Switzerland.

It contains spinal cord data from degenerative cervical myelopathy (DCM) subjects.

## Dataset structure

- sagittal T2w
- axial T2w (top FOV)
- axial T2w (bottom FOV)
- sagittal T1w (not presented for all subjects)

Note:
The axial T2w (top FOV) and the axial T2w (bottom FOV) were stitched together to create a full axial T2w image during the BIDS conversion.
The original non-stitched images are available in the `raw` folder.
For details about the stitching, see the curation script  in the `code` folder. 

## Contact Person

Patrick Freund, Balgrist University Hospital, Zurich, Switzerland.

## Missing data

The following subjects have only a single axial T2w image --> no stitching was performed:
sub-349399
sub-351576
sub-352899
sub-616477
sub-633679
sub-635370
sub-652281
sub-700894
sub-713075
sub-766291
sub-780875
sub-784363
sub-785027
sub-785776
sub-793487
sub-793488

The following subjects have no axial T2w at all:
sub-817811
sub-834907