import json
from openai import AsyncOpenAI
from bot.config.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger("signals")
openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)


class SignalGenerator:
    CHATGPT_MODEL = "gpt-3.5-turbo"     # "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"

    async def forecast_probability(self, symbol, market_data: dict) -> dict:    # noqa
        # оптимизация jSON'a с klines
        optimized_market_data = self.optimize_market_data(market_data)
        try:
            response = await openai_client.chat.completions.create(
                model=SignalGenerator.CHATGPT_MODEL,
                messages=[{"role": "user", "content": f"Проанализируй данные рынка и верни JSON. Данные: {market_data}"}],
                temperature=0.3
            )
            response_json = json.loads(response.choices[0].message.content)
            logger.info(f"Generated signal: {response_json}")
            assert {"signal", "price", "tp", "sl"}.issubset(response_json.keys())
            return response_json
        except (json.JSONDecodeError, AssertionError) as e:
            logger.error(f"Invalid OpenAI response: {e}")
            return {"signal": "NONE"}
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {"signal": "NONE"}

    def optimize_market_data(self, market_data: dict):
        print(market_data)
        return market_data
