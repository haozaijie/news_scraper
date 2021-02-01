# Introduction

This is a package that collects news from certain news websites on a given topic. 
The websites currently available include CNN and WSJ.

The data collected include headlines, summary contents and dates.
With these information, sentiment analysis is performed using the textblob
to generate polarity and subjectivity. Polarity measures if the news is positive or negative and ranges from -1 to 1.
Subjectivity measures if the news is subjective or objective and ranges from 0 to 1.

These metrics are then used to generate line charts for visualization purpose.
Charts generated:
    ```
1. number of news published daily by different news source
2. polarity of news by different sources over time
3. subjectivity of news by different sources over time
    ```

    
## how to run it

Download the repo then run the following command on command line:

    ```python __main__.py```
    
There will be prompt for the topic and date range you are interested in.
Type the answers following the format and the scraper will start.