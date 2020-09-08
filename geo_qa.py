import requests
import lxml.html
import rdflib
import sys

wiki_prefix = "http://wikipedia.org"
UN_nations = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
project_prefix = "http://project.org/"


def get_countries(url):
    """
        input: the url for the UN nations page
        retuns two lists:
            names: the names of the countries
            links: the full url for each country (synchronized with the index in names)
    """
    req = requests.get(url)
    doc = lxml.html.fromstring(req.content)
    tbl = doc.xpath("//table[contains(@id, 'main')]")[0]
    names = tbl.xpath(".//tr[position()>1]//span[@class='flagicon']/../a[1]/@title")
    links = tbl.xpath(".//tr[position()>1]//span[@class='flagicon']/../a[1]/@href")
    links = [wiki_prefix + links[i] for i in range(len(links))]
    return names, links


def get_leader(infobox, leader):
    """
    input:
        infobox: an lxml.html node from the html tree of a country
        leader: either 'president' or 'Prime_Minister'
    output:
        a 2-tuple of the name of the leader and a full url to their wikipedia page 
    """
    try:
        name = infobox.xpath(".//tr[.//th//a[text()='"+ leader + "']]//td[1]//a[1]/@title")[0]
        if '(page does not exist)' not in name:
            link = infobox.xpath(".//tr[.//th//a[text()='"+ leader + "']]//td[1]//a[1]/@href")[0]
            link = wiki_prefix + link
        else:
            link = '(page does not exist)'
            name = name[:-21].strip()
        res = (name, link)
    except IndexError:
        res = ''
    return res


def get_numeral(infobox, A_or_P):
    """
    this function is meant to retreive either the Area or Population of a country
    the input infobox is the tree node of the country,
    and the input A_or_P tells us if we want Area or Population
    output in a list of strings requiering further work
    """
    try:
        head = infobox.xpath(".//tr[.//th//a[contains(text(), '" + A_or_P + "')]]")[0]
    except IndexError:
        head = infobox.xpath(".//tr[.//th[contains(text(), '" + A_or_P + "')]]")[0]
    ar = '' if A_or_P == 'Area' else '/'
    res = head.xpath(".//td[1]/"+ ar +"text()")
    if len(res) == 0:
        res = head.xpath("./following-sibling::tr[1]//td[1]/"+ ar +"text()")
    return res


def parse_area(area_td):
    """
    input: a list of strings from get_numeral(infobox, 'Area')
    output: a tring of the Area
    (maybe the output should be an int?)
    """
    k = '\xa0km'
    for j in range(len(area_td)):
        i = area_td[j].find(k)
        if i != -1:
            I = j
            break
    raw_num = area_td[I][:i]
    if len(raw_num) == 0:
        raw_num = area_td[I - 1]
    i = len(raw_num) - 1
    while raw_num[i] in [',', '.'] or raw_num[i].isnumeric():
        i -= 1
        if i == -1:
            break
        
    return raw_num[i + 1:]


def is_big_number(st):
    """
    a replacement for isnumeric in cases where the number has ',' in it
    """
    st = st.replace(" ", '')
    st = st.replace(",", '')
    return st.isnumeric()


def get_pop(pop_lst):
    """
    input: a list of strings one of which contains the population
    output: one string repesenting the population
    """
    for i in range(len(pop_lst)):
        words = pop_lst[i].split(sep = ' ')
        for j in range(len(words)):
            words[j] = (words[j].replace('\n', '')).replace('\t', '')
            if is_big_number(words[j]):
                return words[j]
    return ''

def gov_text(info):
    """
    input: a country's infobox (rdflib graph node)
    uotput: list of strings of text from the government table cell
    """
    try:
        res = info.xpath(".//tr[.//th//a[contains(text(), 'Government')]][1]")[0]
    except IndexError:
        try:
            res = info.xpath(".//tr[.//th[contains(text(), 'Government')]][1]")[0]
        except IndexError:
            return []
    return res.xpath(".//td[1]//text()")


def refine_gov(lst):
    """
    input: a list of strings from the infobox
    output: one string representing the government
    """
    for i in range(len(lst)):
        try:
            if lst[i].strip()[0] == '(':
                lst = lst[:i]
                break
        except IndexError:
            continue
    res = ''
    for i in range(len(lst)):
        lst[i] = lst[i].strip()
        if is_gov(lst[i]):
            res += ' ' + lst[i]
    return res[1:]


def is_gov(word):
    """
    input: a string
    output: boolean value representing if word can be a kind of government
    """
    if len(word) == 0:
        return False
    for letter in word:
        if (not letter.isalpha()) and (letter not in ['-', ' ']):
            return False
    return True



def get_cap(name, infobox):
    """
    input: a country's infobox (rdflib graph node)
    output: a list of captal cities
    """
    cap = infobox.xpath(".//tr[.//th[contains(text(), 'Capital')]]//td[1]/a/text()")
    if len(cap) == 0:
        cap = infobox.xpath(".//tr[.//th[contains(text(), 'Capital')]]//td[1]//li//a/@title")
    if len(cap) == 0:
        if name in infobox.xpath(".//tr[.//th[contains(text(), 'Capital')]]//td[1]//text()"):
            cap = name
    return cap

    
def extract_country_info(name, country_url):
    """
    input: full country url
    output: a pyhton dictionary with keys
        'government'
        'president'
        'prime_minister'
        'capital'
        'area'
        'population'

    it's noteworthy that this is the main event of the Information Exctraction
    part of the project
    """
    req = requests.get(country_url)
    doc = lxml.html.fromstring(req.content)
    info = doc.xpath("//table[contains(@class, 'infobox')]")[0]
    
    gov = refine_gov(gov_text(info))
    
    president = get_leader(info, 'President')
    prime_minister = get_leader(info, 'Prime Minister')

    cap = get_cap(name, info)

    area = parse_area(get_numeral(info, "Area"))
    pop = get_pop(get_numeral(info, "Population"))
    
    res = {"government" : gov, "president" : president, \
           "prime_minister" : prime_minister, "capital" : cap, \
           "area" : area.strip() + "_km2", "population" : pop.strip()}
    return res


def add_country_data_type_to_graph(graph, info_type, info_data, name):
    """
    pretty straight forward, given an rdf graph and a country dictionry
    we want to add the information from the dictionary to the graph
    """
    if info_type == "capital":
        for data_point in info_data:
            if len(data_point) > 0 and not data_point.isspace():
                if data_point != 'De jure':
                    format_and_add(graph, data_point, info_type, name)
    elif info_type == "government":
        format_and_add(graph, info_data, info_type, name)
        
    elif info_type in ["president", "prime_minister"]:
        if len(info_data) > 0:
            format_and_add(graph, info_data[0], info_type, name)
            
    else:
        #we'll use string and not numeral
        format_and_add(graph, info_data, info_type, name)
    return None


def format_and_add(graph, info, relation, name):
    """
    input: graph and three stirngs
        function formats the strings and adds to the graph 
    """
    info = info.replace(" ", "_")
    name = name.replace(" ", "_")
    inf = rdflib.URIRef(project_prefix + info)
    rel = rdflib.URIRef(project_prefix + relation)
    nm = rdflib.URIRef(project_prefix + name)
    graph.add((inf, rel, nm))
    return None
    



def get_year(born_txt):
    """
    input: a list of string
    output: 'yyyy' or ''
    """
    for i in range(len(born_txt)):
        words = born_txt[i].split()
        for word in words:
            if len(word) == 4 and word.isnumeric():
                return word
            if len(word) == 9 and word[4] == '/' and word[:4].isnumeric() and word[5:].isnumeric():
                return word
    return ''


def add_leader_bday(graph, leader_url, name):
    """
    input: graph, link to leader's wiki page, leader's name
    function adds leader's birth date to graph
    """
    try:
        req = requests.get(leader_url)
        doc = lxml.html.fromstring(req.content)
        info = doc.xpath("//table[contains(@class, 'infobox')]")[0]
    except:
        format_and_add(graph, name, "birthDate", '')
        return
    
    try:
        dob = info.xpath(".//span[@class='bday']/text()")[0]
    except IndexError:
        date = info.xpath(".//tr[.//th[contains(text(), 'Born')]]/td//text()")
        dob = get_year(date)
    format_and_add(graph, name, "birthDate", dob)
    return None


country_type = rdflib.URIRef(project_prefix + 'Country')

def country_to_graph(graph, country_url, name):
    """
    input: rdflib graph, country's url and country name
    function adds all information of the country to the graph
    """
    graph.add((rdflib.URIRef(project_prefix + name.replace(" ", "_")), rdflib.namespace.RDF.type, country_type))
    data = extract_country_info(name, country_url)
    for key in data:
        add_country_data_type_to_graph(graph, key, data[key], name)
    for ldr in ["president", "prime_minister"]:
        leader = data[ldr]
        if len(leader) > 0:
            add_leader_bday(graph, leader[1], leader[0])
    return None



def make_ontology():
    """
    this function creates the ontology
    """
    g = rdflib.Graph()
    names, links = get_countries(UN_nations)
    for i in range(len(names)):
        country_to_graph(g, links[i], names[i])
    g.serialize("ontology.nt", format="nt")
    return None
    
    


#parse question:

def graphstr_to_answer(graph_string):
    """
    input: 'http://project.org/info'
    output: 'info'
    """
    i = len(graph_string) - 1
    while graph_string[i] != '/':
        i -= 1
    return graph_string[i + 1:].replace("_", " ")


def get_bday(graph, leader_type, cont):
    """
    input: formated name
    output: a string 'yyyy-mm-dd'
    """
    qu = list(graph.query("select ?y where { " +\
                            "?x <" + project_prefix + leader_type + "> "+\
                             "<" + project_prefix + cont + ">. " +\
                            "?x <" + project_prefix + "birthDate> ?y.}"))
    try:
        res  = graphstr_to_answer(str(qu[0][0]))
        if res == '':
            return 'Unknowen'
        return res
    except IndexError:
        return ''


def get_by_role(graph, role, name):
    """
    input: graph, wanted role, formated name
    output: a lsit of strings
    """
    qu = list(graph.query("select ?x where { <" + project_prefix + name + "> "+\
                             "<" + project_prefix + role + "> ?x.}"))
    for i in range(len(qu)):
        qu[i] = graphstr_to_answer(str(qu[i][0]))
    return qu

def get_role(graph, name):
    """
    input: graph, formated name
    output: 2-tuple (countries <name> is president of, countries <name> is president of)
    """
    res = (get_by_role(graph, 'president', name), get_by_role(graph, 'prime_minister', name))
    return res
    

def get_attribute(graph, att, cont):
    """
    input: graph, attribute, name of country
    output: list of strings
    """
    qu = list(graph.query("select ?x where { ?x " +\
                                          "<" + project_prefix + att + "> " +\
                                         "<" + project_prefix + cont + ">.}"))
    for i in range(len(qu)):
        qu[i] = graphstr_to_answer(str(qu[i][0]))
    return qu


def print_role(roles):
    """
    input: the output from get_role
    function prints answer (no output)
    """
    rls = ("President", "Prime minister")
    for i in range(2):
        if len(roles[i]) > 0:
            res = rls[i] + " of "
            res += ', '.join(roles[i])
            print(res)
            return None
        
        
def get_name(words, not_of):
    """
    input: question split into words without a question mark
    uotput: name (either country or person)
    this function is needed so that the question doesn't have to be case sensitive
    """
    if not_of:
        start = 2
    else:
        start = 5 if words[4] == 'of' else 6
    end = len(words) - 1 if words[-1].lower() != 'born' else len(words) - 2
    for i in range(start, end + 1):
        if words[i].lower() not in ['of', 'the']:
            tmp = words[i].lower()
            tmp = tmp[0].upper() + tmp[1:]
            words[i] = tmp
    res = '_'.join(words[start : end + 1])
    return res


    
def question_to_answer(question):
    """
    input: question string
    function prints the answer (no output)
    """
    words = question.split()
    words[-1] = words[-1][:-1]
    g = rdflib.Graph()
    g.parse("ontology.nt", format = "nt")
    
    if 'of' not in words:
        name = get_name(words, True)
        print_role(get_role(g, name))
        
    else:
        cont = get_name(words, False)
        att = words[3].lower() if words[4] == 'of' else 'prime_minister'

        if words[-1] == 'born':
            res = get_bday(g, att, cont)
            if len(res) == 0:
                print(cont + ' has no ' + att.replace("_", " "))
                return
            print(res)

        else:
            res = get_attribute(g, att, cont)
            if len(res) == 0:
                print(cont + ' has no ' + att.replace("_", " "))
                return
            
            ans = ', '.join(res)
            print(ans.replace('_', ' '))
    return
                



def main():
    if sys.argv[1] not in ['create', 'question']:
        print("Invalid input, first input to program must be either 'create' or 'question'")
        return
    if sys.argv[1] == 'question':
        question_to_answer(sys.argv[2])
        return
    make_ontology()
    return


if __name__ == '__main__':
    main()


