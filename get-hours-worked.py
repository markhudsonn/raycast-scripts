#!/usr/local/bin/python3.12

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Get hours worked
# @raycast.mode fullOutput

# Optional parameters:
# @raycast.icon ⏳

# Documentation:
# @raycast.author markhuds
# @raycast.authorURL https://raycast.com/markhuds

import os
import requests
from datetime import datetime
from collections import defaultdict

from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
HOURLY_RATE = float(os.getenv("HOURLY_RATE"))


def get_monthly_hours_report():

  headers = {
      "Authorization": "Bearer " + NOTION_API_KEY,
      "Notion-Version": "2022-06-28",
      "Content-Type": "application/json"
  }

  url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
  has_more = True
  next_cursor = None
  data = {"results": []}

  while has_more:
    payload = {}
    if next_cursor:
      payload["start_cursor"] = next_cursor

    response = requests.post(url, headers=headers, json=payload)
    page_data = response.json()
    data["results"].extend(page_data["results"])
    has_more = page_data.get("has_more", False)
    next_cursor = page_data.get("next_cursor")

  monthly_hours = defaultdict(float)
  for item in data["results"]:
    date_str = item["properties"]["Date"]["title"][0]["text"]["content"]
    date_obj = datetime.strptime(date_str, "%d/%m/%y")
    month_year_key = date_obj.strftime("%Y-%m")
    monthly_hours[month_year_key] += item["properties"]["Hours"]["number"]

  header = f"{'Month-Year':<10} | {'Hours Worked':<12} | {'Pay':<10}"
  print(header)
  print("-" * len(header))
  total_hours = sum(monthly_hours.values())
  total_pay = total_hours * HOURLY_RATE
  for month_year_key, hours in sorted(monthly_hours.items()):
    print(f"{month_year_key:<10} | {hours:<12.2f} | £{hours * HOURLY_RATE:<10.2f}")
  print("-" * len(header))
  print(f"{'Total':<10} | {total_hours:<12.2f} | £{total_pay:<10.2f}")


get_monthly_hours_report()
