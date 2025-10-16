from playwright.sync_api import sync_playwright

pw = sync_playwright().start()

browser = pw.firefox.launch(
    headless=True,
    #slow_mo=2000,
)

page=browser.new_page()
page.goto("https://www.bayut.com/to-rent/villas/uae/?rent_frequency=monthly&price_min=5000&price_max=6000")


# Get all the links and extract unique URLs in one go
links = page.locator("xpath=//a[contains(@href, 'property/details') and not(ancestor::div[@aria-label='Recommended search hits'])]").all()

urls = list(set(link.get_attribute("href") for link in links if link.get_attribute("href")))

print(f"Found {len(urls)} unique property links:")
for i, url in enumerate(urls):
    print(f"{i+1}. {url}")

# Now visit each property detail page
for i, url in enumerate(urls):
    print(f"\n{'='*50}")
    print(f"PROPERTY {i+1}: {url}")
    print(f"{'='*50}")
    
    # Navigate to the property detail page
    page.goto(f"https://www.bayut.com{url}")
    
    # Extract the 3 specific containers
    try:
        # 1. Pricing
        pricing = page.locator("xpath=//div[contains(@class, 'fc84e39c') and contains(@class, 'cd769dae')]").text_content()
        print(f"Pricing: {pricing}")
    except:
        print("Pricing: Not found")
    
    try:
        # 2. Property Header (Location)
        location = page.locator("xpath=//div[@aria-label='Property header']").text_content()
        print(f"Location: {location}")
    except:
        print("Location: Not found")
    
    try:
        # 3. Property Description
        description = page.locator("xpath=//div[@aria-label='Property description']").text_content()
        print(f"Description: {description}")
    except:
        print("Description: Not found")
    
    print(f"\n{'-'*30}")

browser.close()