from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import json
import subprocess
import sys

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse-query', methods=['POST'])
def parse_query():
    """Parse user query and generate Bayut URL using OpenAI"""
    try:
        user_query = request.json.get('query', '')
        
        # OpenAI prompt for URL generation
        prompt = f"""
You are an information-extraction and URL-construction agent for UAE rental searches on Bayut. Your job is to:
Parse a natural-language rental query into a strict JSON object.
Normalize beds/baths, price, and rent frequency.
Construct a valid Bayut rent URL from that JSON.
Return only a final JSON object with both the parsed fields and the URL.

SCOPE (RENTAL ONLY)
Handle rent cases only (no buy/sale).
Ignore furnishing/amenities/parking/pets unless they influence price or frequency. Do not include them in output.
Work with Dubai/UAE locations in free text, but URL path remains /uae/ (location filtering handled downstream).

OUTPUT FORMAT (STRICT)
Return exactly one JSON object with these keys (and nothing else):
{{
  "parsed": {{
    "intent": "rent",
    "locations": ["<string>", "..."],            // default ["UAE"]
    "property_type": "apartment|villa|townhouse|penthouse|hotel_apartment|villa_compound|land|building|floor",
    "beds": "studio|1|2|3|4|5|6|7|8+|any",
    "baths": "1|2|3|4|5|6+|any",
    "rent_frequency": "yearly|monthly|weekly|daily|any",
    "price_min_aed": 0,
    "price_max_aed": 0,
    "raw_query": "<the original user text>"
  }},
  "url": "<final bayut url>"
}}

DEFAULTS (WHEN MISSING OR AMBIGUOUS)
intent: "rent" (fixed)
locations: ["UAE"]
property_type: "apartment"
beds: "any"
baths: "any"
rent_frequency: "yearly" (unless text clearly implies monthly/weekly/daily; if user says "either/any", set "any")
price_min_aed / price_max_aed: 0 (omit from URL when zero)

User Query: {user_query}

Return only the JSON object:
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a URL construction agent for Bayut property searches. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Try to parse the JSON response
        try:
            parsed_result = json.loads(result)
            return jsonify({
                'success': True,
                'data': parsed_result
            })
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Failed to parse OpenAI response as JSON',
                'raw_response': result
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/scrape', methods=['POST'])
def scrape():
    """Use existing Playwright scraper to get property data"""
    try:
        url = request.json.get('url', '')
        
        # Import and run the existing scraper
        from scraper import scrape_bayut_url
        
        # Call the scraper function with the URL
        results = scrape_bayut_url(url)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/summarize', methods=['POST'])
def summarize():
    """Summarize scraped results using OpenAI"""
    try:
        raw_data = request.json.get('data', [])
        user_query = request.json.get('original_query', '')
        
        prompt = f"""
You are a property rental assistant. Summarize the following scraped property data in a helpful, concise way for the user.

Original User Query: {user_query}

Scraped Property Data:
{json.dumps(raw_data, indent=2)}

Please provide:
1. A brief summary of what was found
2. Key highlights (best deals, locations, etc.)
3. Direct links to each property for the user to view/rent

Format your response as a clean, user-friendly summary with clickable property links.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful property rental assistant. Provide clear, concise summaries with actionable information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)