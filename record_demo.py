import asyncio
import os
import shutil
import subprocess
from playwright.async_api import async_playwright

async def record_scenery_demo():
    video_dir = os.path.abspath("video_raw")
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    os.makedirs(video_dir, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        # 1. Navigate to frontend UI
        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080")
        await page.wait_for_selector("#welcome-card", timeout=10000)
        await asyncio.sleep(2.0)
        
        # 2. First prompt: Short, scenic & simple core prompt!
        prompt_1 = "Describe Banff morning sunrise"
        print(f"Typing Prompt 1: {prompt_1}")
        
        input_elem = await page.wait_for_selector("#input")
        await input_elem.focus()
        
        for char in prompt_1:
            await page.keyboard.type(char, delay=45)
            await asyncio.sleep(0.01)
            
        await asyncio.sleep(0.6)
        
        send_btn = await page.wait_for_selector("button.send-btn")
        await send_btn.click()
        
        print("Waiting for Prompt 1 response...")
        await page.wait_for_selector(".msg.agent .bubble", timeout=60000)
        await asyncio.sleep(3.5)
        
        await page.evaluate("document.getElementById('log').scrollTop = 150;")
        await asyncio.sleep(3.0)
        
        # 3. Second prompt: Short, scenic & simple rich prompt!
        prompt_2 = "Kyoto weather, save moment, and paint Fushimi Inari at dusk"
        print(f"Typing Prompt 2: {prompt_2}")
        
        await input_elem.focus()
        for char in prompt_2:
            await page.keyboard.type(char, delay=45)
            await asyncio.sleep(0.01)
            
        await asyncio.sleep(0.6)
        await send_btn.click()
        
        print("Waiting for Prompt 2 response...")
        await page.wait_for_selector(".a2img, .a2card", timeout=90000)
        await asyncio.sleep(4.0)
        
        print("Scrolling to display rich output...")
        for scroll_y in range(150, 750, 15):
            await page.evaluate(f"document.getElementById('log').scrollTop = {scroll_y};")
            await asyncio.sleep(0.04)
            
        await asyncio.sleep(6.0)
        
        print("Closing browser context...")
        await page.close()
        await context.close()
        await browser.close()
        
    recorded_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".webm")]
    if not recorded_files:
        raise RuntimeError("No recorded video file found!")
    raw_video_path = recorded_files[0]
    print(f"Raw video saved at: {raw_video_path}")
    return raw_video_path

if __name__ == "__main__":
    asyncio.run(record_scenery_demo())
