import random
import time
import logging
import requests
from datetime import datetime
from web3 import Web3, HTTPProvider
from eth_account import Account

# ============ НАЛАШТУВАННЯ ============
RPC_URL = "https://bsc-dataseed.binance.org/"
L1_BRIDGE_ADDRESS = Web3.to_checksum_address("0xF05F0e4362859c3331Cb9395CBC201E3Fa6757Ea")

# --- Режим 1: Вказати суму в BNB
SEND_MIN = 0.000064
SEND_MAX = 0.00012

# --- Режим 2: Відсоток від балансу
USE_PERCENT_MODE = False
PERCENT_MIN = 90
PERCENT_MAX = 95

SLEEP_MIN = 25
SLEEP_MAX = 65
RETRY_COUNT = 4
L2_GAS_LIMIT_PARAM = 200_000
GAS_LIMIT_FALLBACK = 300_000

USE_PROXY = True
USE_DRY_RUN = False
SHUFFLE_WALLETS = True
DEST_OVERRIDE = None

# ============ ЛОГІ ============
logging.basicConfig(
    filename="bridge_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
failed_log = open("failed_wallets.log", "a")

# ============ ABI ============
L1_BRIDGE_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_to", "type": "address"},
            {"internalType": "uint32",  "name": "_gas", "type": "uint32"},
            {"internalType": "bytes",   "name": "_data", "type": "bytes"}
        ],
        "name": "depositETHTo",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

# ============ ФУНКЦІЇ ============
def load_lines(path: str):
    try:
        with open(path, "r") as f:
            return [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        return []

def normalize_proxy(p: str) -> str:
    return p if p.startswith(("http://", "socks5://")) else "http://" + p

def make_web3(proxy_url: str | None):
    if proxy_url:
        sess = requests.Session()
        sess.proxies = {"http": proxy_url, "https": proxy_url}
        return Web3(HTTPProvider(RPC_URL, session=sess))
    return Web3(Web3.HTTPProvider(RPC_URL))

# ============ ЗАВАНТАЖЕННЯ ============
private_keys = load_lines("priv.txt")
if not private_keys:
    raise SystemExit("❌ priv.txt пустий або не знайдено.")

if SHUFFLE_WALLETS:
    random.shuffle(private_keys)

proxies = [normalize_proxy(p) for p in load_lines("proxy.txt")] if USE_PROXY else []

# ============ ГОЛОВНИЙ ЦИКЛ ============
for i, key in enumerate(private_keys, start=1):
    try:
        proxy_url = proxies[i-1] if USE_PROXY and i-1 < len(proxies) else None
        w3 = make_web3(proxy_url)

        if not w3.is_connected():
            print(f"❌ {i}) RPC недоступний (proxy={proxy_url}). Пропуск.")
            failed_log.write(f"{datetime.now()} | {key[:10]}... | RPC недоступний (proxy={proxy_url})\n")
            continue
        if proxy_url:
            print(f"🌐 Використовується проксі: {proxy_url}")

        acct = Account.from_key(key)
        sender = acct.address
        dest = DEST_OVERRIDE if DEST_OVERRIDE else sender
        bridge = w3.eth.contract(address=L1_BRIDGE_ADDRESS, abi=L1_BRIDGE_ABI)

        nonce = w3.eth.get_transaction_count(sender)
        balance = w3.from_wei(w3.eth.get_balance(sender), "ether")
        gas_price = w3.eth.gas_price
        gas_fee = w3.from_wei(gas_price * GAS_LIMIT_FALLBACK, 'ether')
        available = float(balance) - float(gas_fee)

        if available < SEND_MIN:
            print(f"⚠️ {i}) {sender}: Недостатній баланс ({balance:.6f} BNB), пропуск.")
            failed_log.write(f"{datetime.now()} | {sender} | Недостатній баланс: {balance:.6f} BNB\n")
            continue

        if USE_PERCENT_MODE:
            percent = random.uniform(PERCENT_MIN, PERCENT_MAX)
            send_amount = round(available * (percent / 100), 6)
        else:
            send_amount = round(random.uniform(SEND_MIN, min(SEND_MAX, available)), 6)

        call = bridge.functions.depositETHTo(dest, L2_GAS_LIMIT_PARAM, b"")
        tx_data = call.build_transaction({
            "from": sender,
            "nonce": nonce,
            "value": w3.to_wei(send_amount, "ether"),
            "gasPrice": gas_price,
        })

        try:
            tx_data["gas"] = w3.eth.estimate_gas(tx_data)
        except:
            tx_data["gas"] = GAS_LIMIT_FALLBACK

        if USE_DRY_RUN:
            print(f"🔎 {i}) {sender}: DRY-RUN | {send_amount} BNB | Баланс: {balance:.4f}")
            continue

        success = False
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                signed = w3.eth.account.sign_transaction(tx_data, private_key=key)
                tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                tx_url = f"https://bscscan.com/tx/{w3.to_hex(tx_hash)}"
                mode = f"{percent:.2f}%" if USE_PERCENT_MODE else f"{send_amount} BNB"
                print(f"✅ {i}) {sender}: {mode} → TX: {tx_url}")
                success = True
                break
            except Exception as e:
                print(f"❌ Спроба {attempt} | {sender} | {e}")
                time.sleep(2)

        if not success:
            msg = f"{datetime.now()} | {sender} | ❌ ВСІ {RETRY_COUNT} СПРОБ НЕВДАЛІ\n"
            failed_log.write(msg)
            print(msg)

        delay = random.randint(SLEEP_MIN, SLEEP_MAX)
        print(f"⏳ Затримка {delay} сек...\n")
        time.sleep(delay)

    except Exception as ex:
        failed_log.write(f"{datetime.now()} | {sender} | КРИТИЧНА ПОМИЛКА: {ex}\n")
        print(f"🚫 {i}) {sender} | КРИТИЧНА ПОМИЛКА: {ex}")
        continue

failed_log.close()
