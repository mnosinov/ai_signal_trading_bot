import json
import re
from openai import AsyncOpenAI
from bot.config.config import Config
from bot.utils.logger import setup_logger
from pathlib import Path

logger = setup_logger("signals")
openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)


class SignalGenerator:
    CHATGPT_MODEL = "gpt-3.5-turbo"     # "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"

    async def forecast_probability(self, symbol, market_data: dict) -> dict:    # noqa
        # оптимизация jSON'a с klines
        optimized_market_data = self.optimize_market_data(market_data)
        print(optimized_market_data)

        # загружаем шаблон prompt'a из файла
        # Путь к prompt-файлу
        prompt_path = Path(__file__).parent.parent / "prompts" / "one_symbol_prompt.txt"

        # Загрузка шаблона
        with prompt_path.open("r", encoding="utf-8") as f:
            prompt_template = f.read()

        # Подстановка в шаблон (сжатый JSON)
        prompt = prompt_template \
            .replace("{symbol}", symbol) \
            .replace("{market_data}", json.dumps(optimized_market_data, separators=(',', ':')))

        try:
            response = await openai_client.chat.completions.create(
                model=SignalGenerator.CHATGPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1     # 0.3, 0.5
            )
            response_text = response.choices[0].message.content

            # Извлекаем JSON из текста (на случай если GPT добавил текст до/после)
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                response_json = json.loads(match.group())
                print(response_json)
            else:
                raise ValueError("JSON not found in response")
            logger.info(f"Generated signal: {response_json}")
            return {"signal": response_json}

        except (json.JSONDecodeError, AssertionError,  ValueError) as e:
            logger.error(f"Invalid OpenAI response: {e}")
            return {"signal": None}
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {"signal": None}

    def optimize_market_data(self, data: dict) -> list[dict]:     # noqa
        return [ {
            't': kline["time"],
            'o': kline["open"],
            'h': kline["high"],
            'l': kline["low"],
            'c': kline["close"],
            'v': kline["volume"],
        } for kline in data]
