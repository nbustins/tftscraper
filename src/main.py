from scraper import TftScraper

output_file = "Teamfigth_Tactics_champions_patch_9.21.csv"
set = 'set1'

scraper = TftScraper(set);
scraper.scrape();
scraper.exportCSV(output_file);
