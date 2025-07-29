import boto3
import sys
import botocore
import os

bucketname = sys.argv[1]

component = sys.argv[2]

service_name = sys.argv[3]

date = sys.argv[4]
s3_resource = boto3.resource('s3')

bucket = s3_resource.Bucket(bucketname)

PARTITION = "/data"

download_job_type = sys.argv[5]

def argpath(index):
  try:
    sys.argv[index]
  except IndexError:
    return ''
  else:
    return sys.argv[index]

log_name = argpath(6)
#check whether the required bucket exists on s3 

def check_bucket_exists():
  try:
      s3_resource.meta.client.head_bucket(Bucket=bucketname)
  except botocore.exceptions.ClientError as e:
      # If a client error is thrown, then script exits.
      sys.exit("Specified bucket does not exist or the user does not have permission to access it!!")


#get the available space present on the local system where the logs are to be downloaded

def get_available_local_space(partition):
  partition_stats = os.statvfs(partition)
  total_fs_size = partition_stats.f_frsize * partition_stats.f_blocks     # Size of filesystem in bytes
  free_fs_size = partition_stats.f_frsize * partition_stats.f_bfree      # Actual number of free bytes
  available_fs_size = partition_stats.f_frsize * partition_stats.f_bavail     # Number of free bytes that ordinary users are allowed to use (excl. reserved space)  
  return(available_fs_size)


#generate the path to which the required keys/logs will be downloaded

def get_download_path(component):
  component_path_map = { 
        "middleware": "/data/mwlogs/", 
        "upi": "/data/upilogs/",
        "fastag": "/data/fastaglogs/",
        "cbs": "/data/cbslogs/",
        "kyc": "/data/kyclogs/",
        "acquirer": "/data/aepslogs/",
        "comsdr": "/data/comslogs/"
    }
  
  return component_path_map.get(component,None) 


#fetch the bucket object, which will contain all the required keys.

def get_bucket_object(prefix):

  bucketobj = bucket.objects.filter(Prefix=prefix)
  
  list_bucketobj = list(bucketobj)

  if len(list_bucketobj) <= 0:
    sys.exit("No logs present for the mentioned date!!")
  else:
    return bucketobj
  

#get the total size of the keys/logs to be downloaded.

def get_total_download_size(bucketobj):
  download_size = 0
  for s3_object in bucketobj:
    try:
      download_size = download_size + s3_object.size
    except Exception, e:
      return ("Size Calculation Exception")
  return (download_size)


#finally, if all checks pass, download the required keys.
def get_list_of_logs():
  complete_log_array=[]
  log_names = []
  complete_log = "\n"
  check_bucket_exists()
  download_path = get_download_path(component)+service_name+"_"+date
  if component == "comsdr":
     download_key = "paytmbank/prodcomsdr/"+component+"/"+service_name+"/application/"+date+"/archive/"
  else:  
     download_key = "paytmbank/prod/"+component+"/"+service_name+"/application/"+date+"/archive/"
  for object_summary in bucket.objects.filter(Prefix=download_key):
      complete_log_array.append(object_summary.key)
  complete_log = complete_log.join(complete_log_array)
  print(complete_log.replace(download_key, "")) 
  
def download_s3_object():
  check_bucket_exists()
  download_path = get_download_path(component)+service_name+"/"+date

  if component == "comsdr": 
     if log_name == "no-log-name":
        download_key = "paytmbank/prodcomsdr/"+component+"/"+service_name+"/application/"+date+"/archive/"
     else:
        download_key = "paytmbank/prodcomsdr/"+component+"/"+service_name+"/application/"+date+"/archive/"+log_name
  else: 
     if log_name == "no-log-name":
        download_key = "paytmbank/prod/"+component+"/"+service_name+"/application/"+date+"/archive/"
     else:
        download_key = "paytmbank/prod/"+component+"/"+service_name+"/application/"+date+"/archive/"+log_name

  print(download_key)
  bucketobj = get_bucket_object(download_key)

  available_local_size = get_available_local_space(PARTITION)

  download_size = get_total_download_size(bucketobj)

  if download_size == "Size Calculation Exception":
    sys.exit("Couldn't determine key size. Cannot download the logs, please contact DevOps for assistance")
  elif download_size >= available_local_size:
    sys.exit("Space not available on the bastion server! Please clear some space before the logs can be downloaded. Space required in bytes - " + str(download_size))
  else:
    if not os.path.exists(download_path):
      os.makedirs(download_path)
    for s3_object in bucketobj:
      filename = s3_object.key.rsplit('/',1)[1]
      if s3_object.storage_class == "GLACIER" or s3_object.storage_class == "DEEP_ARCHIVE":
        try:
          obj = s3_resource.Object(s3_object.bucket_name, s3_object.key)
          if obj.restore is None:
              print('Submitting restoration request: %s' % obj.key)
              obj.restore_object(RestoreRequest={"Days":1,"GlacierJobParameters":{"Tier":"Standard"}})
          elif 'ongoing-request="true"' in obj.restore:
              print('Restoration in-progress: %s' % obj.key)
          elif 'ongoing-request="false"' in obj.restore:
              print('Restoration complete: %s' % obj.key)
              bucket.download_file(s3_object.key, download_path + "/" + filename)
              print("File downloaded --- " + s3_object.key)
        except Exception as e:
          sys.exit("Couldn't download s3 object keys. Exception --- " + str(e))

      else:
        try:
          bucket.download_file(s3_object.key,download_path+"/"+filename)
          print ("File downloaded --- " + s3_object.key)
        except Exception, e:
          sys.exit("Couldn't download s3 object keys. Exception --- " + str(e))
if download_job_type == "get-list":
  get_list_of_logs()
elif download_job_type == "download-logs":
  download_s3_object()
else:
  print ("Nothing To do here ! You have not selected anything for donwload log job")
