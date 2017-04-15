# letudiant-cli-offer-scrapper

** Necessity is the mother of invention.**

I had the idea of writing this utility script when I was fed up with checking every time if there were any new internship offers available that suit my needs.

This Python script fetches available internship offers based on the users' criteria from the letudiant.fr, a famous French magazine dedicated to students. It then displays the results on the terminal:

![alt tag](https://github.com/Marrakchino/letudiant-cli-offer-scrapper/blob/master/screenshot_2017-04-05%2010:36:10.png)

# Install

```sh
git clone https://github.com/marrakchino/letudiant-cli-offer-scrapper.git
```

## Usage
```sh

# Display 6 pages of offers 
$ python main.py --pages 6 

# Display 6 pages of offers filtered by keywords
$ python main.py --pages 6 --filter keyword1 --filter keyword2

# Display offers released during the 3 last days
$ python main.py --days 3

# Display offers released during the 3 last days filtered by keywords
$ python main.py --days 3 --filter keyword1 --filter keyword2	

# Display only new offers (based on a previous search)
$ python main.py --new

# Display one page (Default)
$ python main.py 

# Display 5 pages in interactive mode
$ python main.py --pages 5 --interactive

```
