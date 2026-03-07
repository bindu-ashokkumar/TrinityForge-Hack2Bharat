"""
Bedrock Client for AI reasoning, vision analysis, and embeddings
"""

import json
import base64
from typing import List
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


class BedrockTimeoutError(Exception):
    """Bedrock timeout error"""
    pass


class BedrockError(Exception):
    """Bedrock operation error"""
    pass


class BedrockClient:
    """Manages interactions with Amazon Bedrock"""

    def __init__(
        self,
        region: str,
        model_id: str = "amazon.nova-lite-v1:0",
        embedding_model_id: str = "amazon.titan-embed-text-v1",
        timeout: int = 30,
        vision_model_id: str = None,
        text_model_id: str = None,
        vision_region: str = None,
        text_region: str = None,
        **kwargs
    ):
        config = Config(
            read_timeout=timeout,
            connect_timeout=timeout,
            retries={'max_attempts': 1}
        )
        self.bedrock = boto3.client('bedrock-runtime', region_name=region, config=config, **kwargs)
        self.model_id = model_id
        self.embedding_model_id = embedding_model_id
        self.timeout = timeout

        # Separate clients for vision and text if different regions needed
        self.vision_model_id = vision_model_id or model_id
        self.text_model_id = text_model_id or model_id

        vision_r = vision_region or region
        text_r = text_region or region

        if vision_r != region:
            self.vision_client = boto3.client('bedrock-runtime', region_name=vision_r, config=config, **kwargs)
        else:
            self.vision_client = self.bedrock

        if text_r != region:
            self.text_client = boto3.client('bedrock-runtime', region_name=text_r, config=config, **kwargs)
        else:
            self.text_client = self.bedrock
    
    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3
    ) -> dict:
        """
        Invoke Bedrock model via Converse API.

        Returns:
            Parsed JSON response from model

        Raises:
            BedrockTimeoutError: If response takes > timeout seconds
            BedrockError: If model returns error
        """
        try:
            response = self.text_client.converse(
                modelId=self.text_model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                inferenceConfig={"maxTokens": max_tokens, "temperature": temperature}
            )

            text = response['output']['message']['content'][0]['text']
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    try:
                        return json.loads(text[start:end+1])
                    except json.JSONDecodeError:
                        pass
                return {"text": text}

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if 'Timeout' in error_code or 'RequestTimeout' in error_code:
                raise BedrockTimeoutError(f"Bedrock request timed out after {self.timeout} seconds")
            else:
                raise BedrockError(f"Bedrock API error: {str(e)}")
        except Exception as e:
            if 'timeout' in str(e).lower():
                raise BedrockTimeoutError(f"Bedrock request timed out: {str(e)}")
            else:
                raise BedrockError(f"Unexpected Bedrock error: {str(e)}")
    
    def analyze_image(
        self,
        image_path: str,
        prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.3
    ) -> dict:
        """
        Send an image to Bedrock for multimodal analysis.
        Uses the Converse API (works with Amazon Nova and Claude models).
        """
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            ext = image_path.lower().rsplit(".", 1)[-1]
            fmt = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png"}.get(ext, "jpeg")

            response = self.vision_client.converse(
                modelId=self.vision_model_id,
                messages=[{
                    "role": "user",
                    "content": [
                        {"image": {"format": fmt, "source": {"bytes": image_bytes}}},
                        {"text": prompt}
                    ]
                }],
                inferenceConfig={"maxTokens": max_tokens, "temperature": temperature}
            )

            text = response['output']['message']['content'][0]['text']
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Try to extract JSON from the text
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    try:
                        return json.loads(text[start:end+1])
                    except json.JSONDecodeError:
                        pass
                return {"text": text}

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if 'Timeout' in error_code or 'RequestTimeout' in error_code:
                raise BedrockTimeoutError(f"Bedrock vision timed out after {self.timeout}s")
            raise BedrockError(f"Bedrock vision API error: {str(e)}")
        except (BedrockTimeoutError, BedrockError):
            raise
        except Exception as e:
            raise BedrockError(f"Bedrock vision error: {str(e)}")

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Bedrock embedding model.
        
        Model: amazon.titan-embed-text-v1
        """
        try:
            request_body = {
                "inputText": text
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.embedding_model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'embedding' in response_body:
                return response_body['embedding']
            else:
                raise BedrockError("No embedding in response")
                
        except ClientError as e:
            raise BedrockError(f"Failed to generate embeddings: {str(e)}")
        except Exception as e:
            raise BedrockError(f"Unexpected error generating embeddings: {str(e)}")
