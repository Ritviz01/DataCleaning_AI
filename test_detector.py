from app.services.file_detector import detect_file_type

print(detect_file_type("industry.csv"))
print(detect_file_type("sales.xlsx"))
print(detect_file_type("users.json"))
print(detect_file_type("data.parquet"))
print(detect_file_type("abc.xyz"))