#!/usr/bin/env python3
import requests
from pathlib import Path

# Base API URL
BASE_URL = "https://www.eci.gov.in/eci-backend/public/ER/s04/SIR"

def get_states():
    resp = requests.get(f"{BASE_URL}/state")
    resp.raise_for_status()
    return resp.json()

def get_districts(state_id):
    resp = requests.get(f"{BASE_URL}/district", params={"stateId": state_id})
    resp.raise_for_status()
    return resp.json()

def get_acs(state_id, district_id):
    resp = requests.get(f"{BASE_URL}/AC", params={
        "stateId": state_id,
        "districtId": district_id
    })
    resp.raise_for_status()
    return resp.json()

def download_roll(state_id, district_id, ac_no, output_path: Path):
    params = {"stateId": state_id, "districtId": district_id, "acNo": ac_no}
    resp = requests.get(f"{BASE_URL}/roll", params=params, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"✅ Saved ZIP to {output_path.resolve()}")

if __name__ == "__main__":
    out_file = Path("valmikinagar.zip")

    # Labels you want
    STATE_LABEL    = "Bihar"
    DISTRICT_LABEL = "West Champaran"
    AC_LABEL       = "Valmikinagar"

    # 1. Pick State
    states = get_states()
    state = next(s for s in states if s["stateName"] == STATE_LABEL)

    # 2. Pick District
    districts = get_districts(state["stateId"])
    district = next(d for d in districts if d["districtName"] == DISTRICT_LABEL)

    # 3. Pick Assembly Constituency
    acs = get_acs(state["stateId"], district["districtId"])
    ac = next(a for a in acs if a["acName"] == AC_LABEL)

    # 4. Download ZIP
    download_roll(state["stateId"], district["districtId"], ac["acNo"], out_file)
