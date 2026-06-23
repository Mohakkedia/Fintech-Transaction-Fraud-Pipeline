import os
import csv
import random
from datetime import datetime, timedelta

def generate_data(output_dir="data", num_cardholders=1000, num_transactions=20000):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Generate Cardholders
    cardholder_ids = [f"CH_{i:04d}" for i in range(1, num_cardholders + 1)]
    cardholders = []
    names = ["John", "Emily", "Michael", "Sarah", "David", "Jessica", "James", "Ashley", "Robert", "Amanda", 
             "William", "Megan", "Joseph", "Rachel", "Charles", "Stephanie", "Thomas", "Nicole", "Daniel", "Elizabeth"]
    surnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", 
                "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    kyc_statuses = ["APPROVED", "APPROVED", "APPROVED", "PENDING", "REJECTED"]
    
    for ch_id in cardholder_ids:
        name = f"{random.choice(names)} {random.choice(surnames)}"
        risk_score = random.randint(300, 850) # Simulated credit risk score
        kyc = random.choice(kyc_statuses)
        # Daily limit between $200 and $5000
        daily_limit = random.choice([200, 500, 1000, 1500, 2000, 3000, 5000])
        cardholders.append([ch_id, name, risk_score, kyc, daily_limit])
        
    cardholder_file = os.path.join(output_dir, "raw_cardholder_profiles.csv")
    with open(cardholder_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["cardholder_id", "name", "credit_risk_score", "kyc_status", "daily_limit"])
        writer.writerows(cardholders)
    print(f"Generated {len(cardholders)} cardholder profiles at {cardholder_file}")
    
    # 2. Generate Transactions
    merchants = {
        "Grocery": ["SuperSaver", "FreshMart", "WholeFoodsCo", "DailyGrocer"],
        "Retail": ["TargetRun", "WalmartDirect", "NordstromStyle", "MacyShop"],
        "Entertainment": ["NetflixInc", "SpotifyMusic", "TicketMaster", "AMCTheaters"],
        "Gas/Travel": ["ShellGas", "ChevronStation", "UberRide", "DeltaAir"],
        "Digital Services": ["AmazonCloud", "GooglePlay", "AppleStore", "SteamGames"]
    }
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    start_date = datetime(2026, 1, 1)
    transactions = []
    chargebacks = []
    
    # Generate some regular transactions
    for i in range(1, num_transactions + 1):
        tx_id = f"TX_{i:06d}"
        ch_id = random.choice(cardholder_ids)
        category = random.choice(list(merchants.keys()))
        merchant = random.choice(merchants[category])
        merchant_id = f"M_{hash(merchant) % 10000:04d}"
        city = random.choice(cities)
        
        # Base transaction amount
        amount = round(random.uniform(5.0, 300.0), 2)
        
        # Add timestamp spread over 5 months
        seconds_offset = random.randint(0, 150 * 24 * 3600)
        timestamp = start_date + timedelta(seconds=seconds_offset)
        
        transactions.append([tx_id, ch_id, timestamp.strftime("%Y-%m-%d %H:%M:%S"), amount, category, merchant_id, merchant, city])
        
    # Inject Specific Fraud Patterns (to make dbt models interesting)
    
    # Fraud Pattern A: Velocity / High Frequency (Many transactions in short time)
    for j in range(1, 200):
        tx_index = num_transactions + j * 10
        ch_id = random.choice(cardholder_ids)
        base_time = start_date + timedelta(seconds=random.randint(0, 150 * 24 * 3600))
        city = random.choice(cities)
        
        # Generate 4 transactions within 3 minutes
        for k in range(4):
            tx_id = f"TX_VEL_{tx_index + k:06d}"
            timestamp = base_time + timedelta(seconds=k * 45)
            amount = round(random.uniform(80.0, 150.0), 2)
            category = "Digital Services"
            merchant = "SteamGames"
            merchant_id = "M_9999"
            transactions.append([tx_id, ch_id, timestamp.strftime("%Y-%m-%d %H:%M:%S"), amount, category, merchant_id, merchant, city])
            
    # Fraud Pattern B: Duplicate transactions (Same amount, same merchant, same card within 5 mins)
    for j in range(1, 150):
        tx_index = num_transactions + 3000 + j * 5
        ch_id = random.choice(cardholder_ids)
        base_time = start_date + timedelta(seconds=random.randint(0, 150 * 24 * 3600))
        amount = round(random.uniform(25.0, 75.0), 2)
        category = "Entertainment"
        merchant = "NetflixInc"
        merchant_id = "M_1111"
        city = random.choice(cities)
        
        # Standard transaction
        tx_id_1 = f"TX_DUP_{tx_index:06d}"
        timestamp_1 = base_time
        transactions.append([tx_id_1, ch_id, timestamp_1.strftime("%Y-%m-%d %H:%M:%S"), amount, category, merchant_id, merchant, city])
        
        # Duplicate transaction 2 minutes later
        tx_id_2 = f"TX_DUP_{tx_index+1:06d}"
        timestamp_2 = base_time + timedelta(minutes=2)
        transactions.append([tx_id_2, ch_id, timestamp_2.strftime("%Y-%m-%d %H:%M:%S"), amount, category, merchant_id, merchant, city])

    # Fraud Pattern C: Exceeding daily card limits
    for j in range(1, 100):
        tx_index = num_transactions + 6000 + j
        # Choose a cardholder with a low limit (e.g. $200)
        ch_profiles = [ch for ch in cardholders if ch[4] == 200]
        if not ch_profiles:
            ch_profiles = cardholders
        ch_id = random.choice(ch_profiles)[0]
        
        base_time = start_date + timedelta(seconds=random.randint(0, 150 * 24 * 3600))
        city = random.choice(cities)
        
        # Single transaction of $450 (which exceeds the $200 daily limit)
        tx_id = f"TX_LMT_{tx_index:06d}"
        amount = round(random.uniform(400.0, 600.0), 2)
        category = "Gas/Travel"
        merchant = "DeltaAir"
        merchant_id = "M_8888"
        transactions.append([tx_id, ch_id, base_time.strftime("%Y-%m-%d %H:%M:%S"), amount, category, merchant_id, merchant, city])

    # Sort transactions by timestamp
    transactions.sort(key=lambda x: x[2])
    
    tx_file = os.path.join(output_dir, "raw_transactions.csv")
    with open(tx_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "cardholder_id", "timestamp", "amount", "merchant_category", "merchant_id", "merchant_name", "city"])
        writer.writerows(transactions)
    print(f"Generated {len(transactions)} transactions at {tx_file}")

    # 3. Generate Chargebacks (disputed transactions)
    # We will dispute some velocity fraud, duplicate fraud, and a small percentage of regular ones
    disputed_txs = set()
    for tx in transactions:
        tx_id = tx[0]
        amount = tx[3]
        # High probability of chargeback for fraud patterns
        if "TX_VEL" in tx_id and random.random() < 0.85:
            disputed_txs.add(tx_id)
        elif "TX_DUP" in tx_id and random.random() < 0.65:
            disputed_txs.add(tx_id)
        elif "TX_LMT" in tx_id and random.random() < 0.40:
            disputed_txs.add(tx_id)
        elif amount > 250.0 and random.random() < 0.05: # 5% of large normal transactions
            disputed_txs.add(tx_id)
        elif random.random() < 0.005: # 0.5% baseline dispute rate
            disputed_txs.add(tx_id)
            
    for tx in transactions:
        tx_id = tx[0]
        if tx_id in disputed_txs:
            tx_time = datetime.strptime(tx[2], "%Y-%m-%d %H:%M:%S")
            # Dispute happens 1 to 14 days later
            dispute_time = tx_time + timedelta(days=random.randint(1, 14))
            dispute_type = random.choice(["FRAUDULENT", "FRAUDULENT", "FRAUDULENT", "UNRECOGNIZED", "BILLING_ERROR"])
            chargebacks.append([tx_id, dispute_time.strftime("%Y-%m-%d %H:%M:%S"), dispute_type])
            
    chargeback_file = os.path.join(output_dir, "raw_chargebacks.csv")
    with open(chargeback_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "dispute_timestamp", "dispute_category"])
        writer.writerows(chargebacks)
    print(f"Generated {len(chargebacks)} chargeback records at {chargeback_file}")

if __name__ == "__main__":
    generate_data()
