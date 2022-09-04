import subprocess
import shlex
import sys
import os
import argparse


def sbatch_str_gen():
    '''
    Create the sbatch file data before file generating
    :return: Lines as string to save in sbach file
    '''

    ret = []
    ret.append("#!/bin/bash\n")
    ret.append("#SBATCH -n 1 -N 1 --exclusive -p mixedp\n")
    ret.append("module swap gnu8 intel/18.0.1.163")
    ret.append("module swap openmpi3 openmpi/4.1.3-intel")
    ret.append("ml openmpi/4.1.3-intel")
    ret.append("ml dmtcp/v2.6-intel18")
    ret.append("export OMP_NUM_THREADS=16\n")
    return '\n'.join(ret)


def write_sbatch_file(fname, data):
    '''
    Save the sbatch file
    :param fname: sbatch file name
    :param data: lines as string to save
    :return: None
    '''

    with open(fname, "w") as fn:
        fn.write(data)


def generate_dmtcp_cmd(app_name, compress="True", interval=10, overwrite="True", rollback=1):
    '''
    Generating the dmtcp command line
    :param compress: False - No compression; True - Use compression
    :param interval: int as time interval between savings
    :param overwrite: False - Don't overwrite last checkpoint; True - Overwrite last checkpoint
    :param rollback: int parameter for how many chekpoints to save
    :return: None, saving the full sbatch with config
    '''

    print("app name" + app_name + " compress=" + str(compress) + " interval=" + str(interval) + " overwrite=" + str(
        overwrite) + " rollback=" + str(rollback))
    dmtcp_cmd = ["dmtcp_launch"]
    if compress == "True":
        dmtcp_cmd.append("--gzip")
    if interval != "None":
        dmtcp_cmd.append("-i " + str(interval))
    if overwrite == "True":
        dmtcp_cmd.append("--allow-file-overwrite")
    # if rollback != 1:
    # dmtcp_cmd.append("rollback=" + str(rollback))
    # TODO: Fix the rollback command
    dmtcp_cmd.append("mpirun -n 1 /home/gabid/LULESH/build/" + app_name + " -i 50 -s 200")
    # TODO: Add app and mpirun params
    last_cmd = " ".join(dmtcp_cmd) + "\n"
    print("Writing sbatch_test.sh")
    write_sbatch_file("sbatch_test.sh", sbatch_str_gen() + last_cmd)


def start_job(app_name):
    '''
    Start new job with dmtcp wrapper
    :return:
    '''

    command = "echo $PWD ; ml dmtcp/v2.6-intel-impi ; sbatch sbatch_test.sh"
    ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())
    print("Starting job: " + (ret.stdout.decode().split(' '))[-1]) # extracting the job #


def restart_job(job_num):
    '''
    Restart last stopped job
    #TODO: check if the job num is necessary (in case of many jobs running by same user)
    :param job_num:
    :return:
    '''
    # using sbatch shell file restart to run the last check point
    command = "sbatch_slurm_restart.sh"
    ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())
    print("Restarting job: " + (ret.stdout.decode().split(' '))[-1])
    print("Restarting Job: " + str(job_num))


def stop_job(job_num):
    # using scancel to stop the job
    # TODO: validate checkpoint created
    # subprocess.run()
    print("Stopping job: " + str(job_num))
    command = "scancel " + job_num
    ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())


if __name__ == '__main__':
    os.chdir("/home/gabid/LULESH/build")
    # for help --help
    parser = argparse.ArgumentParser(description='Running DMTCP')
    # DMTCP commands
    parser.add_argument('--compress', help='Compress checkpoint file False - No compression ; True - Do compression')
    parser.add_argument('--rollback', help='# of rollback check points')
    parser.add_argument('--overwrite',
                        help='False - Do not overwrite last checkpoint ; True - overwriting in cycle last checkpoint')
    parser.add_argument('--interval', help='# of seconds to create checkpoint')
    parser.add_argument('--start', help='App name to run')
    parser.add_argument('--stop', help='Stop job #')
    parser.add_argument('--restart', help='Restart job #')

    # Get arguments from the user
    args = parser.parse_args()

    if args.start:
        generate_dmtcp_cmd(args.start, args.compress, args.interval if args.interval is not None else 10,
                           args.overwrite,
                           args.rollback)
        start_job(args.start)

    elif args.stop:
        stop_job(args.stop)

    elif args.restart:
        restart_job(args.restart)
    #
    # elif args.compress:
    #     restart_job(args.restart)
    #
    # elif args.rollback:
    #     restart_job(args.restart)
    #
    # elif args.overwrite:
    #     restart_job(args.restart)
    #
    # elif args.interval:
    #     restart_job(args.restart)
