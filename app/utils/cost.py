import tiktoken

from app.core import config


def count_tokens(text):
    return len(tiktoken.get_encoding("cl100k_base").encode(text))


def cost_usd(model, input_tokens, output_tokens=0):
    price_in, price_out = config.PRICES.get(model, (0, 0))
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000
