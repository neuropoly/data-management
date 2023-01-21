# INSPIRED

This is an MRI dataset acquired in the context of the INSPIRED project.

It contains brain and spinal cord data acquired at two sites centers (Toronto, Zurich) from healthy controls (HC) and two pathologies:
- degenerative cervical myelopathy (DCM)
- spinal cord injury (SCI)

It also contains spinal cord segmentation for T2w axial images and gray matter and white matter segmentations for T2star images.

## Dataset structure

Spinal cord MRI data:
- T1w
- T2w axial
- T2w sagittal
- T2star
- DWI (A-P and P-A phase encoding)

Brain MRI data:
- MPM (multi-parameter mapping)
- DWI (A-P and P-A phase encoding)

## Naming convention

sub-<site><pathology>XXX

Note: BIDS label `acq-cspine` is used to differentiate spine images from brain. For details, see https://github.com/neuropoly/data-management/pull/185#issuecomment-1362069079.

Note: 01 corresponds to Toronto site, 02 to Zurich site. For details, see https://github.com/neuropoly/data-management/issues/184#issuecomment-1329250514.

## Details

https://www.spinalsurgerynews.com/2016/10/inspired-spinal-cord-neuro-imaging-project/14594