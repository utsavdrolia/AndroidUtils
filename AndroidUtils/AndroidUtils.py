import subprocess
from time import sleep


def run_command(command):
    print " ".join(command)
    return subprocess.check_output(command)


def connect(dev):
    command = ["adb", "connect", dev]
    return run_command(command)


def connect_all(devs):
    for dev in devs:
        connect(dev)
        sleep(5)


def get_available_devices(subnet, num_devs):
    devs = []
    subnet = ".".join(subnet.split(".")[0:2])
    for last in range(1, 255):
        dev = subnet + "." + str(last)
        reply = connect(dev).split()
        if reply[0] == "connected":
            devs.append(reply[2])
            if len(devs) == num_devs:
                return devs
    return devs


def disconnect():
    command = ["adb", "disconnect"]
    run_command(command)


def kill_server():
    command = ["adb", "kill-server"]
    run_command(command)


def start_server():
    command =["adb", "start-server"]
    run_command(command)


def send_file(local, remote, dev):
    command = ["adb", "-s", dev, "wait-for-device", "push", local, remote]
    run_command(command)


def get_file(remote, local, dev):
    command = ["adb", "-s", dev, "wait-for-device", "pull", remote, local]
    run_command(command)


def rm(remote, dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "rm", remote]
    run_command(command)


def get_files(remote, local, devs):
    for dev in devs:
        get_file(remote, local+dev, dev)


def mkdir(dev, dir):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "mkdir -p", dir]
    run_command(command)


def stopApp(dev, app):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "force-stop", app]
    run_command(command)


def launchApp(dev, app):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "start", "-a", "android.intent.action.MAIN", "-n", app]
    run_command(command)


def send_intent(dev, intent):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a"]
    command.extend(intent)
    run_command(command)


def send_intent_to_all(devs, intent):
    for dev in devs:
        send_intent(dev, intent)


def launchAppOnAll(devs, app):
    for dev in devs:
        launchApp(dev, app)


def killAppOnAll(devs, app):
    for dev in devs:
        stopApp(dev, app)


def trepn_profiler_launch(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "startservice", "com.quicinc.trepn/.TrepnService"]
    run_command(command)
    sleep(1)
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.load_preferences",
               "-e", "com.quicinc.trepn.load_preferences_file", "/sdcard/trepn/saved_preferences/pref.pref"]
    run_command(command)
    sleep(1)


def trepn_launch_all(devs):
    for dev in devs:
        trepn_profiler_launch(dev)


def trepn_start_profiling(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.start_profiling",
               "-e", "com.quicinc.trepn.database_file", "log"]
    run_command(command)


def trepn_start_profiling_all(devs):
    for dev in devs:
        trepn_start_profiling(dev)


def trepn_stop_profiling(dev):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.stop_profiling"]
    run_command(command)


def trepn_stop_profiling_all(devs):
    for dev in devs:
        trepn_stop_profiling(dev)


def trepn_read_logs(dev, log):
    command = ["adb", "-s", dev, "wait-for-device", "shell", "am", "broadcast", "-a", "com.quicinc.trepn.export_to_csv", "-e",
               "com.quicinc.trepn.export_db_input_file", "log", "-e", "com.quicinc.trepn.export_csv_output_file", "out.csv"]
    run_command(command)
    sleep(5)
    get_file("/sdcard/trepn/out.csv", log, dev)
    rm("/sdcard/trepn/out.csv", dev)
    rm("/sdcard/trepn/log.db", dev)


def trepn_read_logs_all(devs, logdir):
    for dev in devs:
        trepn_read_logs(dev, logdir + dev)


def USBPowerOff():
    subprocess.call("/home/utsav/Research/Hyrax/AndroidScripts/USBpowerOff.sh")


def USBPowerOn():
    subprocess.call("/home/utsav/Research/Hyrax/AndroidScripts/USBpowerOn.sh")