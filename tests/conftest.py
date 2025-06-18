import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.binance.client import BinanceDataService
from bot.openai.signals import SignalGenerator


@pytest.fixture
def mock_binance():
    mock = AsyncMock(spec=BinanceDataService)
    mock.get_klines.return_value = []
    return mock


@pytest.fixture
def mock_signal_generator():
    mock = MagicMock(spec=SignalGenerator)
    mock.generate_signal.return_value = {"signal": "NONE"}
    return mock
