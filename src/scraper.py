import requests
import sys
from bs4 import BeautifulSoup

class TftScraper():

    def __init__(self,set):

        switchSet = {
                'set1' : 'set1/',
                'set2' : 'set2/'
        }
        self.url = "https://lolchess.gg/champions/"+ switchSet.get(set,'set1')
        self.data = []
        self.atrsNames = ['Name','HealthLvl1','HealthLvl2','HealthLvl3',
                        'AttackDamageLvl1','AttackDamageLvl2','AttackDamageLvl3',
                        'DPSLvl1','DPSLvl2','DPSLvl3','Range','AttackSpeed',
                        'Armor','MagicalResistance','Origin','Class','Cost']
        self.data.append(self.atrsNames)

    # Returns the html content
    def __download_html(self,url):
        page = requests.get(url)

        return(BeautifulSoup(page.content,'html.parser'))

    # Returns a list with all the champion links
    def __getChampionsLinks(self,html):
        links = []
        afilter = html.findAll('a')

        for a in afilter:
            if 'class' in a.attrs and a['class'][0] == "guide-champion-list__item":
                links.append(a['href'])

        return(links)

    # Returns value without spaces or new lines
    def __cleanValue(self,value):
        return value.replace('\n', ' ').replace('\r', '').replace(' ','')

    # Given a string with format A/B/C/D and a list, extends the list with [A,B,D]
    def __splitAndAdd(self,l,value):
        values = value.split("/")
        l.extend([values[0],values[1],values[3]])

    # Given the src of attack speed image returns the value
    def __getValueFromASimg(self,imgsrc):
        switchImg = {
            'ico-attack-distance-01.svg' : '1',
            'ico-attack-distance-02.svg' : '2',
            'ico-attack-distance-03.svg' : '3',
            'ico-attack-distance-04.svg' : '4'
        }

        return switchImg.get(imgsrc,'-1')

    # Given a value with an img attribute, returns the string of the src image given a value
    def __getSrcfromImage(self,value):
        value = value.img['src'].split('/')
        value = value[len(value)-1]

        return value

    # Given a list with origins and 1 class returns a list of length 2 where the first position is a string of all origins and the second is the class.
    def __joinOrigin(self,l):
        s = ''
        i = 0
        while (i < len(l)-1):
            s += l[i]
            i+=1;
            if (i < len(l)-1): s+="-"

        return([s,l[len(l)-1]])

    # Returns a list with the values of the stats
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

            # Split the special cases
            if statName in ("Health","AttackDamage","DPS"):
                #get 3 val
                self.__splitAndAdd(statsClean,statValue)
            # Special case extract information of a image
            elif statName == "AttackRange":
                statsClean.append(self.__getValueFromASimg(self.__getSrcfromImage(s)))
            else:
                statsClean.append(statValue)

        return(statsClean)

    # Returns a list with the origins and the class
    def __getOriginAndClass(self,bs):
        l = []
        ocraw = bs.find_all("div", class_ = "guide-champion-detail__synergy")
        for oc in ocraw:
            l.append(oc.span.text)

        return(l)

    # Returns the value of the cost
    def __getCost(self,bs):
        divcost = bs.find_all("div", class_ = "guide-champion-detail__stats__value")
        lvlcost = self.__cleanValue(divcost[0].div.text).split('/')

        # We only want the cost of 1 champion
        return lvlcost[0]

    # Returns the name of the champion link
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
            # Get the html content
            html = self.__download_html(champion)
            # Get the stats
            stats = self.__getStats(html)
            # Get the origin and the class
            oc = self.__getOriginAndClass(html)
            # Check if there are more than 1 origin.
            if len(oc) > 2:
                oc = self.__joinOrigin(oc)

            # Add a new line of data
            self.data.append([self.__getNameFromLink(champion)]+stats+oc+[self.__getCost(html)])
            # Show progress
            sys.stdout.write('#')
            sys.stdout.flush()

        print("\n -> Proces has finished.")

    def exportCSV(self, filename):
        # Overwrite to the specified file.
        # Create it if it does not exist.
        file = open("../csv/" + filename, "w+")

        # Dump all the data with CSV format
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                file.write(self.data[i][j] + ";");
            file.write("\n");
