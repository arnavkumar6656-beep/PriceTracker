import json
import os
import re
import sys
import asyncio
import concurrent.futures
import traceback
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)

SELECTORS_FILE = os.path.join(os.path.dirname(__file__), 'selectors.json')
with open(SELECTORS_FILE, 'r') as f:
    SELECTORS = json.load(f)

def get_site_config(url: str):
    domain = urlparse(url).netloc.lower()
    if 'amazon.in' in domain:
        return SELECTORS.get('amazon.in')
    elif 'flipkart.com' in domain:
        return SELECTORS.get('flipkart.com')
    elif 'croma.com' in domain:
        return SELECTORS.get('croma.com')
    return None

def determine_site(url: str):
    domain = urlparse(url).netloc.lower()
    if 'amazon.in' in domain: return 'Amazon'
    if 'flipkart.com' in domain: return 'Flipkart'
    if 'croma.com' in domain: return 'Croma'
    return 'Unknown'

def extract_price(price_str: str) -> float:
    if not price_str:
        return None
    clean_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(clean_str)
    except ValueError:
        return None

async def _scrape_product_internal(url: str):
    logger.info(f"[Scraper] Starting scrape for URL: {url}")
    config = get_site_config(url)
    if not config:
        logger.warning(f"[Scraper] Scraping failed: Unsupported website domain for URL: {url}")
        return {"error": "Unsupported website"}

    logger.info(f"[Scraper] Detected site configuration: {config['site_name']}")
    async with async_playwright() as p:
        logger.info("[Scraper] Launching Playwright browser (headless=False)")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            logger.info(f"[Scraper] Navigating to {url}")
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
            logger.info("[Scraper] Page loaded.")
            
            # Dismiss popup via Escape keyboard shortcut or button click
            try:
                logger.info("[Scraper] Dismissing Flipkart popup...")
                await page.keyboard.press("Escape")
                try:
                    await page.click("button._2KpZ6l._2doB4z", timeout=2000)
                except:
                    pass
                logger.info("[Scraper] Closed/dismissed popup.")
            except Exception as e:
                logger.info(f"[Scraper] No popup detected or dismissed: {e}")
                
            logger.info("[Scraper] Extracting elements...")
            
            title = None
            title_sel = config.get('title')
            try:
                logger.info(f"[Scraper] Querying title selector: '{title_sel}'")
                title_el = await page.wait_for_selector(title_sel, timeout=5000)
                if title_el:
                    title = await title_el.inner_text()
                    title = title.strip()
                    logger.info(f"[Scraper] Extracted title: '{title}'")
                else:
                    logger.warning(f"[Scraper] Title element not found for selector: '{title_sel}'")
                    html_snippet = await page.content()
                    print(f"SELECTOR FAILURE DETECTED:")
                    print(f"  Selector: {title_sel}")
                    print(f"  Current URL: {page.url}")
                    print(f"  HTML Snippet (first 1000 chars of body):")
                    try:
                        body = await page.query_selector("body")
                        body_html = await body.inner_html() if body else html_snippet
                        print(body_html[:1000])
                    except Exception:
                        print(html_snippet[:1000])
            except Exception as e:
                logger.error(f"[Scraper] Failed to find title for {url}: {e}")
                traceback.print_exc()
                await page.screenshot(path="debug.png")
                html_snippet = await page.content()
                print(f"SELECTOR FAILURE DETECTED (EXCEPTION):")
                print(f"  Selector: {title_sel}")
                print(f"  Current URL: {page.url}")
                print(f"  HTML Snippet (first 1000 chars of body):")
                try:
                    body = await page.query_selector("body")
                    body_html = await body.inner_html() if body else html_snippet
                    print(body_html[:1000])
                except Exception:
                    print(html_snippet[:1000])
                    
            if not title:
                logger.info("[Scraper] Title is empty. Falling back to default 'h1' element...")
                try:
                    h1_el = await page.query_selector("h1")
                    if h1_el:
                        title = await h1_el.inner_text()
                        title = title.strip()
                        logger.info(f"[Scraper] Fallback extracted title: '{title}'")
                except Exception as e:
                    logger.error(f"[Scraper] Fallback 'h1' title extraction failed: {e}")
                    traceback.print_exc()
            
            if title:
                title = re.sub(r'\s*\.\.\.\s*more\s*$', '', title, flags=re.IGNORECASE)
                title = re.sub(r'\.\.\.$', '', title)
                title = title.strip()

            price_str = None
            price = None
            logger.info(f"[Scraper] Querying price selectors...")
            for selector in config['price']:
                try:
                    logger.info(f"[Scraper] Testing price selector: '{selector}'")
                    el = await page.query_selector(selector)
                    if el:
                        price_str = await page.evaluate('(element) => element.textContent', el)
                        if price_str:
                            price_str = price_str.strip()
                            parsed_val = extract_price(price_str)
                            if parsed_val is not None:
                                price = parsed_val
                                logger.info(f"[Scraper] Found price string: '{price_str}' -> parsed value: ₹{price}")
                                break
                            else:
                                logger.info(f"[Scraper] Found price element but extracted text '{price_str}' could not be parsed to float.")
                    else:
                        logger.warning(f"[Scraper] Selector returned null: {selector}")
                except Exception as e:
                    logger.debug(f"[Scraper] Exception checking selector '{selector}': {e}")
                    traceback.print_exc()
                    continue
            
            if price is None:
                try:
                    logger.info("[Scraper] Running fallback price extractor using font-size heuristics...")
                    heuristic_price_str = await page.evaluate(r'''() => {
                        const elements = Array.from(document.querySelectorAll('div, span, p'));
                        const candidates = [];
                        for (const el of elements) {
                            const text = (el.innerText || '').trim();
                            if (/^₹\s*\d+(?:,\d+)*(?:\.\d+)?$/.test(text)) {
                                const num = parseFloat(text.replace(/[^\d.]/g, ''));
                                if (!isNaN(num) && num > 0) {
                                    const style = window.getComputedStyle(el);
                                    const fontSize = parseFloat(style.fontSize) || 0;
                                    if (style.display !== 'none' && style.visibility !== 'hidden' && el.offsetWidth > 0) {
                                        candidates.push({ text, fontSize });
                                    }
                                }
                            }
                        }
                        candidates.sort((a, b) => b.fontSize - a.fontSize);
                        return candidates.length > 0 ? candidates[0].text : null;
                    }''')
                    if heuristic_price_str:
                        logger.info(f"[Scraper] Heuristics found price candidate text: '{heuristic_price_str}'")
                        price = extract_price(heuristic_price_str)
                except Exception as e:
                    logger.error(f"[Scraper] Heuristics price extraction failed: {e}")
                    traceback.print_exc()
            
            if price is None:
                logger.warning(f"[Scraper] Failed to extract a valid price for URL: {url}")
                html_snippet = await page.content()
                print(f"SELECTOR FAILURE DETECTED (PRICE):")
                print(f"  Selectors Tested: {config['price']}")
                print(f"  Current URL: {page.url}")
                print(f"  HTML Snippet (first 1000 chars of body):")
                try:
                    body = await page.query_selector("body")
                    body_html = await body.inner_html() if body else html_snippet
                    print(body_html[:1000])
                except Exception:
                    print(html_snippet[:1000])
                await page.screenshot(path="debug.png")

            image_url = None
            try:
                img_selector = config['image']
                logger.info(f"[Scraper] Querying image selector: '{img_selector}'")
                el = await page.query_selector(img_selector)
                if el:
                    image_url = await el.get_attribute('src')
                    logger.info(f"[Scraper] Extracted image URL: '{image_url}'")
                else:
                    logger.info(f"[Scraper] Image element not found for selector: '{img_selector}'")
            except Exception as e:
                logger.debug(f"[Scraper] Exception extracting image: {e}")
                traceback.print_exc()
                
            if not image_url and 'flipkart.com' in url:
                try:
                    logger.info("[Scraper] Running fallback image extractor for Flipkart...")
                    images = await page.query_selector_all("img")
                    for img in images:
                        src = await img.get_attribute("src")
                        srcset = await img.get_attribute("srcset")
                        img_url = src or srcset
                        if img_url and "rukminim" in img_url and "image/" in img_url:
                            if srcset:
                                first_url = srcset.split()[0]
                                image_url = first_url
                            else:
                                image_url = src
                            if image_url:
                                logger.info(f"[Scraper] Fallback found image URL: {image_url}")
                                break
                except Exception as e:
                    logger.error(f"[Scraper] Fallback image extraction failed: {e}")
                    traceback.print_exc()

            await page.screenshot(path="debug.png")
            logger.info("[Scraper] Saved debug screenshot to debug.png")

            result = {
                "title": title,
                "price": price,
                "image_url": image_url,
                "site": config['site_name']
            }
            logger.info(f"[Scraper] Scraping completed successfully for {url}. Result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"[Scraper] Error scraping {url}: {e}")
            traceback.print_exc()
            try:
                await page.screenshot(path="debug.png")
            except:
                pass
            return {"error": str(e)}
        finally:
            await browser.close()
            logger.info("[Scraper] Browser closed.")

async def scrape_product(url: str):
    if sys.platform == 'win32':
        logger.info("[Scraper] Win32 environment detected. Offloading scrape to a separate thread with ProactorEventLoop.")
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, _scrape_in_thread, url)
    else:
        return await _scrape_product_internal(url)

def _scrape_in_thread(url: str):
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_scrape_product_internal(url))
    finally:
        loop.close()
