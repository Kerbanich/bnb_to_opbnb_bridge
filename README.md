
# BNB → opBNB Bridge Script

This Python script automates bridging BNB from the **BNB Chain** to **opBNB** using the official [opBNB bridge contract](https://bscscan.com/address/0xF05F0e4362859c3331Cb9395CBC201E3Fa6757Ea).

🌐 **Bridge Website**: [https://opbnb-bridge.bnbchain.org/deposit](https://opbnb-bridge.bnbchain.org/deposit)

---

## ✅ Features

- Private key-based wallet control
- Proxy support
- Send either:
  - fixed BNB amount, or
  - a percentage of current balance (e.g., 90–95%)
- Random delay between wallets
- Dry-run mode (safe simulation)
- Dynamic gas price from BNB network
- Retry logic and error logging
- Logs failed wallets to `failed_wallets.log`

---

## ⚙️ Quick Start (English)

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate it:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run script:**
   ```bash
   python main.py
   ```

---

## 📂 Files

- `priv.txt` – list of private keys (one per line)
- `proxy.txt` – list of proxies (optional)
- `requirements.txt` – Python libraries required

---

## 🇷🇺 Скрипт моста BNB → opBNB

Этот скрипт на Python автоматически бриджит BNB из сети **BNB Chain** в **opBNB** через официальный [смарт-контракт моста](https://bscscan.com/address/0xF05F0e4362859c3331Cb9395CBC201E3Fa6757Ea).

🌐 **Сайт моста**: [https://opbnb-bridge.bnbchain.org/deposit](https://opbnb-bridge.bnbchain.org/deposit)

---

### ✅ Возможности

- Работа с кошельками по приватным ключам
- Поддержка прокси
- Отправка:
  - фиксированной суммы BNB
  - или процента от баланса (например, 90–95%)
- Случайная задержка между кошельками
- Dry-run режим (тест без транзакций)
- Динамическая цена газа с сети BNB
- Повторные попытки при ошибках
- Лог неудачных кошельков в `failed_wallets.log`

---

### ⚙️ Инструкция запуска

1. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   ```

2. **Активируйте его:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите скрипт:**
   ```bash
   python main.py
   ```

---

---

## ⚙️ Configuration Parameters

You can adjust these values at the top of the `bnb_to_opbnb_bridge.py` script:

| Parameter         | Description |
|------------------|-------------|
| `USE_PERCENT_MODE` | If `True`, sends a percentage of the wallet balance instead of a fixed range |
| `PERCENT_MIN` / `PERCENT_MAX` | The min and max percentage of the balance to send (used only if `USE_PERCENT_MODE = True`) |
| `SEND_MIN` / `SEND_MAX` | Minimum and maximum amount in BNB to send (used if `USE_PERCENT_MODE = False`) |
| `USE_PROXY`      | If `True`, uses proxy from `proxy.txt` file (supports http/socks5) |
| `USE_DRY_RUN`    | If `True`, script only simulates transactions without sending real ones |

---
