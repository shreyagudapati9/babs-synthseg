
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
        help='If present, T1w scans will be processed. If not present, T1w scans will not be processed.', action='store_true')

    parser.add_argument(
        '--t2w',
        help='If present, T2w scans will be processed. If not present, T2w scans will not be processed.', action='store_true')

    parser.add_argument(
        '--flair',
        help='If present, FLAIR scans will be processed. If not present, FLAIR scans will not be processed.', action='store_true')

    parser.add_argument(
        '--mprage',
        help='If present, MPRAGE scans will be processed. If not present, MPRAGE scans will not be processed.', action='store_true')

    return parser

def run_robust_synthseg(scan, inFn, out_robust, volscsv, qccsv, postfn):
    print()
    print()
    print("===== Running SynthSeg (Robust) on : ", scan, " =====")

    out_dir = op.join(out_robust, scan.split(".nii")[0])
    volscsv = op.join(out_dir, volscsv)
    qccsv = op.join(out_dir, qccsv)
    postfn = op.join(out_dir, postfn)
    result = subprocess.run(["mri_synthseg", "--i", inFn, "--o", out_dir, "--vol", volscsv, "--qc", qccsv, "--post", postfn, "--robust", "--parc"])

    return result

def run_notrobust_synthseg(scan, inFn, out_notrobust, volscsv, qccsv, postfn):

    print()
    print()
    print("===== Running SynthSeg (Not Robust) on : ", scan, " =====")

    out_dir = op.join(out_notrobust, scan.split(".nii")[0])
    volscsv = op.join(out_dir, volscsv)
    qccsv = op.join(out_dir, qccsv)
    postfn = op.join(out_dir, postfn)
    result = subprocess.run(["mri_synthseg", "--i", inFn, "--o", out_dir, "--vol", volscsv, "--qc", qccsv, "--post", postfn, "--parc"])

    return result

def get_fs_version():

    output = subprocess.check_output(['recon-all', '-version']).decode('utf-8')
    version = output.split("-")[-3]
    return version

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
    if args.t1w is True:
        types_to_process.append("T1w")
    if args.t2w is True:
        types_to_process.append("T2w")
    if args.flair is True:
        types_to_process.append("FLAIR")
    if args.mprage is True:
        types_to_process.append("MPRAGE")

    if len(types_to_process)==0:
        print("Please specify the type of scans you would like to process (--t1w, --t2w, --flair or --mprage) and try again.")
        exit(1)

    fs_version = get_fs_version()
    # Synthseg robust directory
    robust_dir = "synthseg_fs"+get_fs_version()+"_parc_robust"
    out_robust = op.join(args.output_dir, robust_dir)
    if op.exists(out_robust) is False:
        os.makedirs(out_robust)

    # Synthseg not robust directory
    notrobust_dir = "synthseg_fs"+get_fs_version()+"_parc_notrobust"
    out_notrobust = op.join(args.output_dir, notrobust_dir)
    if op.exists(out_notrobust) is False:
        os.makedirs(out_notrobust)

    for ses in sessions :
        sesPath = op.join(dir_4analysis, ses)
        if "anat" in os.listdir(sesPath):
            anatPath = op.join(sesPath, "anat")
            # Get only the scans we wish to process
            scans = [fn for fn in os.listdir(anatPath) if (any(x.lower() in fn.lower() for x in types_to_process) and (".nii" in fn or ".nii.gz" in fn))]
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
            print()
            print()

            # Not robust synthseg
            result_notrobust = run_notrobust_synthseg(scan, scanPath, out_notrobust, volscsv, qccsv, postfn)
            if result_notrobust.returncode!=0 :
                print("SynthSeg Non-Robust did not run for scan : ", scan)
            print()
            print()


if __name__ == "__main__":
    main()
