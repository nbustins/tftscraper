from scraper import TftScraper

output_file = "datasetChampions_v2.csv"

scraper = TftScraper();
scraper.scrape();
scraper.exportCSV(output_file);
