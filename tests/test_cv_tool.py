import os
import sys
import unittest
from dotenv import load_dotenv

# Add src/backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/backend'))

from tools.cv_tool import CVTool
from botocore.exceptions import NoCredentialsError

class TestCVTool(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.cv_tool = CVTool(region_name="us-east-1")
        # 1x1 base64 encoded PNG image to simulate a valid image for Rekognition
        import base64
        self.dummy_jpeg_bytes = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')

    def test_aws_credentials_loaded(self):
        """
        Tests whether the boto3 client correctly loads AWS credentials from the environment.
        We assert that AWS_ACCESS_KEY_ID is available.
        """
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.assertIsNotNone(access_key, "AWS_ACCESS_KEY_ID is missing from the environment. Credentials might not be loaded.")

    def test_analyze_water_appearance_valid_json(self):
        """
        Tests whether the CV tool returns a properly structured schema payload
        for a simulated image request.
        """
        try:
            appearance = self.cv_tool.analyze_water_appearance(self.dummy_jpeg_bytes, "s3://test-bucket/water.jpg")
            # Verify the response is an instance of our payload model and has expected defaults
            self.assertIsNotNone(appearance.clarity_classification)
            self.assertIn(appearance.clarity_classification, ["Clear", "Cloudy", "Colored"])
            self.assertIsInstance(appearance.confidence_score, float)
            
            # This verifies the payload is valid JSON (Pydantic model dumping)
            json_dump = appearance.model_dump_json()
            self.assertTrue(len(json_dump) > 0)
            
        except Exception as e:
            if "InvalidSignatureException" in str(e) or "UnrecognizedClientException" in str(e) or "AccessDeniedException" in str(e):
                self.skipTest("Valid AWS credentials are required to run this test against Rekognition.")
            else:
                self.fail(f"API call to Rekognition failed: {str(e)}")

    def test_analyze_test_strip_valid_json(self):
        """
        Tests whether the CV tool returns a properly structured test strip payload.
        """
        try:
            strip = self.cv_tool.analyze_test_strip(self.dummy_jpeg_bytes, "s3://test-bucket/strip.jpg")
            self.assertIsNotNone(strip.ph)
            self.assertIsInstance(strip.confidence_score, float)
            
            json_dump = strip.model_dump_json()
            self.assertTrue(len(json_dump) > 0)
        except Exception as e:
            if "InvalidSignatureException" in str(e) or "UnrecognizedClientException" in str(e) or "AccessDeniedException" in str(e):
                self.skipTest("Valid AWS credentials are required to run this test against Rekognition.")
            else:
                self.fail(f"API call to Rekognition failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
