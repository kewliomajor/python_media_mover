import os
import subprocess
import paramiko
import discord_notify
import secrets


def log_exec_errors(cmd, error):
    errors = error.readlines()

    if len(errors) > 0:
        error_string = ""
        for err_line in errors:
            err_line = err_line.rstrip("\n\r")
            error_string += err_line
        print('Error exec on remote: ' + cmd + ' - ' + error_string)
        discord_notify.send('Error exec on remote ' + cmd + ' - ' + error_string)
        exit()


if os.system("ping -c 1 " + secrets.desktop_host) != 0:
    print('desktop is not available - exiting')
    exit()

ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()
ssh_client.connect(secrets.radarr_host, username=secrets.ssh_user, key_filename=secrets.radarr_private_key_path)

print('connected to radarr')

command = 'find movies tv -name "*.*"'

stdin, stdout, stderr = ssh_client.exec_command(command)

log_exec_errors(command, stderr)

for line in stdout.readlines():
    line = line.rstrip("\n\r")
    line = line.replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')

    try:
        output = subprocess.check_output(["scp -3 'radarr:" + line + "' 'desktop:\"Desktop/Movies to Watch\"'"], shell=True)
    except subprocess.CalledProcessError as e:
        discord_notify.send('Error copying file ' + line + ' to desktop - ' + str(e))
        exit()

    print('Copied file ' + line + ' to desktop')
    discord_notify.send('Copied file ' + line + ' to desktop')

    print('deleting remote file')

    command = 'rm ' + line

    stdin, stdout, stderr = ssh_client.exec_command(command)

    log_exec_errors(command, stderr)

ssh_client.close()

print('done')

exit()
