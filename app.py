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
Convert this rental query to a complete Bayut URL: "{user_query}"

Use this format:
https://www.bayut.com/to-rent/{{beds}}-{{property_type}}/{{location}}/{{area}}/?rent_frequency={{freq}}&price_min={{min}}&price_max={{max}}&baths_in={{baths}}

Examples:
"3BR apartment in Dubai Marina under 90k monthly"
→ https://www.bayut.com/to-rent/3-bedroom-apartments/dubai/dubai-marina/?rent_frequency=monthly&price_max=90000

"2BR villa in Downtown Dubai 5k-15k monthly with 2 baths"
→ https://www.bayut.com/to-rent/2-bedroom-villas/dubai/downtown-dubai/?rent_frequency=monthly&price_min=5000&price_max=15000&baths_in=2

"Studio in JVC around 5k monthly"
→ https://www.bayut.com/to-rent/studio-apartments/dubai/jumeirah-village-circle/?rent_frequency=monthly&price_max=5000

"Villa in Abu Dhabi under 150k yearly"
→ https://www.bayut.com/to-rent/villas/abu-dhabi/abu-dhabi-city/?rent_frequency=yearly&price_max=150000

Return ONLY the complete Bayut URL with all relevant parameters.
"""

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a URL construction agent for Bayut property searches. Return only the URL."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        # Extract URL from response
        if result.startswith('http'):
            url = result.split('\n')[0].strip()
        else:
            import re
            url_match = re.search(r'https://[^\s]+', result)
            url = url_match.group(0) if url_match else result
        
        # Debug logging
        print(f"🔍 DEBUG: Generated URL: {url}")
        print(f"🔍 DEBUG: URL length: {len(url)}")
        
        return jsonify({
            'success': True,
            'data': {
                'url': url,
                'raw_query': user_query
            }
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
        
        # Debug logging
        print(f"🔍 DEBUG: Received URL: {url}")
        print(f"🔍 DEBUG: URL length: {len(url)}")
        print(f"🔍 DEBUG: URL type: {type(url)}")
        print(f"🔍 DEBUG: Request JSON: {request.json}")
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'No URL provided to scraper'
            })
        
        # Import and run the existing scraper
        from scraper import scrape_bayut_url
        
        print(f"🔍 DEBUG: Calling scraper with URL: {url}")
        
        # Call the scraper function with the URL
        results = scrape_bayut_url(url)
        
        print(f"🔍 DEBUG: Scraper returned {len(results)} results")
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        print(f"🔍 DEBUG: Error in scraper: {str(e)}")
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
            model="gpt-4o-mini",
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