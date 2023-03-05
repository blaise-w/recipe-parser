from bs4 import BeautifulSoup
from urllib.request import urlopen
import nltk
from nltk import tokenize
import re
#import requests

COOKING_METHODS = ['add', 'airfry', 'bake', 'boil', 'broil', 'chop', 'combine', 'cook', 'cool', 'cream','cube', 'cut', 'dice', 'drain', 'fry', 'freeze', 'garnish', 'grill', 'heat', 'knead', 'keep warm', 'marinate', 'melt', 'mince', 'mix', 'peel', 'poach', 'pour', 'preheat', 'reduce heat', 'roast', 'saute', 'sauté', 'season', 'simmer', 'slice', 'steam', 'stir', 'strain', 'toast', 'whisk']

INGREDIENTS = ['tomatoes', 'pasta', 'oil', 'garlic', 'tomato paste', 'salt', 'pepper', 'basil', 'cheese', 'water']
# edge case tomato versus tomato paste?? idk
TOOLS = ['skillet', 'pan', 'pot', 'bowl', 'knife', 'oven']

VERB_TO_TOOL = {'drain':['colander'],'simmer':['pan'],'peel':['peeler','knife'],'boil':['pot'],'bake':['oven'],'airfry':['airfryer'],'saute':['spatula','pan'],'sauté':['spatula','pan'],'cut':['knife'],'chop':['knife'],'stir':['spatula','wooden spoon'],'mix':['spatula','wooden spoon']}

SUBSTITIONS = {
    'allspice': ['cinnamon', 'nutmeg', 'clove'],
    'baking powder': ['baking soda', 'cream of tartar', 'yeast'],
    'basil': ['oregano', 'thyme'],
    'bay leaves': ['thyme'],
    'ground beef': ['ground turkey', 'ground chicken', 'ground pork'],
    'brown sugar': ['white sugar', 'molasses', 'honey'],
    'butter': ['margarine', 'shortening', 'oil'],
    'cardamom': ['cinnamon', 'ginger'],
    'carrots': ['sweet potatoes', 'parsnips'],
    'cayenne pepper': ['red pepper flakes', 'paprika'],
    'chicken': ['turkey', 'pork'],
    'chili powder': ['paprika', 'cumin', 'garlic powder'],
    'cinnamon': ['nutmeg', 'allspice', 'cardamom'],
    'clove': ['allspice', 'nutmeg', 'cinnamon'],
    'coconut milk': ['heavy cream', 'soy milk'],
    'coriander': ['cumin', 'caraway'],
    'cornstarch': ['flour', 'arrowroot'],
    'cumin': ['coriander', 'chili powder'],
    'curry powder': ['garam masala', 'cumin', 'coriander'],
    'dill': ['fennel', 'tarragon'],
    'eggs': ['silken tofu', 'applesauce', 'banana'],
    'fish': ['tilapia', 'cod', 'halibut'],
    'fish sauce': ['soy sauce', 'hoisin sauce'],
    'garlic': ['shallot', 'onion', 'chives'],
    'ginger': ['allspice', 'cinnamon', 'nutmeg'],
    'ground pork': ['ground beef', 'ground turkey'],
    'heavy cream': ['coconut milk', 'silken tofu'],
    'honey': ['brown sugar', 'white sugar', 'maple syrup'],
    'italian sausage': ['chorizo', 'andouille sausage'],
    'lemon juice': ['lime juice', 'vinegar'],
    'milk (regular)': ['soy milk', 'almond milk', 'coconut milk'],
    'mustard (dry)': ['mustard (prepared)', 'wasabi'],
    'nutmeg': ['allspice', 'cinnamon', 'ginger'],
    'olive oil': ['canola oil', 'vegetable oil', 'coconut oil'],
    'onion': ['shallot', 'garlic', 'chives'],
    'paprika': ['cayenne pepper', 'chili powder'],
    'parmesan cheese': ['pecorino romano', 'grana padano'],
    'pasta': ['zucchini noodles', 'spaghetti squash'],
    'pork': ['chicken', 'turkey'],
    'potatoes': ['sweet potatoes', 'cauliflower'],
    'red pepper flakes': ['cayenne pepper', 'chili powder'],
    'rice': ['quinoa', 'couscous'],
    'salmon': ['trout', 'mackerel', 'tuna'],
    'sauce (tomato)': ['salsa', 'marinara sauce'],
    'shallot': ['onion', 'garlic', 'chives'],
    'shrimp': ['prawns', 'scallops', 'crab'],
    'sour cream': ['Greek yogurt', 'creme fraiche'],
    'soy sauce': ['fish sauce', 'tamari'],
    'spinach': ['kale', 'arugula', 'collard greens'],
    'sriracha': ['hot sauce', 'red pepper flakes'],
    'sugar': ['brown sugar', 'honey', 'maple syrup'],
    'brown sugar': ['sugar', 'honey', 'maple syrup'],
    'thyme': ['oregano', 'rosemary', 'bay leaves'],
    'tofu': ['tempeh', 'chicken', 'pork'],
    'tomatoes': ['red bell pepper', 'canned tomatoes', 'salsa'],
    'ground turkey': ['ground beed', 'ground chicken', 'ground pork'],
    'turkey': ['chicken', 'pork'],
    'vanilla extract': ['maple extract', 'almond extract'],
    'vegetable oil': ['olive oil', 'canola oil', 'coconut oil'],
    'vinegar': ['lemon juice', 'lime juice'],
    'white wine': ['chicken or vegetable broth', 'white grape juice', 'ginger ale'],
    'worcestershire sauce': ['soy sauce', 'oyster sauce', 'fish sauce'],
    'yellow mustard': ['dijon mustard', 'whole grain mustard']
}

stopwords = ['making','is','do', 'be', 'c', 'f']

class Recipe:
    def __init__(self, name, ingredientslist, nutrition, steps, ingredients, index, cookingmethods):
        self.name = name
        self.ingredientlist = ingredientslist
        self.ingredients = ingredients
        self.nutrition = nutrition
        self.steps = steps
        self.index = 0
        self.cookingmethods = cookingmethods

    def organizeInfo(self, text):
        self.name = text[0]
        nutind = 0
        for ind,t in enumerate(text):
            if 'Ingredient' in t:
                ingind = ind
            if 'Direction' in t:
                dirind = ind
            if 'Nutrition Facts (per serving)' in t:
                nutind = ind
            if 'Nutrition Facts' in t:
                if ind != nutind:
                    nutind2 = ind
        
        curr = text[ingind:dirind]
        self.ingredientlist = curr[1:]
        self.ingredients = ingredientHelper(self.ingredientlist)
        self.steps = remove_short_words(text[dirind:nutind])
        curr1 = text[nutind2:]
        curr = curr1[1:-2]
        new = remove_shorter_words(curr)
        final = {}
        for w in new:
            if contains_number(w):
                sp = split_on_number(w)
                final[sp[0]] = sp[1]
        self.nutrition = final
        self.index = 0


    def printinfo(self):
        print('Recipe name:', self.name)
        print()
        print('List of ingredients:')
        for i in self.ingredients:
            print(i,':',self.ingredients[i])
        print()
        print('Cooking steps:')
        for i in self.steps:
            print(i)
        print()
        print('Nutritional Facts:')
        for i in self.nutrition:
            print(i,':',self.nutrition[i])

    def parse_steps(self):
        cooking_methods, ingredients, tools = {}, {}, {}
        for i, step in enumerate(self.steps):
            words = step.split(' ')
            for word in words:
                word = word.lower()
                if word in COOKING_METHODS:
                    temp = cooking_methods.get(i, set())
                    temp.add(word)
                    cooking_methods[i] = temp
                if word in TOOLS: # deal with "skillet or pan" just including both in list rn
                    temp = tools.get(i, set())
                    temp.add(word)
                    tools[i] = temp
                elif word in VERB_TO_TOOL:
                    temp = tools.get(i, set())
                    for tool in VERB_TO_TOOL[word]:
                        temp.add(tool)
                    tools[i] = temp
            for ing in self.ingredients:
                if ing in step:
                    temp = ingredients.get(ing, set())
                    temp.add(ing)
                    ingredients[i] = temp


        return cooking_methods, ingredients, tools

def remove_short_words(list_of_strings):
    return [string for string in list_of_strings if len(string.split()) > 3]

def remove_shorter_words(list_of_strings):
    return [string for string in list_of_strings if len(string.split()) > 1]

def contains_number(string):
    return bool(re.search(r'\d', string))

def split_on_number(string):
    match = re.search(r'(\D+)(\d.*)', string)
    if match:
        return [match.group(1), match.group(2)]
    else:
        return [string]

def scrape(url_input):
    url = url_input
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text()

    new_text = text[:text.find("Recipe")] + '  Prep Time' + text[text.find("Prep Time", text.find("Recipe")) + len("Prep Time"):]
    new_text = new_text[:new_text.find('**')]
    new_text = re.sub('Dotdash', '  ', new_text)
    new_text = re.sub(r'\s{3,}', '. ', new_text)
    new_text = re.sub(r'\.{2,}', '.', new_text)
    new_text = re.sub(r';', '.', new_text)


    out = tokenize.sent_tokenize(new_text)
    for i,k in enumerate(out):
        k = k.replace('\n',' ')
        pattern = re.compile(r'\d+\.\d+.*')
        if not pattern.match(k):
            out[i] = re.sub('\.','', k)
    output = out[1:]
    return output

def ingredientHelper(lststr):
    outdict = {}
    string_to_tag = lststr
    for i in string_to_tag:
        if ',' in i:
            temp = i.split(',')
            t1 = tokenize.word_tokenize(temp[0])
            t = nltk.pos_tag(t1)
            word = t[-1]
            if not 'JJ' in word[1]:
                i = temp[0]
        
        if ' - ' in i:
            i = i.split(' - ')[0]

        if not i.isascii():
            pattern = re.compile(r'([\u00BC-\u00BE\u2150-\u215E])')
            i = pattern.sub(lambda x: str({
            '\u00BC': 0.25,
            '\u00BD': 0.5,
            '\u00BE': 0.75,
            '\u2152': 0.1,
            '\u2153': 0.33,
            '\u2154': 0.67,
            '\u2155': 0.2,
            '\u2156': 0.4,
            '\u2157': 0.6,
            '\u2158': 0.8,
            '\u215B': 0.125,}.get(x.group(), x.group())), i)
        
        pattern1 = re.compile(r'\d+\s\((.*)\) \w+ (.*)') #parentheses in ingredient
        pattern2 = re.compile(r'(\d+)  (.*)') #double space
        pattern3 = re.compile(r'(.*) (to\staste)') #to taste
        pattern4 = re.compile(r'(\d+ \w+) (.*)') #normal format
        pattern5 = re.compile(r'(\d+\.\d+ \w+) (.*)') #decimal
        pattern6 = re.compile(r'(\d+)\s(\d+)\.(\d+) \w+ (.*)') #number and decimal fix then use pattern 5
        match1 = pattern1.match(i)
        match2 = pattern2.match(i)
        match3 = pattern3.match(i)
        match4 = pattern4.match(i)
        match5 = pattern5.match(i)
        match6 = pattern6.match(i)
        if match1:
            newpat = re.compile(r'.*\((.*)\).*')
            #print(newpat.match(i)[0])
            outdict[match1.group(2)] = match1.group(1)
        elif match2:
            outdict[match2.group(2)] = match2.group(1)
        elif match3:
            item = match3.group(1)
            q = match3.group(2)
            splstr = item.split(' and ')
            if len(splstr)>=2:
                item1 = splstr[0]
                item2 = splstr[1]
                outdict[item1] = q
                outdict[item2] = q
            else:
                outdict[item] = q
        elif match4:
            outdict[match4.group(2)] = match4.group(1)
        elif match5:
            outdict[match5.group(2)] = match5.group(1)
        elif match6:
            parts = i.split()
            # Convert the first two parts to floats and add them together
            total = float(parts[0]) + float(parts[1])
            # Combine the total with the rest of the string
            i = f"{total} {' '.join(parts[2:])}"
            newmatch = pattern5.match(i)
            outdict[newmatch.group(2)] = newmatch.group(1) 
    return outdict

def generate_recipe(url):
    r = Recipe
    text = scrape(url) #https://www.allrecipes.com/recipe/11691/tomato-and-garlic-pasta/
    #https://www.allrecipes.com/recipe/16354/easy-meatloaf/
    Recipe.organizeInfo(r, text)
    return r

def generate_youtube(command):
    command_words = command.split(' ')
    link = "https://www.youtube.com/results?search_query="
    for word in command_words:
        link = link + "+" + str(word)
    print("This link should help: " + link)

def generate_google(command):
    command_words = command.split(' ')
    link = "https://www.google.com/search?q="
    for word in command_words:
        link = link + "+" + str(word)
    print("This link should help: " + link)

def generate_substitute(ingredient):
    if ingredient in SUBSTITIONS:
        for i in SUBSTITIONS[ingredient]:
            print(i)
    else:
        generate_google('what is a substitute for ' + str(ingredient))

def remy(rec):
    r = rec
    cooking_methods, ingredients, tools = r.parse_steps(r)
    while r.index < len(r.steps) - 1:
        print(r.steps[r.index])
        command = input().lower()
        if command == "quit" or command == "q" or command =='done' or command == 'exit':
            return
        elif ("show" in command and "ingredient" in command) or command == '1':
            printingredients(r)
            print('What would you like to do now?')
            continue
        elif "repeat" in command:
            continue
        elif  "next" in command or command ==  "":
            r.index += 1
        elif "last" in command or "back" in command or "previous" in command:
            if r.index == 0:
                print('You are at the first step')
            else: 
                r.index -=1
        elif ("step" in command and ("go" in command or "jump" in command or "skip" in command) and "to" in command):
            pattern = re.compile(r'.*(\d+).*')
            mat = pattern.match(command)
            n = int(mat.group(1))
            if n>=len(r.steps):
                print('This is not a valid step number')
            else:
                r.index = n
        elif command == "what":
            pass
        elif command == "do what": # can generalize these to checking in a list of similar possible inputs
            print(", ".join(cooking_methods.get(r.index, cooking_methods.get(r.index - 1, [r.steps[r.index]]))))
            continue
        elif command == "to what":
            print(", ".join(ingredients.get(r.index, ingredients.get(r.index - 1, ["No ingredients"])))) # only looks one step back. maybe keep as a variable instead
            continue
        elif command == "how much":
            printed = False
            step_ingredients = ingredients.get(r.index, ingredients.get(r.index - 1, ["No ingredients"]))
            for ingredient in r.ingredients:
                for i in step_ingredients:
                    if re.search(i, ingredient):
                        printed = True
                        print(ingredient)
            if printed: continue
            print("No ingredients")
        elif command == "with what":
            print(", ".join(tools.get(r.index, tools.get(r.index - 1, ["Use what you have"]))))
            continue
        command_words = command.split(' ')
        if command_words[0] == 'how':
            link = "https://www.youtube.com/results?search_query="
            for word in command_words:
                link = link + "+" + str(word)
            print("This link should help: " + link)

        #print(r.steps[r.index])
        #print(nltk.pos_tag(tokenize.word_tokenize(r.steps[r.index].lower())))

    print("Bon Apetit! :)")

def RecipeDaddy():
    url = input('Hi! Please enter the URL of the recipe you would like help with: ')
    r = generate_recipe(url)
    print('Looks like we are making',r.name)
    valid = True
    while valid:
        print('Would you like to [1] go over the ingredients or [2] jump right into the cooking steps?')
        choice = input()
        if choice == 'exit' or choice == 'stop' or choice =='quit':
            valid = False
            return
        elif choice == '1':
            printingredients(r)
            print('Shall we go through the steps now? y/n')
            c = input()
            if c == 'y':
                valid = False
                remy(r)

        elif choice == '2':
            valid = False
            remy(r)
        else:
            print('Hmm I do not understand what you want me to do')
    
def get_methods(text):
    verblist = []
    tokens = tokenize.word_tokenize(text.lower())
    tags = nltk.pos_tag(tokens)
    pattern = re.compile(r'VB.?')
    bad = re.compile(r'VBN|VBD')
    for i, temp in enumerate(tags):
        word = temp[0]
        tag = temp[1]
        if word not in stopwords:
            if i == 0 and not pattern.match(tag):
                notfound = True
                for w,t in tags:
                    if t == 'NN' and notfound and w not in stopwords:
                        verblist.append(w)
                        notfound = False
            elif pattern.match(tag):
                if bad.match(tag):
                    continue
                elif i+1 < len(tags):
                    next = tags[i+1]
                    if next[1] == 'NN' and next[0] not in stopwords:
                        bigram = word + ' ' + next[0]
                        verblist.append(bigram)
                    else:
                        verblist.append(word)
                else:
                    verblist.append(word)
    if len(verblist) == 0:
        verblist.append(tokens[0])
    verblist = list(set(verblist))
    return verblist

def printingredients(r):
    for i in r.ingredientlist:
        print(i)
    print()
    print()

RecipeDaddy()

