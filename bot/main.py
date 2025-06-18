import asyncio
from bot.binance.client import BinanceDataService
from bot.openai.signals import SignalGenerator
from bot.config.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger("main")


class TradingBot:
    def __init__(self):
        self.binance_client = None
        self.signal_generator = None
        self.running = False

    async def initialize(self):
        """Инициализация сервисов"""
        try:
            self.binance_client = BinanceDataService(
                api_key=Config.BINANCE_API_KEY,
                api_secret=Config.BINANCE_API_SECRET
            )
            self.signal_generator = SignalGenerator()
            logger.info("Services initialized successfully")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    async def fetch_market_data(self, symbol: str, interval: str) -> list:
        """Получение данных с Binance"""
        try:
            async with BinanceDataService(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET) as binance_data_service:
                # await openai_client.create_order("DOTUSDT", "BUY", 0.001)
                data = await binance_data_service.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=100
                )
            logger.debug(f"Received {len(data)} klines for {symbol}")
            return data[-50:]  # Берем последние 50 свечей
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return []

    async def process_trading_cycle(self):
        """Один цикл анализа и торговли"""
        symbol = "SOLUSDT"
        try:
            # 1. Получаем данные
            market_data = await self.fetch_market_data(symbol, "15m")
            if not market_data:
                return

            # 2. Генерируем сигнал
            signal = await self.signal_generator.forecast_probability(symbol, market_data)
            logger.info(f"Signal received: {signal}")

            # 3. Исполняем сделку (заглушка)
            if signal.get("signal") in ("BUY", "SELL"):
                self.execute_trade(signal)

        except Exception as e:
            logger.error(f"Trading cycle error: {e}")

    def execute_trade(self, signal: dict):  # noqa
        """Заглушка для торговой логики"""
        logger.info(
            f"Заглушка: EXECUTE {signal['signal']} | "
            f"Price: {signal.get('price')} | "
            f"TP: {signal.get('tp')} | "
            f"SL: {signal.get('sl')}"
        )

    async def run(self):
        """Основной цикл работы бота"""
        try:
            await self.initialize()
            self.running = True
            logger.info("Starting trading bot...")

            while self.running:
                await self.process_trading_cycle()
                break   # только для DEBUG целей
                await asyncio.sleep(60)  # Пауза между циклами
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Корректное завершение работы"""
        if self.binance_client:
            await self.binance_client.close()
        self.running = False
        logger.info("Bot stopped")

    async def check_services(self):
        return {
            "binance_client": await self.binance_client.openai_client.ping(),
            "openai": bool(self.signal_generator.openai_client)
        }


if __name__ == "__main__":
    bot = TradingBot()

    try:
        asyncio.run(bot.run())
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        raise
