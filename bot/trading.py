from binance import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.models.trade import TradeSignal
from typing import Dict, Any


class TradingEngine:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    async def execute_trade(self, signal: Dict[str, Any], symbol: str):
        session = self.Session()
        try:
            trade = TradeSignal(
                symbol=symbol,
                signal_type=signal["signal"],
                price=signal["price"],
                tp_price=signal["tp"],
                sl_price=signal["sl"],
                status="OPEN",
            )
            session.add(trade)
            session.commit()

            # Здесь логика исполнения ордера через Binance API
            # ...
            
            print("implement the logic of binance api order")

        finally:
            session.close()
