# Property Search Agent

A smart property search tool that uses AI to generate Bayut URLs and scrape property data.

## Features

- 🧠 **AI-Powered URL Generation** - Converts natural language queries to Bayut search URLs
- 🕷️ **Web Scraping** - Extracts property data using Playwright
- ✨ **AI Summarization** - Provides polished property summaries with rental links
- 🎯 **Real-time Results** - Complete flow from query to final summary

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/settlelinecompany-commits/property-search-agent.git
cd property-search-agent
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
```bash
playwright install
```

### 4. Set Up OpenAI API Key
```bash
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_actual_key_here" > .env
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser
Visit: http://localhost:5000

## Usage

1. Enter a natural language property query (e.g., "3BR apartment in Dubai Marina under 90k monthly")
2. Click "Search Properties"
3. View the generated Bayut URL, raw scraper results, and AI summary
4. Click property links to view rentals on Bayut

## Example Queries

- "Studio in JVC around 5k monthly"
- "Villa in Downtown Dubai under 150k yearly"
- "2BR apartment in Business Bay under 8k monthly"
- "Penthouse in Palm Jumeirah under 200k yearly"

## Requirements

- Python 3.8+
- OpenAI API Key
- Internet connection

## Troubleshooting

- **"ModuleNotFoundError: No module named 'flask'"** → Run `pip install -r requirements.txt`
- **"Executable doesn't exist"** → Run `playwright install`
- **"No URL provided to scraper"** → Check your OpenAI API key in .env file