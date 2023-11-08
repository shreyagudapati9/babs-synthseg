
# SynthSeg Image for BABS

## Input : BIDS directory

  Structure : 
  - sub-01
    - ses-01
      - anat
        - sub-01_ses-01_run-01_T1w.nii.gz
        - sub-01_ses-01_run-01_T2w.nii.gz
        - sub-01_ses-01_run-01_FLAIR.nii.gz
   - sub-02
     - ses-01
       - anat
         - sub-02_ses-01_run-01_T1w.nii.gz
   - sub-03
     - ses-01
       - anat


## Output : 

- Derivatives
  - synthseg_fs7.4.1_parc_robust
    -
    -
    -
  - synthseg_fs7.4.1_parc_notrobust
    -
    -
    -

## Commands to run synthseg :  

**synthseg_fs7.4.1_parc_robust** : `mri_synthseg --i <input> --o <output> --vol <vol> --qc <qc> --post <post> --robust --parc`  

**synthseg_fs7.4.1_parc_notrobust** : `mri_synthseg --i <input> --o <output> --vol <vol> --qc <qc> --post <post> --parc`
