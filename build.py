import os

import fabric

import sys

import paramiko

import shutil

bucketname = sys.argv[1]

component = sys.argv[2]

service_name = sys.argv[3]

date = sys.argv[4]

job_type = sys.argv[5]

dir_path = sys.argv[6]

def argpath(index):
  try:
    sys.argv[index]
  except IndexError:
    return ''
  else:
    return sys.argv[index]

download_job_type = argpath(7)
log_name = argpath(8)
task_name = argpath(9)
log_folder_name_t_delete = argpath(10)
ssh_ip = "172.23.5.80"
def check_ssh_connection():
  ssh = None
  try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_ip, username="jenkins",timeout=10)
    if ssh:
      ssh.close()
    return True,"connection success"
  except Exception, e:
    exception = "Unable to connect to the remote bastion server. Reason: "+str(e)
    return False,exception

def uploadNdRunScript(script_location,jenkins_home,job_type):
    remote_connection = fabric.Connection(ssh_ip,user='jenkins')
    file_upload = remote_connection.put(script_location,jenkins_home)
    if job_type == "Log-Download":
        download_result = remote_connection.run('python '  + jenkins_home + ' '+bucketname+ ' ' +component+ ' ' + service_name + ' ' + date + ' ' +download_job_type + ' ' +log_name, hide=True)
    else:
        download_result = remote_connection.run('python ' + jenkins_home + ' ' +component + ' ' +log_folder_name_t_delete, hide=True)
    msg = "{0.stdout}"
    print(msg.format(download_result))
def runbuild():
  try:
    connection_result,connection_message = check_ssh_connection()
    if connection_result:
      if job_type == "Log-Download":
        uploadNdRunScript('services/s3-logs-download/downloadlogs.py', '/home/jenkins/downloadlogs.py',job_type)

      else:
        if task_name == "get-file-size":
          uploadNdRunScript('services/s3-logs-download/getsize.py', '/home/jenkins/getsize.py',job_type)
        else:
          uploadNdRunScript("services/s3-logs-download/deletelogdir.py", '/home/jenkins/deletelogdir.py',job_type)
        
    else:
      raise Exception(connection_message)
  except Exception as e:
    print('Could not download the requested logs. Reason: ' + str(e))

# execute main function

runbuild()
