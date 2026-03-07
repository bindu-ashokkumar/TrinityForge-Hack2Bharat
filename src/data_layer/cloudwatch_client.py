"""
CloudWatch Client for logging and metrics
"""

import json
import re
from typing import Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError


class CloudWatchClient:
    """Manages logging and metrics"""
    
    def __init__(self, region: str, log_group: str = "/aws/swasthcart"):
        self.logs = boto3.client('logs', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.log_group = log_group
        self.log_stream = f"stream-{datetime.utcnow().strftime('%Y-%m-%d')}"
        
        # Ensure log group and stream exist
        self._ensure_log_group()
        self._ensure_log_stream()
    
    def _ensure_log_group(self):
        """Ensure log group exists"""
        try:
            self.logs.create_log_group(logGroupName=self.log_group)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                print(f"Warning: Could not create log group: {str(e)}")
    
    def _ensure_log_stream(self):
        """Ensure log stream exists"""
        try:
            self.logs.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                print(f"Warning: Could not create log stream: {str(e)}")
    
    def log_event(
        self,
        level: str,
        message: str,
        context: Optional[dict] = None
    ) -> None:
        """Log event to CloudWatch Logs"""
        try:
            # Sanitize context to remove sensitive data
            sanitized_context = self._sanitize_context(context) if context else {}
            
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
                "context": sanitized_context
            }
            
            self.logs.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[
                    {
                        'timestamp': int(datetime.utcnow().timestamp() * 1000),
                        'message': json.dumps(log_entry)
                    }
                ]
            )
            
        except Exception as e:
            # Best-effort logging - don't fail the application
            print(f"Warning: Failed to log to CloudWatch: {str(e)}")
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "None"
    ) -> None:
        """Put custom metric to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='SwasthCart',
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.utcnow()
                    }
                ]
            )
        except Exception as e:
            # Best-effort metrics - don't fail the application
            print(f"Warning: Failed to put metric to CloudWatch: {str(e)}")
    
    def _sanitize_context(self, context: dict) -> dict:
        """Sanitize context to remove sensitive data"""
        sanitized = {}
        
        # Patterns for sensitive data
        sensitive_patterns = [
            r'password', r'secret', r'key', r'token', r'credential',
            r'ssn', r'credit_card', r'email', r'phone', r'address'
        ]
        
        for key, value in context.items():
            # Check if key contains sensitive pattern
            is_sensitive = any(re.search(pattern, key.lower()) for pattern in sensitive_patterns)
            
            if is_sensitive:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_context(value)
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "...[truncated]"
            else:
                sanitized[key] = value
        
        return sanitized
