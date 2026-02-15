"""Seed currencies and bootstrap exchange rates at startup."""

from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ISO 4217 currency list (subset of commonly used currencies)
CURRENCIES = [
    ("USD", "US Dollar", "$"),
    ("EUR", "Euro", "€"),
    ("GBP", "British Pound", "£"),
    ("JPY", "Japanese Yen", "¥"),
    ("CAD", "Canadian Dollar", "CA$"),
    ("AUD", "Australian Dollar", "A$"),
    ("CHF", "Swiss Franc", "CHF"),
    ("CNY", "Chinese Yuan", "¥"),
    ("SEK", "Swedish Krona", "kr"),
    ("NOK", "Norwegian Krone", "kr"),
    ("DKK", "Danish Krone", "kr"),
    ("NZD", "New Zealand Dollar", "NZ$"),
    ("MXN", "Mexican Peso", "$"),
    ("SGD", "Singapore Dollar", "S$"),
    ("HKD", "Hong Kong Dollar", "HK$"),
    ("KRW", "South Korean Won", "₩"),
    ("INR", "Indian Rupee", "₹"),
    ("BRL", "Brazilian Real", "R$"),
    ("ZAR", "South African Rand", "R"),
    ("RUB", "Russian Ruble", "₽"),
    ("TRY", "Turkish Lira", "₺"),
    ("PLN", "Polish Zloty", "zł"),
    ("CZK", "Czech Koruna", "Kč"),
    ("HUF", "Hungarian Forint", "Ft"),
    ("RON", "Romanian Leu", "lei"),
    ("IDR", "Indonesian Rupiah", "Rp"),
    ("MYR", "Malaysian Ringgit", "RM"),
    ("THB", "Thai Baht", "฿"),
    ("PHP", "Philippine Peso", "₱"),
    ("AED", "UAE Dirham", "د.إ"),
    ("SAR", "Saudi Riyal", "﷼"),
    ("ILS", "Israeli New Shekel", "₪"),
    ("ARS", "Argentine Peso", "$"),
    ("CLP", "Chilean Peso", "$"),
    ("COP", "Colombian Peso", "$"),
    ("PEN", "Peruvian Sol", "S/"),
    ("PKR", "Pakistani Rupee", "₨"),
    ("BDT", "Bangladeshi Taka", "৳"),
    ("EGP", "Egyptian Pound", "£"),
    ("NGN", "Nigerian Naira", "₦"),
    ("KES", "Kenyan Shilling", "KSh"),
    ("UAH", "Ukrainian Hryvnia", "₴"),
    ("BGN", "Bulgarian Lev", "лв"),
    ("HRK", "Croatian Kuna", "kn"),
    ("ISK", "Icelandic Króna", "kr"),
]


async def seed_currencies(session: AsyncSession) -> None:
    """Upsert ISO 4217 currencies. Safe to call multiple times."""
    await session.execute(
        text(
            """
            INSERT INTO currencies (code, name, symbol)
            VALUES (:code, :name, :symbol)
            ON CONFLICT (code) DO NOTHING
            """
        ),
        [{"code": code, "name": name, "symbol": symbol} for code, name, symbol in CURRENCIES],
    )
    await session.commit()


# Approximate USD-based rates (1 USD = X target).
# Used only to bootstrap an empty exchange_rates table so the UI works out of the box.
_BOOTSTRAP_RATES_USD: list[tuple[str, float]] = [
    ("EUR", 0.9200),
    ("GBP", 0.7900),
    ("JPY", 149.50),
    ("CAD", 1.3600),
    ("AUD", 1.5300),
    ("CHF", 0.8950),
    ("CNY", 7.2400),
    ("SEK", 10.40),
    ("NOK", 10.60),
    ("DKK", 6.8800),
    ("NZD", 1.6300),
    ("MXN", 17.10),
    ("SGD", 1.3400),
    ("HKD", 7.8200),
    ("KRW", 1320.0),
    ("INR", 83.10),
    ("BRL", 4.9700),
    ("ZAR", 18.60),
    ("PLN", 4.0200),
    ("CZK", 22.80),
    ("HUF", 355.0),
    ("RON", 4.5800),
    ("IDR", 15600.0),
    ("MYR", 4.6800),
    ("THB", 35.20),
    ("PHP", 56.50),
    ("AED", 3.6725),
    ("SAR", 3.7500),
    ("ILS", 3.7000),
    ("TRY", 30.50),
    ("UAH", 37.50),
    ("BGN", 1.7990),
]


async def seed_exchange_rates(session: AsyncSession) -> None:
    """Insert bootstrap USD exchange rates only when the table is completely empty.

    Safe to call multiple times — does nothing once any row exists.
    """
    import uuid as _uuid

    result = await session.execute(text("SELECT COUNT(*) FROM exchange_rates"))
    count = result.scalar_one()
    if count > 0:
        return

    today = date.today().isoformat()
    rows = [
        {"id": str(_uuid.uuid4()), "base": "USD", "target": target, "rate": rate, "date": today}
        for target, rate in _BOOTSTRAP_RATES_USD
    ]
    await session.execute(
        text(
            """
            INSERT INTO exchange_rates (id, base_currency, target_currency, rate, date)
            VALUES (:id, :base, :target, :rate, :date)
            ON CONFLICT (base_currency, target_currency, date) DO NOTHING
            """
        ),
        rows,
    )
    await session.commit()
