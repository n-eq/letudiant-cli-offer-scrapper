from bs4 import BeautifulSoup
import urllib

URL="http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165/niveaux-3_2_9/page-1.html"

r=urllib.urlopen(URL)
soup=BeautifulSoup(r)

offer_titles=soup.find_all("a", class_="c-search-result__title")
for title in offer_titles:
    print(title)


