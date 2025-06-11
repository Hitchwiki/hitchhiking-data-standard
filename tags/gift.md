- [x] Approved


| Tag         | Importance  | Type    | Description                                                        | Enum                        | Example |
|-------------|-------------|---------|--------------------------------------------------------------------|-----------------------------|---------|
| kind        | required | string  | Kind of gift received.                          | money, food, goods          |food       |
| description | optional | string  | Further description of the give received.                          |                             |Just a bagel.         |
| price       | `[amount, currency]`   | optional       | Price array. If used, both values are required. `currency` uses ISO 4217 or common crypto codes (BTC, SATS). `amount` is a positive decimal number. What is the estimated/ exact value of the gift received? |             | `["50", "USD"]`, `["10000", "SATS"]`|
