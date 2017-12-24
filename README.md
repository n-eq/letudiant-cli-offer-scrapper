# letudiant-cli-offer-scrapper

**Necessity is the mother of invention.**

I had the idea of writing this utility script when I was fed up with checking every time if there were any new internship offers available that suit my needs.

This Python script fetches available internship offers based on the user's criteria from [letudiant](http://letudiant.fr), a famous French magazine dedicated to students. It then displays the results on the terminal:

![alt tag](https://raw.githubusercontent.com/Marrakchino/letudiant-cli-offer-scrapper/master/res/screenshot_2017-12-24%2017-18-13.png)

## Install

```sh
$ git clone https://github.com/marrakchino/letudiant-cli-offer-scrapper.git
$ pip install -r requirements.txt # (still in **ci** branch)
```

## Configuration

There's some configuration that needs to be done (by hand, I'll create a script or so to automate the thing one day).

You need to choose the URL from which you want to extract job offers, it's something similar to this:
http://jobs-stages.letudiant.fr/stages-etudiants/offres/domaines-103_129_165_111/niveaux-3_2_9/page-1.html
This variable should be stored as`URL` in `offer-scrapper/main.py`.

Additionally, you need to choose a location for the `results` file (used for a `--new`less execution)

## Usage
```sh

# Display 6 pages of offers 
$ python offer-scrapper/main.py.py --pages 6 

# Display 6 pages of offers filtered by keywords
$ python offer-scrapper/main.py --pages 6 --filter keyword1 --filter keyword2

# Display offers released during the 3 last days
$ python offer-scrapper/main.py --days 3

# Display offers released during the 3 last days filtered by keywords
$ python offer-scrapper/main.py --days 3 --filter keyword1 --filter keyword2	

# Display only new offers (based on a previous search)
$ python offer-scrapper/main.py --new

# Display one page (Default)
$ python offer-scrapper/main.py 

# Display 5 pages in interactive mode
$ python offer-scrapper/main.py --pages 5 --interactive

```

### Interactive mode

The interactive mode enables the user to access the offer details by indicating its number. The program then displays on the terminal the details (salary, duration, expectations ...) and waits for another input.


![alt tag](https://raw.githubusercontent.com/Marrakchino/letudiant-cli-offer-scrapper/master/res/interactive_mode.png)


### Notes

* This software is far from being efficient, this was not my goal when I started 
developing it. Some operations are poorly developed and clearly unoptimized.

* letudiant.fr's pages are subject to modifications. In particular, HTML `tags`
and class names may differ from a version to another. Therefore, this software is
not guaranteed to be 100% functional. Some minor code tweaks may be needed 
in order to adapt to such changes.
