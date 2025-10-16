from playwright.sync_api import sync_playwright
import json

def handler(request):
    """Vercel serverless function handler"""
    
    # Get URL from query parameters
    url = request.get('query', {}).get('url', 'https://www.bayut.com/to-rent/villas/uae/?rent_frequency=monthly&price_min=5000&price_max=6000')
    
    try:
        pw = sync_playwright().start()
        
        browser = pw.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        
        # Get all the links and extract unique URLs
        links = page.locator("xpath=//a[contains(@href, 'property/details') and not(ancestor::div[@aria-label='Recommended search hits'])]").all()
        urls = list(set(link.get_attribute("href") for link in links if link.get_attribute("href")))
        
        results = []
        
        # Visit each property detail page
        for i, url in enumerate(urls[:3]):  # Limit to 3 for demo
            print(f"Processing property {i+1}: {url}")
            
            # Navigate to the property detail page
            page.goto(f"https://www.bayut.com{url}")
            
            property_data = {
                "url": f"https://www.bayut.com{url}",
                "pricing": None,
                "location": None,
                "description": None
            }
            
            # Extract the 3 specific containers
            try:
                # 1. Pricing
                pricing = page.locator("xpath=//div[contains(@class, 'fc84e39c') and contains(@class, 'cd769dae')]").text_content()
                property_data["pricing"] = pricing
            except:
                property_data["pricing"] = "Not found"
            
            try:
                # 2. Property Header (Location)
                location = page.locator("xpath=//div[@aria-label='Property header']").text_content()
                property_data["location"] = location
            except:
                property_data["location"] = "Not found"
            
            try:
                # 3. Property Description
                description = page.locator("xpath=//div[@aria-label='Property description']").text_content()
                property_data["description"] = description
            except:
                property_data["description"] = "Not found"
            
            results.append(property_data)
        
        browser.close()
        pw.stop()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'total_properties': len(results),
                'properties': results
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
