import pytest
from unittest.mock import AsyncMock, MagicMock
from bot.trading import TradingEngine
from bot.models.trade import TradeSignal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def trading_engine():
    engine = create_engine("sqlite:///:memory:")
    TradingEngine.Base.metadata.create_all(engine)
    return TradingEngine(engine)


@pytest.mark.asyncio
async def test_execute_trade(trading_engine):
    mock_session = MagicMock()
    trading_engine.Session = MagicMock(return_value=mock_session)

    test_signal = {"signal": "BUY", "price": 50000.0, "tp": 51000.0, "sl": 49000.0}

    await trading_engine.execute_trade(test_signal, "BTCUSDT")

    # Проверяем, что сессия была создана
    trading_engine.Session.assert_called_once()

    # Проверяем, что объект TradeSignal был добавлен
    mock_session.add.assert_called_once()
    assert isinstance(mock_session.add.call_args[0][0], TradeSignal)

    # Проверяем, что изменения были зафиксированы
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_signal(trading_engine):
    with pytest.raises(ValueError):
        await trading_engine.execute_trade({"signal": "INVALID"}, "BTCUSDT")
