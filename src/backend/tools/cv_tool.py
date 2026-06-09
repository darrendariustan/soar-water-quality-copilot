import boto3
import base64
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from schemas import WaterAppearancePayload, WaterTestStripPayload

class CVTool:
    def __init__(self, region_name="us-east-1"):
        """
        Initialize the CV tool with AWS Rekognition client.
        Boto3 automatically picks up credentials from environment variables 
        (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) if they are set.
        """
        self.rekognition = boto3.client('rekognition', region_name=region_name)

    def analyze_water_appearance(self, image_bytes: bytes, image_url: str) -> WaterAppearancePayload:
        """
        Uses Amazon Rekognition to analyze the visual appearance of the water sample.
        Maps the detected labels to our WaterAppearancePayload schema.
        """
        try:
            response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=10,
                MinConfidence=70
            )
            
            # Simple heuristic mapping for MVP
            labels = [label['Name'].lower() for label in response.get('Labels', [])]
            
            clarity = "Clear"
            if any(word in labels for word in ["cloud", "cloudy", "mud", "turbid", "opaque"]):
                clarity = "Cloudy"
            elif any(word in labels for word in ["color", "brown", "green", "yellow", "tinted"]):
                clarity = "Colored"
                
            particles = any(word in labels for word in ["particle", "dirt", "sediment", "sand", "debris"])
            
            # Use confidence of the most relevant label, or default to a baseline
            confidence = response['Labels'][0]['Confidence'] / 100.0 if response.get('Labels') else 0.8
            
            return WaterAppearancePayload(
                image_url=image_url,
                clarity_classification=clarity,
                particle_detected=particles,
                confidence_score=confidence
            )
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"Rekognition API error: {str(e)}")

    def analyze_test_strip(self, image_bytes: bytes, image_url: str) -> WaterTestStripPayload:
        """
        Uses Amazon Rekognition to analyze the dip test strip.
        In a real application, this might use Custom Labels to map colors to chemical ppm values.
        For MVP, we verify connectivity via detect_labels and return a mocked parsed result.
        """
        try:
            # We call Rekognition just to verify connectivity and get a basic confidence score
            response = self.rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=5,
                MinConfidence=50
            )
            
            confidence = response['Labels'][0]['Confidence'] / 100.0 if response.get('Labels') else 0.85
            
            # Mocking test strip values for MVP to satisfy the schema
            return WaterTestStripPayload(
                image_url=image_url,
                ph=7.2,
                chlorine_residual_ppm=1.0,
                turbidity_ntu=2.5,
                nitrate_ppm=5.0,
                nitrite_ppm=0.1,
                hardness_ppm=120.0,
                iron_ppm=0.05,
                confidence_score=confidence
            )
        except (BotoCoreError, ClientError) as e:
            raise Exception(f"Rekognition API error: {str(e)}")
