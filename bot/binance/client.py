from typing import Optional, Dict, List
from binance import AsyncClient, BinanceSocketManager
from tenacity import retry, stop_after_attempt, wait_exponential
from bot.utils.logger import setup_logger

logger = setup_logger("binance_client")


class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Optional[AsyncClient] = None
        self.socket_manager: Optional[BinanceSocketManager] = None

    async def connect(self) -> None:
        """Установка соединения с Binance API"""
        try:
            self.client = await AsyncClient.create(
                    api_key=self.api_key,
                    api_secret=self.api_secret,
                    testnet=False  # Для реальной торговли
            )
            self.socket_manager = BinanceSocketManager(self.client)
            logger.info("Binance connection established")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

    async def close(self) -> None:
        """Корректное закрытие соединений"""
        if self.client:
            await self.client.close_connection()
            logger.info("Binance connection closed")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_klines(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """
        Получение исторических данных
        :param symbol: Торговая пара (BTCUSDT)
        :param interval: Интервал (1m, 5m, 15m и т.д.)
        :param limit: Количество свечей
        :return: Список словарей с данными свечей
        """
        print(1)
        print(self.client)
        if not self.client:
            print(11111)
            raise RuntimeError("Client not connected")

        try:
            print(2)
            data = await self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            print(3)
            return self._format_klines(data)
        except Exception as e:
            logger.error(f"Klines error for {symbol}: {e}")
            raise

    def _format_klines(self, data: List) -> List[Dict]:
        """Форматирование сырых данных Binance"""
        return [{
            'time': item[0],
            'open': float(item[1]),
            'high': float(item[2]),
            'low': float(item[3]),
            'close': float(item[4]),
            'volume': float(item[5])
        } for item in data]

    @retry(stop=stop_after_attempt(3))
    async def get_account_info(self) -> Dict:
        """Получение информации об аккаунте"""
        try:
            return await self.client.futures_account()
        except Exception as e:
            logger.error(f"Account info error: {e}")
            raise

    async def create_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        **kwargs
    ) -> Dict:
        """
        Создание ордера
        :param symbol: Торговая пара
        :param side: BUY/SELL
        :param quantity: Количество
        :param order_type: Тип ордера (MARKET, LIMIT и т.д.)
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
                **kwargs
            }
            logger.info(f"Creating order: {params}")
            return await self.client.futures_create_order(**params)
        except Exception as e:
            logger.error(f"Order error: {e}")
            raise

    async def start_market_stream(self, symbol: str, callback):
        """Запуск websocket-потока для маркет-данных"""
        try:
            async with self.socket_manager.futures_kline_socket(symbol, interval='15m') as stream:
                while True:
                    data = await stream.recv()
                    callback(data)
        except Exception as e:
            logger.error(f"Websocket error: {e}")
            raise


    async def __aenter__(self):
        """
        Пример использования в виде контекстного менеджера
        async with BinanceClient(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET) as client:
            klines = await client.get_klines("DOTUSDT", "15m")
            await client.create_order("DOTUSDT", "BUY", 0.001)
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
