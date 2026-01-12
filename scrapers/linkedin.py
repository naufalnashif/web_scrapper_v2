import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import time

class LinkedInScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _get_deep_detail(self, client, url):
        """Mengambil data mendalam sesuai test.py"""
        try:
            r = client.get(url, timeout=15.0)
            if r.status_code == 200:
                s = BeautifulSoup(r.text, 'html.parser')
                
                # Full Description
                desc_div = s.find('div', class_='description__text')
                full_desc = desc_div.get_text(separator="\n").strip() if desc_div else "N/A"
                
                # Criteria Map
                criteria = {}
                items = s.find_all('li', class_='description__job-criteria-item')
                for it in items:
                    h = it.find('h3').text.strip() if it.find('h3') else "Other"
                    v = it.find('span').text.strip() if it.find('span') else "N/A"
                    criteria[h] = v
                
                app_tag = s.find('span', class_='num-applicants__caption')
                comp_link_tag = s.find('a', class_='topcard__org-name-link')
                
                return {
                    "description": full_desc,
                    "seniority_level": criteria.get("Seniority level", "N/A"),
                    "employment_type": criteria.get("Employment type", "N/A"),
                    "job_function": criteria.get("Job function", "N/A"),
                    "industries": criteria.get("Industries", "N/A"),
                    "applicants_count": app_tag.text.strip() if app_tag else "N/A",
                    "company_link": comp_link_tag['href'].split('?')[0] if comp_link_tag else "N/A"
                }
        except: pass
        return {}

    def get_data(self, keyword, max_posts=10, since_date=None):
        clean_keyword = keyword.strip()
        scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        
        data = {
            "platform": "LinkedIn",
            "profile_info": {"username": clean_keyword, "category": "Corporate Intelligence", "followers": 0},
            "posts": []
        }

        with httpx.Client(headers=self.headers, follow_redirects=True) as client:
            params = {"keywords": clean_keyword, "location": "Indonesia", "start": 0}
            try:
                r = client.get(base_url, params=params)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    cards = soup.find_all('li')
                    
                    for card in cards[:max_posts]:
                        try:
                            title = card.find('h3', class_='base-search-card__title').text.strip()
                            comp = card.find('h4', class_='base-search-card__subtitle').text.strip()
                            loc = card.find('span', class_='job-search-card__location').text.strip()
                            link = card.find('a', class_='base-card__full-link')['href'].split('?')[0]
                            
                            # Deep Extractions
                            details = self._get_deep_detail(client, link)
                            time.sleep(1.8) 
                            
                            item = {
                                "name": title,
                                "publisher": comp,
                                "location": loc,
                                "url": link,
                                "date": card.find('time')['datetime'] if card.find('time') else scraped_at,
                                "caption": f"[{comp}] {title} in {loc}",
                                "scraped_at": scraped_at,
                                "platform": "LinkedIn",
                                "username": clean_keyword, # Untuk filter dashboard
                                "description": details.get("description", "N/A"),
                                "seniority_level": details.get("seniority_level", "N/A"),
                                "employment_type": details.get("employment_type", "N/A"),
                                "job_function": details.get("job_function", "N/A"),
                                "industries": details.get("industries", "N/A"),
                                "applicants_count": details.get("applicants_count", "N/A"),
                                "company_link": details.get("company_link", "N/A")
                            }
                            data["posts"].append(item)
                        except: continue
                return data
            except Exception as e:
                return {"error": str(e), "platform": "LinkedIn"}