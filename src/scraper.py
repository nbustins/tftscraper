import requests
from bs4 import BeautifulSoup

class TftScraper():

    def __init__(self):
        self.url = "https://lolchess.gg/champions"
        self.data = []

    def __download_html(self,url):
        page = requests.get(url)

        return(BeautifulSoup(page.content,'html.parser'))

    def __getChampionsLinks(self,html):
        links = []
        afilter = html.findAll('a')

        for a in afilter:
            if 'class' in a.attrs and a['class'][0] == "guide-champion-list__item":
                links.append(a['href'])

        return(links)

    def __cleanValue(self,value):
        return value.replace('\n', ' ').replace('\r', '').replace(' ','')

    def __splitAndAdd(self,l,value):
        values = value.split("/")
        l.extend([values[0],values[1],values[3]])

    def __joinOrigin(self,l):
        s = ''
        i = 0
        while (i < len(l)-1):
            s += l[i]
            i+=1;
            if (i < len(l)-1): s+="-"

        return([s,l[len(l)-1]])

    def __getStats(self,bs):

        statsClean = []
        statsRaw = bs.find_all("div", class_ = "guide-champion-detail__base-stat")

        for s in statsRaw:
            # Get stat name
            statName = s.find("div", class_ = "guide-champion-detail__base-stat__name").text
            # Get stat value
            statValue = s.find("div", class_ = "guide-champion-detail__base-stat__value").text

            #Clean the raw value and the stat
            statName = self.__cleanValue(statName)
            statValue = self.__cleanValue(statValue)

            #TODO: Tractar cas especial attack speed.

            # Split the special cases
            if statName in ("Health","AttackDamage","DPS"):
                #get 3 val
                self.__splitAndAdd(statsClean,statValue)
            else:
                statsClean.append(statValue)

        return(statsClean)

    def __getOriginAndClass(self,bs):
        l = []
        ocraw = bs.find_all("div", class_ = "guide-champion-detail__synergy")
        for oc in ocraw:
            l.append(oc.span.text)

        return(l)

    def __getNameFromLink(self,l):
        l = l.split('/')
        return l[len(l)-1]

    def scrape(self):
        print("Scraping, please wait.")
        html = self.__download_html(self.url);
        # Obtain all links
        championLinks = self.__getChampionsLinks(html)

        # Extract the information for each champion
        for champion in championLinks:
            # Obtenim el contingut html
            html = self.__download_html(champion)

            # Obtenim els estats
            stats = self.__getStats(html)

            # Obtenim la classe i origen
            oc = self.__getOriginAndClass(html)
            # Mirem si es de tipus multiorigen
            if len(oc) > 2:
                oc = self.__joinOrigin(oc)

            #Add a new line of data
            self.data.append([self.__getNameFromLink(champion)]+stats+oc)
        print("Proces has finished.")

    def exportCSV(self, filename):
        # Overwrite to the specified file.
        # Create it if it does not exist.
        file = open("../csv/" + filename, "w+")

        # Dump all the data with CSV format
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                file.write(self.data[i][j] + ";");
            file.write("\n");
