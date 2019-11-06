from scraper import TftScraper

output_file = "datasetChampions.csv"

scraper = TftScraper();
scraper.scrape();
scraper.exportCSV(output_file);
