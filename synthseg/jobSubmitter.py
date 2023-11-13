
import argparse
import os
import os.path as op
import subprocess

def cli():
    parser = argparse.ArgumentParser(
        description='SynthSeg BIDS App')
    parser.add_argument(
        'input_dir',
        help='The directory of the (unzipped) input dataset, '
        'or the path to the zipped dataset; '
        'unzipped dataset should be formatted according to the BIDS standard.')

    parser.add_argument(
        'output_dir',
        help='The directory where the output files should be stored')

    parser.add_argument(
        'analysis_level',
        choices=['participant'],
        help='Level of the analysis that will be performed.'
        " Currenlty only 'participant' is allowed.")

    parser.add_argument(
        '--participant_label', '--participant-label',
        help='The label of the participant that should be analyzed. The label'
        ' can either be <sub-xx>, or just <xx> which does not include "sub-".'
        " Currently only one participant label is allowed.",
        required=True)

    parser.add_argument(
        '--t1w',
        help='If 1, T1w scans will be processed. If 0, T1w scans will not be processed.',
        required=True)

    parser.add_argument(
        '--t2w',
        help='If 1, T2w scans will be processed. If 0, T2w scans will not be processed.',
        required=True)

    parser.add_argument(
        '--flair',
        help='If 1, FLAIR scans will be processed. If 0, FLAIR scans will not be processed.',
        required=True)

    return parser

def run_robust_synthseg(scan, inFn, out_robust, volscsv, qccsv, postfn):
    print("===== Running SynthSeg (Robust) on : ", scan, " =====")

    out_dir = op.join(out_robust, scan.split(".nii")[0])
    volscsv = op.join(out_dir, volscsv)
    qccsv = op.join(out_dir, qccsv)
    postfn = op.join(out_dir, postfn)
    result = subprocess.run(["mri_synthseg", "--i", inFn, "--o", out_dir, "--vol", volscsv, "--qc", qccsv, "--post", postfn, "--robust", "--parc"])

    return result

def run_notrobust_synthseg(scan, inFn, out_notrobust, volscsv, qccsv, postfn):
    print("===== Running SynthSeg (Not Robust) on : ", scan, " =====")

    out_dir = op.join(out_notrobust, scan.split(".nii")[0])
    volscsv = op.join(out_dir, volscsv)
    qccsv = op.join(out_dir, qccsv)
    postfn = op.join(out_dir, postfn)
    result = subprocess.run(["mri_synthseg", "--i", inFn, "--o", out_dir, "--vol", volscsv, "--qc", qccsv, "--post", postfn, "--parc"])

    return result

def main():

    args = cli().parse_args()

    # Sanity checks and preparations: --------------------------------------------
    if args.participant_label:
        if "sub-" == args.participant_label[0:4]:
            participant_label = args.participant_label
        else:
            participant_label = "sub-" + args.participant_label

    print("participant: " + participant_label)

    # check and make output dir:
    if op.exists(args.output_dir) is False:
        os.makedirs(args.output_dir)

    dir_4analysis = os.path.join(args.input_dir, participant_label)
    #print(dir_4analysis)
    sessions = [ses for ses in os.listdir(dir_4analysis) if op.isdir(op.join(dir_4analysis,ses))] # Gets sessions
    #print(sessions)

    # Check scans to be processed :
    types_to_process = []
    if str(args.t1w) == '1':
        types_to_process.append("T1w")
    if str(args.t2w) == '1':
        types_to_process.append("T2w")
    if str(args.flair) == '1':
        types_to_process.append("FLAIR")

    # Synthseg robust directory
    out_robust = op.join(args.output_dir, "synthseg_fs7.4.1_parc_robust")
    if op.exists(out_robust) is False:
        os.makedirs(out_robust)

    # Synthseg not robust directory
    out_notrobust = op.join(args.output_dir, "synthseg_fs7.4.1_parc_notrobust")
    if op.exists(out_notrobust) is False:
        os.makedirs(out_notrobust)

    for ses in sessions :
        sesPath = op.join(dir_4analysis, ses)
        if "anat" in os.listdir(sesPath):
            anatPath = op.join(sesPath, "anat")
            # Get only the scans we wish to process
            scans = [fn for fn in os.listdir(anatPath) if (any(x in fn for x in types_to_process) and (".nii" in fn or ".nii.gz" in fn))]
        else :
            continue
        for scan in scans:
            scanPath = op.join(anatPath, scan)
            volscsv = "volumes.csv"
            qccsv = "qc_scores.csv"
            postfn = "posterior_probability_maps.nii.gz"

            # Robust synthseg
            result_robust = run_robust_synthseg(scan, scanPath, out_robust, volscsv, qccsv, postfn)
            if result_robust.returncode!=0 :
                print("SynthSeg Robust did not run for scan : ", scan)

            # Not robust synthseg
            result_notrobust = run_notrobust_synthseg(scan, scanPath, out_notrobust, volscsv, qccsv, postfn)
            if result_notrobust.returncode!=0 :
                print("SynthSeg Non-Robust did not run for scan : ", scan)


if __name__ == "__main__":
    main()
