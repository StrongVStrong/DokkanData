# Dokkan Data
 A dokkan.wiki scraper that allows users to get all character data with no trouble.  

## Features
- Simple: Click play and let the magic happen with the scraper being self sufficient and handling itself
- User Friendly: Multiple programs and options that allow the user to scrape off a certain character, scrape new data alone, scrape characters from certain pages, etc

## Requirements
- Selenium
- Pandas
- Json
- re
- datetime
- time


## Get started
To start the scraping process, first obtain all links by running dokkanlinks.py  

Then run dokkanwikiData.py to obtain all character data currently available  

If the program stops at any point, obtain the most recent character id and place it at the end of the start_link variable in ...AtAChar.py  

If you wish to update your existing character data with new character data after updates come out, run ...NewChars.py

## Creation process
 Here's a video explanation of how I made the program and my thought process behind it:  
 [![Watch the video](https://img.youtube.com/vi/Me22FEYvfCA/0.jpg)](https://www.youtube.com/watch?v=Me22FEYvfCA)


