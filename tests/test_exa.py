import os
import sys
from unittest.mock import patch, MagicMock

# Add src/backend to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/backend'))

from tools.exa_crawl_tool import search_trusted
from agents.exa_crawl_agent import exa_crawl_agent
from agents.schemas import QualityAssessment
from schemas import WaterQualityAnalysisRequest

class MockExaResult:
    def __init__(self, title, url, highlights):
        self.title = title
        self.url = url
        self.highlights = highlights

class MockExaResponse:
    def __init__(self, results):
        self.results = results

@patch.dict(os.environ, {"EXA_API_KEY": "dummy_key"})
@patch("exa_py.Exa")
def test_search_trusted_success(mock_exa_class):
    mock_instance = MagicMock()
    mock_exa_class.return_value = mock_instance
    mock_instance.search_and_contents.return_value = MockExaResponse([
        MockExaResult("WHO Water Guidelines", "https://who.int/water", ["Guidance on safe water."])
    ])
    
    result = search_trusted("water safety", num_results=1)
    
    assert result["used_live"] is True
    assert len(result["sources"]) == 1
    assert result["sources"][0]["title"] == "WHO Water Guidelines"
    assert result["sources"][0]["summary"] == "Guidance on safe water."
    assert result["note"] == ""

@patch.dict(os.environ, {"EXA_API_KEY": ""})
def test_search_trusted_no_key():
    result = search_trusted("water safety")
    
    assert result["used_live"] is False
    assert len(result["sources"]) == 0
    assert "EXA_API_KEY not set" in result["note"]

@patch.dict(os.environ, {"EXA_API_KEY": "dummy_key"})
@patch("exa_py.Exa")
def test_exa_crawl_agent(mock_exa_class):
    mock_instance = MagicMock()
    mock_exa_class.return_value = mock_instance
    mock_instance.search_and_contents.return_value = MockExaResponse([
        MockExaResult("CDC Nitrate", "https://cdc.gov/nitrate", ["Boiling does not remove nitrate."])
    ])
    
    # Mock the graph state
    quality = QualityAssessment(contamination_type="nitrate")
    request = WaterQualityAnalysisRequest(
        user_id="test_user",
        appearance={"water_appearance": "clear", "confidence_score": 1.0, "image_url": ""},
        test_strip={"ph": 7.0, "confidence_score": 1.0, "image_url": ""},
        location="Uganda"
    )
    state = {"quality": quality, "request": request}
    
    result = exa_crawl_agent(state)
    
    exa_output = result["exa"]
    assert exa_output.used_live is True
    assert len(exa_output.sources) == 1
    assert exa_output.sources[0].title == "CDC Nitrate"
    
    # Verify the query was formed correctly by inspecting the mock call
    args, kwargs = mock_instance.search_and_contents.call_args
    query = args[0]
    assert "nitrate" in query
    assert "Uganda" in query
