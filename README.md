# IE_project-countries_from_wikipedia

This program extracts information from the countries table at
https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)
The code is correct as of 13 Jul 2020, if changes were made to the wikipedia page since - changes might be needed for the extraction code as well.

The information is then stored to a local file as an ontology.

The way to use this is by one of two comands:
1. exctarct the information using ./python3 geo_qa.py create file_name.nt
  after which an ontogy will be created with the name file_name.nt
  Obviously, you need to be conected to the internet for this.
  This part of the program takes 10-20 minutes to run.
  
2. Query the ontology by using ./python3 geo_qa.py question “natural language question string”
  Where “natural language question string” is one of the following:
  (i) Who is the president of "some_country"?
  (ii) Who is the prime minister of "some_country"?
  (iii) What is the population of "some_country"?
  (iv) What is the area of "some_country"?
  (v) What is the government of "some_country"?
  (vi) What is the capital of "some_country"?
  (vii) When was the president of "some_country" born?
  (viii) When was the prime minister of "some_country" born?
  (ix) Who is "some_entity"?
  
  where "some_entity" refers to a leader of a country

