from bs4 import BeautifulSoup
from urllib.request import urlopen
from nltk import tokenize
from nltk import pos_tag
from nltk import RegexpParser
import re

COOKING_METHODS = ['boil', 'bake', 'fry', 'broil', 'steam', 'roast', 'airfry', 'cook', 'freeze', 'melt', 'saute', 'sauté', 'grill', 'melt', 'stirring', 'pour', 'dice', 'mince', 'heat', 'keep warm', 'reduce heat'] # two word instructions ??
INGREDIENTS = ['tomatoes', 'pasta', 'oil', 'garlic', 'tomato paste', 'salt', 'pepper', 'basil', 'cheese', 'water']
# edge case tomato versus tomato paste?? idk
TOOLS = ['skillet', 'pan', 'pot', 'bowl', 'knife', 'oven']

VERB_TO_TOOL = {'drain':['colander'],'simmer':['pan'],'peel':['peeler','knife'],'boil':['pot'],'bake':['oven'],'airfry':['airfryer'],'saute':['spatula','pan'],'sauté':['spatula','pan'],'cut':['knife'],'chop':['knife'],'stir':['spatula','wooden spoon'],'mix':['spatula','wooden spoon']}

class Recipe:
    def __init__(self, name, ingredients, nutrition, steps):
        self.name = name
        self.ingredients = ingredients
        self.nutrition = nutrition
        self.steps = steps
        self.index = 0

    def __str__(self):
        return f"{self.name} Recipe:\nIngredients: {self.ingredients}\nNutritional Information: {self.nutrition}\nSteps: {self.steps}"

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
        self.ingredients = curr[1:]
        # turn this into a dictionary?^
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
            print(i)
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
                if word in INGREDIENTS:
                    temp = ingredients.get(i, set())
                    temp.add(word)
                    ingredients[i] = temp
                if word in TOOLS: # deal with "skillet or pan" just including both in list rn
                    temp = tools.get(i, set())
                    temp.add(word)
                    tools[i] = temp
                elif word in VERB_TO_TOOL:
                    temp = tools.get(i, set())
                    for tool in VERB_TO_TOOL[word]:
                        temp.add(tool)
                    tools[i] = temp


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

    out = tokenize.sent_tokenize(new_text)
    for i,k in enumerate(out):
        k = k.replace('\n',' ')
        out[i] = re.sub('\.','', k)
    output = out[1:]
   #print(output)
    return output

def generate_recipe(url):
    r = Recipe
    text = scrape(url) #https://www.allrecipes.com/recipe/11691/tomato-and-garlic-pasta/
    Recipe.organizeInfo(r, text)
    return r



def bot():
    url = input('Enter the link to the recipe: ')
    r = generate_recipe(url)
    #Recipe.printinfo(r)
    #print("hey \n")
    cooking_methods, ingredients, tools = r.parse_steps(r)
    print(r.steps[r.index])

    while r.index < len(r.steps) - 1:
        command = input().lower()
        if command == "next" or command ==  "":
            r.index += 1
        elif command == "last" or command == "back":
            if r.index != 0:
                r.index -=1
        elif command == "what":
            pass
        elif command == "quit" or command == "q":
            break
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

        print(r.steps[r.index])

    print("Bon Apetit! :)")



bot()