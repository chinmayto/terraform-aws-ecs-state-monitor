# write a code to monitor ECS cluster using boto3 and send an sns notification if cluster status is changed
import boto3
import time
from botocore.exceptions import ClientError

# change the region if needed
boto3.setup_default_session(region_name='us-east-2')

def get_ecs_clusters():
    """Get a list of ECS clusters."""
    ecs_client = boto3.client('ecs')
    try:
        response = ecs_client.list_clusters()
        print("ECS Clusters found:", response['clusterArns'])
        return response['clusterArns']
    except ClientError as e:
        print(f"Error fetching ECS clusters: {e}")
        return []
    
def get_cluster_status(cluster_arn):
    """Get the status of a specific ECS cluster."""
    ecs_client = boto3.client('ecs')
    try:
        response = ecs_client.describe_clusters(clusters=[cluster_arn])
        print (f"Status for cluster {cluster_arn}: {response['clusters'][0]['status']}")
        return response['clusters'][0]['status']
    except ClientError as e:
        print(f"Error fetching status for cluster {cluster_arn}: {e}")
        return None
    
def send_sns_notification(message):
    """Send an SNS notification."""
    sns_client = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-2:197317184204:CT-ECS-Cluster-topic'  # Replace with your SNS topic ARN
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject='ECS Cluster Status Change Notification'
        )
        print("Notification sent successfully.")
    except ClientError as e:
        print(f"Error sending SNS notification: {e}")

def monitor_ecs_clusters():
    """Monitor ECS clusters for status changes."""
    previous_statuses = {}
    
    while True:
        clusters = get_ecs_clusters()
        if not clusters:
            print("No ECS clusters found.")
            time.sleep(60)
            continue
        
        for cluster_arn in clusters:
            current_status = get_cluster_status(cluster_arn)
            if current_status is None:
                continue
            
            if cluster_arn not in previous_statuses:
                message = f"ECS Cluster {cluster_arn} status changed from NONE to {current_status}."
                send_sns_notification(message)
                previous_statuses[cluster_arn] = current_status
                continue
            
            if current_status != previous_statuses[cluster_arn]:
                message = f"ECS Cluster {cluster_arn} status changed from {previous_statuses[cluster_arn]} to {current_status}."
                send_sns_notification(message)
                previous_statuses[cluster_arn] = current_status
        
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    monitor_ecs_clusters()
