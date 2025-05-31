# file_operations.py

import csv
import json

def save_as_csv(path, data, headers):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def save_as_html(path, data, headers):
    with open(path, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Directory Listing</title>")
        f.write("<style>body {font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px;} "
                "table {border-collapse: collapse; width: 100%; margin-top: 20px;} "
                "th, td {border: 1px solid #ddd; padding: 8px; text-align: left;} "
                "th {background-color: #f2f2f2;} "
                "tr:nth-child(even) {background-color: #f9f9f9;} "
                "tr:hover {background-color: #e2e2e2;}"
                "</style>")
        f.write("</head><body><h1>Directory Listing</h1><table><tr>")
        for header in headers: f.write(f"<th>{header}</th>")
        f.write("</tr>")
        for row in data:
            f.write("<tr>")
            for header in headers: f.write(f"<td>{row.get(header, '')}</td>")
            f.write("</tr>")
        f.write("</table></body></html>")

def save_as_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)