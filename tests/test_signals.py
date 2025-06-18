import pytest
from bot.openai.signals import SignalGenerator


@pytest.mark.asyncio
async def test_signal_generation(mock_signal_generator):
    test_data = [{"close": 50000}]
    result = await mock_signal_generator.generate_signal(test_data)
    assert "signal" in result
