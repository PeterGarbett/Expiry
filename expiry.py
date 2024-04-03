#
#
#   Utility to delete time expired and corrupt image files
#   Time is figured out by filename. system timestamps
#   get mangled by scp or someone forgetting the -p option on cp
#   The filename doesn't
#
#   Look to limit directories such as /var/www/html
#   by date.
#

import sys
import os
import glob
import datetime
from PIL import Image 
import tidy

dryRun = False


def txtTimestampToTime(filename):

    # Convert something of the form
    # 2024_03_06_14_24_21_423461_l<junk>.<junk>
    # to datetime object

    try:
        timestamp = filename.replace("_", "-", 2)
        timestamp = timestamp.replace("_", " ", 1)
        timestamp = timestamp.replace("_", ":", 2)
        timestamp = timestamp.replace("_", ".", 1)
        timestamp = timestamp.split("_l")
        timestamp = timestamp[0]

        # the fact that strptime isn't capable of coping
        # directly with the output of datetime now is
        # really poor.

        stampNoMs = timestamp[:-7]
        MicrosecondsTXT = timestamp.split(".")[1]
        MicrosecondsTXT = MicrosecondsTXT.split("_")[0]
        MicrosecondsTXT = MicrosecondsTXT.strip()
        Microseconds = int(MicrosecondsTXT)
        when = datetime.datetime.strptime(stampNoMs, "%Y-%m-%d %H:%M:%S")
        when = when.replace(microsecond=Microseconds)
    except Exception as e:
        print("Error extracting timestamp ", e)
        when = datetime.datetime.now()  # default to new

    return (filename, when)


def check_image(base, filename):

    debug = False

    try:
        I = Image.open(base + filename)  # open the image file
        I.verify()  # verify that it is, in fact an image
        if debug:
            print("Good:", filename)
        I.close()
        return True
    except (IOError, SyntaxError) as e:
        if debug:
            print("Bad file:", filename, e)  # print out the names of corrupt files
        return False


def delete_old_image_files(folder, ageLimit):


    # folder is the name of the folder in which we
    # have to perform the delete operation
    # changing the current working directory
    # to the folder specified

    try:
        os.chdir(os.path.join(os.getcwd(), folder))
    except Exception as e:
        print(e)
        return

    # Only interested in these. Which limits the damage from
    # any accidental deletion

    imgnames = sorted(glob.glob("2*.jpg"))

    for index in range(len(imgnames)):
        if not check_image(folder, imgnames[index]):
            try:
                command = "sudo rm -f " + folder + imgnames[index] + " > /dev/null 2>&1"
                if not dryRun:
                    print("Remove corrupt jpg via command :", command)
                    os.system(command)
            except Exception as e:
                print(e)
                pass

    imgnames = sorted(glob.glob("2*.jpg"))
    when = list(map(txtTimestampToTime, imgnames))
    when = sorted(when, key=lambda x: x[1])

    now = datetime.datetime.now()
    expiryTime = now - datetime.timedelta(days=ageLimit)

    for index in range(len(when)):
        if when[index][1] < expiryTime:
            if not dryRun:
                os.system(
                    "sudo rm -f " + when[index][0] + " > /dev/null 2>&1"
                )
            print("Delete:", when[index][0])
        else:
            break  # List is sorted by date so there won't be any more

    # Remove local/non_local duplicates

    tidy.tidy(folder)

if __name__ == "__main__":

    runfile = sys.argv.pop(0)
    inputargs = sys.argv

    if len(inputargs) != 2:
        print(
            "Incorrect usage! Should be : <path>/expiry <directory> <time limit in days>"
        )
        sys.exit()

    try:
        ageLimit = int(inputargs[1])
    except:
        print(
            "Incorrect usage! Should be : <path>/expiry <directory> <time limit in days>"
        )
        sys.exit()

    print(
        "Delete corrupt images and images older than ",
        ageLimit,
        " days on directory:",
        inputargs[0],
    )

    delete_old_image_files(inputargs[0], ageLimit)

    sys.exit()
