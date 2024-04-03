""" Remove initial file if file has a _local copy """
import sys
import os
import glob

DRYRUN = False


def tidy(folder):
    """Remove initial file if file has a _local copy"""

    # folder is the name of the folder in which we
    # have to perform the delete operation
    # changing the current working directory
    # to the folder specified

    try:
        os.chdir(os.path.join(os.getcwd(), folder))
    except Exception as err:
        print(err)
        sys.exit()

    # Only interested in these. Which limits the damage from
    # any accidental deletion

    imgnames = sorted(glob.glob("2*.jpg"))

    local = [x for x in imgnames if "_local" in x]
    original_names = [x.replace("_local", "") for x in local]

    # we have an original copy and a one labeled local. only need one

    both_local_and_non_local = set(original_names) & set(imgnames)

    for item in both_local_and_non_local:
        command = "sudo rm -f " + item
        # command = "ls " + item
        print(command)
        os.system(command)


if __name__ == "__main__":
    runfile = sys.argv.pop(0)
    inputargs = sys.argv

    if len(inputargs) != 1:
        print("Incorrect usage! Should be : <path>/tidy <directory>")
        sys.exit()

    print("Remove duplicates of _local and non-local images ")

    tidy(inputargs[0])

    sys.exit()
