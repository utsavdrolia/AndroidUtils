import subprocess
from time import sleep
import itertools


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
    print "Running:" + " ".join(command)
    return subprocess.check_output(command)


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
    try:
        ret = run_command(command)
        return ret
    except subprocess.CalledProcessError:
        return


def rm(remote, dev):
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


def trepn_profiler_launch(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "startservice", "com.quicinc.trepn/.TrepnService"]
    run_command(command)
    sleep(1)
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.load_preferences",
               "-e", "com.quicinc.trepn.load_preferences_file", "/sdcard/trepn/saved_preferences/pref.pref"]
    res = run_command(command)
    sleep(1)
    return res


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


def trepn_read_logs(dev, log):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.export_to_csv", "-e",
               "com.quicinc.trepn.export_db_input_file", "log", "-e", "com.quicinc.trepn.export_csv_output_file", "out.csv"]
    res = run_command(command)
    sleep(5)
    get_file("/sdcard/trepn/out.csv", log, dev)
    rm("/sdcard/trepn/out.csv", dev)
    rm("/sdcard/trepn/log.db", dev)
    return res


def reboot(dev):
    command = ["adb", "-s", dev, "reboot"]
    return run_command(command)


def USBPowerOff():
    subprocess.call("/home/utsav/Research/Hyrax/AndroidScripts/USBpowerOff.sh")


def USBPowerOn():
    subprocess.call("/home/utsav/Research/Hyrax/AndroidScripts/USBpowerOn.sh")