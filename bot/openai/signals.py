import json
from openai import AsyncOpenAI
from bot.config.config import Config
from bot.utils.logger import setup_logger

logger = setup_logger("signals")
client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)


class SignalGenerator:
    @staticmethod
    async def generate_signal(market_data: dict) -> dict:
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
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
