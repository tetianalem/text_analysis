#
# Part 1. Web scraping of job applications from EY careers
#
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_ey_jobs(country: str, num_pages: int) -> pd.DataFrame:
    # --- Setup headless Chrome ---
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    base_url = "https://careers.ey.com"
    search_base = f"{base_url}/ey/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_country={country}&optionsFacetsDD_customfield1="

    jobs = []

    # --- Loop through specified pages ---
    for page_num in range(num_pages):
        startrow = page_num * 25
        page_url = f"{search_base}&startrow={startrow}"
        print(f"🔎 Fetching: Page {page_num + 1} | {page_url}")
        
        driver.get(page_url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        job_cards = soup.select("tr.data-row")

        for job_card in job_cards:
            try:
                title_elem = job_card.select_one("a.jobTitle-link")
                title = title_elem.get_text(strip=True)
                job_url = base_url + title_elem["href"]
                location = job_card.select_one("span.jobLocation").get_text(strip=True)

                jobs.append({
                    "Title": title,
                    "Location": location,
                    "URL": job_url
                })
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

    # --- Scrape job descriptions with progress tracking ---
    descriptions = []

    print(f"\n📄 Fetching job descriptions for {len(jobs)} jobs...\n")
    for idx, job in enumerate(jobs, start=1):
        try:
            print(f"📝 [{idx}/{len(jobs)}] Fetching: {job['Title'][:60]}")
            driver.get(job["URL"])
            time.sleep(8)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            body = soup.find("span", class_="jobdescription")

            if body:
                text = body.get_text(separator=" ", strip=True)
                descriptions.append(text)
            else:
                descriptions.append("No description found.")
        except Exception as e:
            print(f"❌ Error fetching {job['URL']}: {e}")
            descriptions.append("Error loading or parsing page.")

    driver.quit()

    # --- Return DataFrame ---
    df = pd.DataFrame(jobs)
    df["Job Description"] = descriptions
    return df


df_jobs_ua = scrape_ey_jobs('UA', 20)
df_jobs_ge = scrape_ey_jobs('DE', 20)
df_jobs_us = scrape_ey_jobs('US', 20)

df_jobs_ua.to_excel("ey_jobs_ua.xlsx", index=True)
df_jobs_ge.to_excel("ey_jobs_ge.xlsx", index=True)
df_jobs_us.to_excel("ey_jobs_us.xlsx", index=True)

# 
# Part 2. Transformation of web scraped data of job applications from EY careers
#


#
# Part 3. Web scraping of reviews from Glassdoor
#
