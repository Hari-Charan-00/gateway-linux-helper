import warnings
import sys
import subprocess
import time

warnings.filterwarnings("ignore")

OPS_RAMP_CLOUD_DOMAIN = "api.opsramp.io"
PING_COUNT = 4

unixtime = str(sys.argv[1])
uuid = unixtime.split("@@")[0]

print(uuid)

def execute_commands(commands):
    try:
        for command, success_message in commands:
            print(f"Executing: {success_message}")
            exit_code = subprocess.call(command, shell=True)

            if exit_code == 0:
                print("Command executed successfully.")
                print("=" * 50)
            else:
                print(f"Command failed with exit code {exit_code}.")
                print("=" * 50)
                break  # Stop execution if a command fails

            # Add a short delay to allow the file system to recognize the copied file
            time.sleep(1)

    except Exception as e:
        print("Got Exception:", str(e))

process = subprocess.Popen(['ping', OPS_RAMP_CLOUD_DOMAIN, '-c', str(PING_COUNT)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
returncode = process.wait()
res = process.stdout.read().decode()

if returncode != 0:
    print("Ping to OpsRamp Cloud failed!")
    print("Ping was not successful, please whitelist the following IP addresses for USPOD1 only 140.239.76.0/24 206.80.7.128/26 34.86.90.64/27")
    pingresult = False
else:
    pingresult = True

print("Ping result of OpsRamp cloud:\n", res)
telnet = True

process2 = subprocess.Popen(['telnet', OPS_RAMP_CLOUD_DOMAIN, '443'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
res2 = process2.stdout.read().decode()
print("Checking telnet for OpsRamp cloud on port 443:\n", res2)

if "Connected" not in res2:
    telnet = False
    print("*************************************************************")
    print("Telnet was not successful, please whitelist the following IP addresses for USPOD1 only 140.239.76.0/24 206.80.7.128/26 34.86.90.64/27")
    print("*************************************************************")
    if pingresult is False or telnet is False:
        print("Result: OpsRamp Gateway is unable to reach OpsRamp Cloud")
        print("[Failed]")
        print("Next Steps")
        print("Assigning the ticket for further troubleshooting")
        print("*************************************************************")
    sys.exit()
else:
    print("Telnet was successful")

process3 = subprocess.Popen(['nslookup', OPS_RAMP_CLOUD_DOMAIN], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
res3 = process3.stdout.read().decode()

if telnet and pingresult:
    print("*************************************************************")
    print("Result: OpsRamp cloud is reachable from OpsRamp Gateway")
    print("The Gateway had good reachability.")
    print("Running service-related commands")
    print("*************************************************************")
    def execute_command(command):
        try:
            command_with_sudo = "sudo su -c '{}'".format(command)
            process = subprocess.Popen(
                command_with_sudo,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, _ = process.communicate()
            stdout_decoded = stdout.decode('utf-8') 
            return stdout_decoded
        except subprocess.CalledProcessError as e:
            print("Error executing command: {}".format(command))
            print("Error output: {}".format(e.output))
            return None

    command = "service vprobe status"
    stdout_data_decoded = execute_command(command)

    if stdout_data_decoded and 'active (running)' in stdout_data_decoded:
        print("vprobe status is in running state")
        execute_command("systemctl restart monit")
        time.sleep(300)
        print("Restarted all services successfully")
        print("No issues with the Gateway reachability and services. Please check manually if the Gateway was not Online")
        print("[Success]")
        print("Next Steps")
        print("Closing this incident.")
        print("*************************************************************")
        sys.exit()

    else:
        print("Trying to restart the vprobe")
        stdout_data_decoded1 = execute_command("systemctl restart vprobe")
        time.sleep(100)
        if 'active (running)' not in stdout_data_decoded1:
            print("vprobe service is not running")
            print("Unable to restart, please do manually")
        else:
            print("vprobe restarted")

    print("Restarting all services")
    second_iteration = execute_command("systemctl restart monit")

    if second_iteration:
        time.sleep(300)
        print("Restarted all services successfully")
        print("No issues with the Gateway reachability and services. Please check manually if the Gateway was not Online")
        print("*************************************************************")
        print("[Success]")
        print("Next Steps")
        print("Closing this incident.")
        print("*************************************************************")

else:
    commands_to_execute = [
        ("sudo su -", "sudo command executed."),
        ("cd /var/log/app", "Changed directory."),
        ("ls > /dev/null 2>&1", "Listed files."),
        ("if [ -e vprobe.log ] && [ -e vprobe-tls-comm.log  ]; then echo 'Both vprobe.log and vprobe-tls-comm.log  exist'; fi", "Checked for existence of vprobe.log and vprobegateway.tls."),
        ("cp /var/log/app/vprobe.log /home/ruser/vprobe.log", "Copied vprobe.log as vprobe.log."),
        ("cp /var/log/app/vprobe-tls-comm.log /home/ruser/vprobe.tls", "Copied vprobe-tls-comm.log as vprobe.tls."),
        ("cd /home/ruser", "Back to user directory."),
        ("if [ -e vprobe.log ]; then echo 'vprobe.log exists'; fi", "Checked for vprobe.log existence."),
        ("if [ -e vprobe.tls ]; then echo 'vprobe.tls exists'; fi", "Checked for vprobe.tls existence."),
        ("cd /home/ruser", "Back to user directory."),
        ("chown ruser:ruser /home/ruser/vprobe.log", "Changed ownership of vprobe.log."),
        ("chmod 644 /home/ruser/vprobe.log", "Changed permissions of vprobe.log."),
        ("chown ruser:ruser /home/ruser/vprobe.tls", "Changed ownership of vprobe.tls."),
        ("chmod 644 /home/ruser/vprobe.tls", "Changed permissions of vprobe.tls.")
        # Add more commands as needed
    ]

    execute_commands(commands_to_execute)
    print("=" * 50)
    print("All commands executed successfully.")
    print("You can log in and download the logs in the path /home/ruser")
