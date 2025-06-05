- [ ] Approved


| Tag         | Importance  | Type    | Description                                                        | Enum                        | Example |
|-------------|-------------|---------|--------------------------------------------------------------------|-----------------------------|---------|
| kind        | required | string  | Kind of gift received.                          | money, food, goods          |food       |
| description | optional | string  | Further description of the give received.                          |                             |Just a bagel.         |
| value       | optional | float   | Positive decimal number. What is the estimated/ exact value of the gift received? Required if `currency` is given. |                             |4         |
| currency    | optional | string (ISO 4217)  | Currency code following the ISO 4217 standard. Required if `value` is given. |                                                  |                             |EUR       |
