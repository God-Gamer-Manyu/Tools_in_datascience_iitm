import math
import pandas as pd
import os

CSV_PATH = r"d:\Rtamanyu\_IIt Madras\2nd year\sem 1\Tools in datascience\Week 7\q-geospatial-python-proximity.csv"
CANDIDATE_LAT = 40.725734
CANDIDATE_LON = -73.934463
RADIUS_KM = 1.2


def haversine_km(lat1, lon1, lat2, lon2):
    # all args in decimal degrees
    # returns distance in kilometers
    R = 6371.0  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def load_data(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found at {path}")
    return pd.read_csv(path)


if __name__ == '__main__':
    df = load_data(CSV_PATH)

    # Ensure correct dtypes
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
    df['daily_customers'] = pd.to_numeric(df['daily_customers'], errors='coerce').fillna(0).astype(int)

    # Compute distances
    df['distance_km'] = df.apply(lambda row: haversine_km(CANDIDATE_LAT, CANDIDATE_LON, row['latitude'], row['longitude']), axis=1)

    # Filter within radius
    near = df[df['distance_km'] <= RADIUS_KM].copy()

    count_near = len(near)
    total_customers = near['daily_customers'].sum()

    # Round summed customers to nearest whole number (already int)
    total_customers_rounded = int(round(total_customers))

    print(f"Stores within {RADIUS_KM} km of candidate site ({CANDIDATE_LAT}, {CANDIDATE_LON}): {count_near}")
    print(f"Combined daily customers (rounded): {total_customers_rounded}")

    # Optional: print the store ids and distances for verification
    if count_near > 0:
        print("\nStores found (store_id, distance_km, daily_customers):")
        for _, r in near.sort_values('distance_km').iterrows():
            print(f"{r['store_id']}: {r['distance_km']:.3f} km, {r['daily_customers']} customers")
