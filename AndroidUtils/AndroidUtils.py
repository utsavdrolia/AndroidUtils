import os
import subprocess
import traceback
from time import sleep
import itertools

# setup logs
# create logger
import logging
import logging.handlers

import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create temp director
if not os.path.exists("/tmp/AndroiUtils"):
    os.makedirs("/tmp/AndroiUtils")

# create console handler and set level to debug
ch = logging.handlers.RotatingFileHandler("/tmp/AndroiUtils/log", maxBytes=10 * 1024, backupCount=10)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(fmt='[%(name)][%(levelname)s]%(asctime)s %(message)s', datefmt='%Y/%m/%d-%H:%M:%S')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

stream = logging.StreamHandler(stream=sys.stdout)
stream.setLevel(logging.DEBUG)
stream.setFormatter(formatter)
logger.addHandler(stream)


def all(func, devs, *args):
    """
    Apply function and args to all devices
    :param func:
    :param devs:
    :param args:
    :return:
    """
    repeated_args = []
    for arg in args:
        repeated_args.append(itertools.repeat(arg, len(devs)))
    return map(func, devs, *repeated_args)


def run_command(command):
    logger.info("Running:" + " ".join(command))
    try:
        return subprocess.check_output(command)
    except subprocess.CalledProcessError:
        logger.error(traceback.format_exc())
        return


def connect(dev):
    """
    Connects to given device (IP address)
    :param dev: IP address of device
    :return: "<IPaddress>:<port>" if connected, None otherwise
    """
    command = ["adb", "connect", dev]
    reply = run_command(command).split()
    sleep(1)
    if reply[0] == "connected":
        return reply[2]
    elif reply[0] == "already":
        return reply[3]
    return None


def get_available_devices(subnet, num_devs):
    devs = []
    subnet = ".".join(subnet.split(".")[:-1])
    for last in range(1, 255):
        dev = subnet + "." + str(last)
        reply = connect(dev)
        if reply is not None:
            devs.append(reply)
            if len(devs) == num_devs:
                return devs
    return devs


def disconnect():
    command = ["adb", "disconnect"]
    return run_command(command)


def kill_server():
    command = ["adb", "kill-server"]
    return run_command(command)


def start_server():
    command =["adb", "start-server"]
    return run_command(command)


def send_file(dev, local, remote):
    command = ["adb", "-s", dev, "wait-for-device", "push", local, remote]
    return run_command(command)


def get_file(dev, remote, local):
    command = ["adb", "-s", dev, "wait-for-device", "pull", remote, local]
    ret = run_command(command)
    return ret


def rm(dev, remote):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "rm", remote]
    return run_command(command)


def mkdir(dev, dir):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "mkdir -p", dir]
    return run_command(command)


def kill_app(dev, app):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "force-stop", app]
    return run_command(command)


def launch_app(dev, app):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "start", "-a", "android.intent.action.MAIN", "-n", app]
    return run_command(command)


def send_intent(dev, intent):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a"]
    command.extend(intent)
    return run_command(command)


def trepn_profiler_launch(dev, preference_name):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "startservice", "com.quicinc.trepn/.TrepnService"]
    run_command(command)
    sleep(1)
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.load_preferences",
               "-e", "com.quicinc.trepn.load_preferences_file", "/sdcard/trepn/saved_preferences/" + preference_name]
    res = run_command(command)
    sleep(1)
    return res


def trepn_profiler_kill(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "stopservice", "com.quicinc.trepn/.TrepnService"]
    return run_command(command)


def trepn_start_profiling(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.start_profiling",
               "-e", "com.quicinc.trepn.database_file", "log"]
    res = run_command(command)
    sleep(1)
    return res


def trepn_stop_profiling(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.stop_profiling"]
    res = run_command(command)
    sleep(1)
    return res


def trepn_export_logs(dev):
    """
    Start exporting the logs
    :param dev:
    :return:
    """
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.export_to_csv", "-e",
               "com.quicinc.trepn.export_db_input_file", "log", "-e", "com.quicinc.trepn.export_csv_output_file", "out.csv"]
    res = run_command(command)
    return res


def trepn_get_logs(dev, log):
    """
    Get the exported logs
    :param dev:
    :param log:
    :return:
    """
    # check if fully exported
    while True:
        ret = run_command(["adb", "-s", dev, "wait-for-device", "shell", "lsof", "|", "grep", "trepn/out.csv"])

        if len(ret) == 0 or ret.find("out.csv") == -1:
            break
        logger.info("Exporting...")
        sleep(1)

    get_file(dev, "/sdcard/trepn/out.csv", log)
    rm(dev, "/sdcard/trepn/out.csv")
    rm(dev, "/sdcard/trepn/log.db")


def reboot(dev):
    command = ["adb", "-s", dev, "reboot"]
    return run_command(command)


def dumpsys_battery(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "dumpsys", "batterystats", "--checkin"]
    return run_command(command)


def dumpsys_reset(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "dumpsys", "batterystats", "--reset"]
    return run_command(command)


def get_netstats(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "cat", "/proc/net/xt_qtaguid/stats"]
    return run_command(command)


def get_uid(dev, package_name):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "dumpsys", "package", package_name]
    out = run_command(command)
    out = out.splitlines()
    for line in out:
        line = line.strip()
        if line.startswith("userId"):
            chunks = line.split()
            for chunk in chunks:
                if chunk.startswith("userId"):
                    _ , userid = chunk.split("=")
                    return userid
    return None


def get_netstats_uid(dev, uid):
    out = get_netstats(dev)
    out = out.splitlines()
    rx_bytes = 0l
    tx_bytes = 0l
    for line in out:
        line = line.strip()
        chunks = line.split()
        userid = chunks[3]
        if userid == uid:
            rx_bytes += long(chunks[5])
            tx_bytes += long(chunks[7])

    return {"rx": rx_bytes, "tx": tx_bytes}
