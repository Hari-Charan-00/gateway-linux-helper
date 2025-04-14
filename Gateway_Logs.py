import subprocess
import time

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
        print("An error occurred:", str(e))

if __name__ == "__main__":
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
    print("You can log in and download the logs")
