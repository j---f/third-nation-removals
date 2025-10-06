from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

def load_removals_data():
    """Load removals data from JSON file"""
    try:
        with open('data/removals.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route('/api/v1/removals')
def get_all_removals():
    """Get all removal data with metadata"""
    data = load_removals_data()
    return jsonify({
        "metadata": {
            "total_entries": len(data),
            "last_updated": os.path.getmtime('data/removals.json') if os.path.exists('data/removals.json') else None,
            "version": "1.0"
        },
        "data": data
    })

@app.route('/api/v1/removals/summary')
def get_summary():
    """Get summary statistics"""
    data = load_removals_data()

    # Count by destination country
    by_country = {}
    total_people = 0

    for entry in data:
        country = entry.get('destination_country', 'Unknown')
        by_country[country] = by_country.get(country, 0) + (entry.get('number_removed') or 0)
        if entry.get('number_removed'):
            total_people += entry['number_removed']

    return jsonify({
        "total_removals": len(data),
        "total_people": total_people,
        "by_destination_country": by_country,
        "ongoing_programs": len([e for e in data if e.get('ongoing', False)])
    })

@app.route('/api/v1/removals/country/<country>')
def get_by_country(country):
    """Get removals by destination country"""
    data = load_removals_data()
    filtered = [e for e in data if e.get('destination_country', '').lower() == country.lower()]
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(debug=True)