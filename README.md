# IE_project-countries_from_wikipedia

This program extracts information from the countries table at
https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)

The information is then stored to a local file as an ontology.

The way to use this is by one of two comands:
1. exctarct the information using ./python3 geo_qa.py create file_name.nt
  after which an ontogy will be created with the name file_name.nt
  Obviously, you need to be conected to the internet for this.
  This part of the program takes 10-20 minutes to run.
  
2. Query the ontology by using ./python3 geo_qa.py question “<natural language question string>”
  Where “<natural language question string>” is one of the following:
  (i) Who is the president of <country>?
  (ii) Who is the prime minister of <country>?
  (iii) What is the population of <country>?
  (iv) What is the area of <country>?
  (v) What is the government of <country>?
  (vi) What is the capital of <country>?
  (vii) When was the president of <country> born?
  (viii) When was the prime minister of <country> born?
  (ix) Who is <entity>?
  
  <entity> refers to a leader of a country

