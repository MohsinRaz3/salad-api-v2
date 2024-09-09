voices_id_list = [
  {"name": "Sarah", "id": "EXAVITQu4vr4xnSDxMaL"},
  {"name": "Dan", "id": "HRtOQGUGcbYfuAAouyYR"},
  {"name": "Laura", "id": "FGY2WhTYpPnrIDTdsKH5"},
  {"name": "Charlie", "id": "IKne3meq5aSn9XLyUdCD"},
  {"name": "George", "id": "JBFqnCBsd6RMkjVDRZzb"},
  {"name": "Callum", "id": "N2lVS1w4EtoT3dr4eOWO"},
  {"name": "Liam", "id": "TX3LPaxmHKxFdv7VOQHJ"},
  {"name": "Charlotte", "id": "XB0fDUnXU5powFXDhCwa"},
  {"name": "Alice", "id": "Xb7hH8MSUJpSbSDYk0k2"},
  {"name": "Matilda", "id": "XrExE9yKIg1WjnnlVkGX"},
  {"name": "Will", "id": "bIHbv24MWmeRgasZH58o"},
  {"name": "Jessica", "id": "cgSgspJ2msm6clMCkdW9"},
  {"name": "Eric", "id": "cjVigY5qzO86Huf0OWal"},
  {"name": "Chris", "id": "iP95p4xoKVk53GoZ742B"},
  {"name": "Brian", "id": "nPczCjzI2devNBz1zQrb"},
  {"name": "Daniel", "id": "onwK4e9ZLuTAKqWW03F9"},
  {"name": "Lily", "id": "pFZP5JQG7iQjIQuC4Bku"},
  {"name": "Bill", "id": "pqHfZKP75CvOlQylNhV4"}
]


def get_voice_id_by_name( name):
    for voice in voices_id_list:
        if voice["name"] == name:
            return voice["id"]
    return None

