import paramiko
import os

# Set up the SSH key and GitLab repository details
ssh_key_path = os.path.expanduser('~/.ssh/id_rsa')
gitlab_user = "poneil3411@gmail.com"
gitlab_host = "gitlab.com"
gitlab_repo = "https://wwww.gitlab.com/mab-project/prod/mac-auth-byp4ss.git"
clone_directory = "~/your_local_directory"

# Create the SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Load the private key
private_key = paramiko.RSAKey(filename=ssh_key_path)

# Connect to GitLab
ssh.connect(hostname=gitlab_host, username=gitlab_user, pkey=private_key)

# Prepare the git clone command
clone_command = f"git clone git@gitlab.com:{gitlab_repo} {clone_directory}"

# Execute the command
stdin, stdout, stderr = ssh.exec_command(clone_command)
print(stdout.read().decode())
print(stderr.read().decode())

# Close the SSH connection
ssh.close()
