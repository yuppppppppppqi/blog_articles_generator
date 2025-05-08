import os
import re
import time
import json
import requests
from playwright.sync_api import sync_playwright
from PIL import Image, ImageEnhance
import random
import csv

REVIEW_SELECTORS = [
    'div[jscontroller="e6Mltc"] .jftiEf',
    'div[data-review-id]',
    '.jftiEf',
    '.section-review-content',
    '.wiI7pd',
]

def extract_place_id(url):
    match = re.search(r"place_id:([\w-]+)", url)
    return match.group(1) if match else url

def extract_reviews_from_url(page, url, max_reviews=20, max_scrolls=10):
    page.goto(url + "&hl=en")
    try:
        page.wait_for_load_state("networkidle", timeout=90000)
    except Exception as e:
        print(f"    [ERROR] Timeout or error loading page for URL: {url}\n    {e}")
        return []
    time.sleep(2)
    buttons = page.locator('button')
    for i in range(buttons.count()):
        text = buttons.nth(i).text_content()
        if text and ("review" in text.lower() or "รีวิว" in text.lower()):
            try:
                buttons.nth(i).click()
                time.sleep(3)
                break
            except Exception:
                pass
    reviews_to_save = []
    seen = set()
    for scroll in range(max_scrolls):
        for selector in REVIEW_SELECTORS:
            reviews = page.locator(selector)
            count = reviews.count()
            if count >= 1:
                for i in range(count):
                    try:
                        review_text = reviews.nth(i).text_content()
                        review_text_clean = review_text.strip() if review_text else ''
                        if review_text_clean and review_text_clean not in seen:
                            reviews_to_save.append({"text": review_text_clean})
                            seen.add(review_text_clean)
                            if len(reviews_to_save) >= max_reviews:
                                break
                    except Exception:
                        pass
                if len(reviews_to_save) >= max_reviews:
                    break
        if len(reviews_to_save) >= max_reviews:
            break
        try:
            page.mouse.wheel(0, 2000)
            time.sleep(2)
        except Exception:
            pass
    return reviews_to_save

def get_high_res_url(src):
    return re.sub(r'w\d+-h\d+', 'w1200-h900', src)

def normalize_url(url):
    return url.split('=')[0]

def save_images_for_url(page, url, shop_dir, max_gallery_images=5):
    os.makedirs(shop_dir, exist_ok=True)
    page.goto(url + "&hl=en")
    page.wait_for_load_state("networkidle")
    img_candidates = page.locator('img[src*="lh3.googleusercontent.com"]')
    best_idx = -1
    best_area = 0
    for i in range(img_candidates.count()):
        try:
            width = img_candidates.nth(i).evaluate('el => el.naturalWidth')
            height = img_candidates.nth(i).evaluate('el => el.naturalHeight')
            if width > 300 and height > 300 and width * height > best_area:
                best_area = width * height
                best_idx = i
        except Exception:
            pass
    if best_idx != -1:
        try:
            img_candidates.nth(best_idx).click()
            time.sleep(5)
            seen = set()
            saved = 0
            for nav in range(10):
                gallery_imgs = page.locator('img[src^="https://lh3.googleusercontent.com/"]')
                for i in range(gallery_imgs.count()):
                    img_elem = gallery_imgs.nth(i)
                    try:
                        width = img_elem.evaluate('el => el.naturalWidth')
                        height = img_elem.evaluate('el => el.naturalHeight')
                        src = img_elem.get_attribute('src')
                        srcset = img_elem.get_attribute('srcset')
                        if srcset:
                            largest_url = srcset.split(',')[-1].split()[0]
                            src = largest_url
                        norm_src = normalize_url(src)
                        if norm_src and norm_src not in seen and saved < max_gallery_images:
                            try:
                                high_res_url = get_high_res_url(src)
                                img_data = requests.get(high_res_url).content
                                fname = os.path.join(shop_dir, f'image_{saved+1:02d}.png')
                                with open(fname, 'wb') as handler:
                                    handler.write(img_data)
                                seen.add(norm_src)
                                saved += 1
                            except Exception:
                                pass
                    except Exception:
                        pass
                if saved >= max_gallery_images:
                    break
                right_arrow = page.locator('button[aria-label="Next"], button[jsaction*="pane.photoGalleryPage.next"]')
                if right_arrow.count() > 0:
                    try:
                        right_arrow.first.click()
                        time.sleep(1)
                    except Exception:
                        break
                else:
                    break
        except Exception:
            pass
    else:
        print("[DEBUG] No suitable main image found to click.")

def main():
    all_data = {}
    # Read URLs from the CSV file's 'Google Maps Link' column
    csv_path = os.path.join(os.path.dirname(__file__), 'input', 'top_rated_massage_shops.csv')
    urls = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('Google Maps Link', '').strip()
            if url:
                urls.append(url)
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(locale='en-US')
        page = context.new_page()
        output_base = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_base, exist_ok=True)
        for idx, url in enumerate(urls, 1):
            place_id = extract_place_id(url)
            print(f"Extracting reviews for {place_id}...")
            try:
                reviews = extract_reviews_from_url(page, url)
            except Exception as e:
                print(f"  [ERROR] Failed to extract reviews for {place_id}: {e}")
                reviews = []
            all_data[place_id] = {"reviews": reviews}
            print(f"  Found {len(reviews)} reviews. Now saving images...")
            shop_dir = os.path.join(output_base, f'shop{idx:02d}')
            try:
                save_images_for_url(page, url, shop_dir, max_gallery_images=10)
            except Exception as e:
                print(f"  [ERROR] Failed to save images for {place_id}: {e}")
                print(f"  [INFO] Retrying image save for {place_id} after reload...")
                try:
                    page.reload()
                    time.sleep(3)
                    save_images_for_url(page, url, shop_dir, max_gallery_images=10)
                except Exception as e2:
                    print(f"  [ERROR] Second attempt to save images for {place_id} also failed: {e2}")
        browser.close()
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output', 'all_reviews.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Saved reviews for {len(all_data)} places to {output_path}")

    # === 画像加工処理を追加 ===
    BASE_DIR = output_base
    shop_dirs = [d for d in os.listdir(BASE_DIR) if d.startswith('shop') and os.path.isdir(os.path.join(BASE_DIR, d))]
    for shop_dir in shop_dirs:
        shop_path = os.path.join(BASE_DIR, shop_dir)
        modified_dir = os.path.join(shop_path, 'modified')
        os.makedirs(modified_dir, exist_ok=True)
        for filename in os.listdir(shop_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                img_path = os.path.join(shop_path, filename)
                with Image.open(img_path) as img:
                    # 1. Rotate by 3 degrees
                    img = img.rotate(3, expand=True, fillcolor=(255,255,255))
                    # 2. Crop
                    orig_w, orig_h = img.size
                    crop_w = int(orig_w * 0.7)
                    crop_h = int(orig_h * 0.75)
                    max_x = orig_w - crop_w
                    max_y = orig_h - crop_h
                    if max_x > 0:
                        start_x = random.randint(0, max_x)
                    else:
                        start_x = 0
                    if max_y > 0:
                        start_y = random.randint(0, max_y)
                    else:
                        start_y = 0
                    img = img.crop((start_x, start_y, start_x + crop_w, start_y + crop_h))
                    # 3. Slightly change color (randomly adjust brightness, color, contrast)
                    enhancers = [
                        (ImageEnhance.Brightness, 0.95, 1.05),
                        (ImageEnhance.Color, 0.95, 1.05),
                        (ImageEnhance.Contrast, 0.95, 1.05),
                    ]
                    for enhancer_class, min_factor, max_factor in enhancers:
                        factor = random.uniform(min_factor, max_factor)
                        img = enhancer_class(img).enhance(factor)
                    # Save to modified directory
                    save_path = os.path.join(modified_dir, filename)
                    img.save(save_path)
                    print(f"Processed and saved: {save_path}")

if __name__ == "__main__":
    main() 