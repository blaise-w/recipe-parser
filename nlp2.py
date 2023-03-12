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

MEAT_INGREDIENTS = ["beef", "pork", "chicken", "lamb", "venison", "turkey", "duck", "goose", "quail", 
"rabbit", "boar", "elk", "bison", "kangaroo", "buffalo", "veal", "ham", "bacon", "sausage", "chorizo", 
"pepperoni", "prosciutto", "salami", "pastrami", "corned beef", "ground beef", "ground pork", "ground chicken", 
"ground turkey", "ground lamb", "ground venison", "ground bison", "ground elk", "ground kangaroo", 
"ground buffalo", "beef jerky", "pork belly", "liver", "sweetbreads", "oxtail", "short ribs", "ribeye",
 "filet mignon", "sirloin", "flank steak", "skirt steak", "picanha", "brisket", "pork chops", "pork tenderloin", 
 "rack of lamb", "leg of lamb", "lamb chops", "chicken breasts", "chicken thighs", "chicken wings", 
 "chicken legs", "chicken drumsticks", "whole chicken", "turkey breast", "turkey legs", "turkey wings", 
 "duck breast", "duck legs", "rabbit legs", "boar chops", "boar tenderloin", "elk chops", "elk tenderloin",
  "bison burgers", "bison ribeye", "bison tenderloin", "kangaroo burgers", "kangaroo loin", "buffalo burgers",
   "buffalo ribeye", "buffalo tenderloin"]

VEGETARIAN_SUBSTITUTIONS = substitutions = {
    "beef": "mushrooms",
    "pork": "jackfruit",
    "chicken": "tofu",
    "lamb": "seitan",
    "venison": "eggplant",
    "turkey": "tempeh",
    "duck": "mushrooms",
    "goose": "mushrooms",
    "quail": "tofu",
    "rabbit": "portobello mushrooms",
    "boar": "mushrooms",
    "elk": "portobello mushrooms",
    "bison": "tofu",
    "kangaroo": "portobello mushrooms",
    "buffalo": "tofu",
    "veal": "tofu",
    "ham": "soy ham",
    "bacon": "tempeh bacon",
    "sausage": "veggie sausage",
    "chorizo": "soyrizo",
    "pepperoni": "veggie pepperoni",
    "prosciutto": "vegetarian prosciutto",
    "salami": "veggie salami",
    "pastrami": "vegetarian pastrami",
    "corned beef": "veggie corned beef",
    "ground beef": "textured vegetable protein",
    "ground pork": "textured vegetable protein",
    "ground chicken": "textured vegetable protein",
    "ground turkey": "textured vegetable protein",
    "ground lamb": "textured vegetable protein",
    "ground venison": "textured vegetable protein",
    "ground bison": "textured vegetable protein",
    "ground elk": "textured vegetable protein",
    "ground kangaroo": "textured vegetable protein",
    "ground buffalo": "textured vegetable protein",
    "beef jerky": "tofu jerky",
    "pork belly": "smoked tofu",
    "liver": "mushrooms",
    "sweetbreads": "tofu",
    "oxtail": "mushrooms",
    "short ribs": "tempeh",
    "ribeye": "portobello mushrooms",
    "filet mignon": "grilled tofu",
    "sirloin": "portobello mushrooms",
    "flank steak": "seitan",
    "skirt steak": "tofu",
    "picanha": "mushrooms",
    "brisket": "seitan",
    "pork chops": "portobello mushrooms",
    "pork tenderloin": "tofu",
    "rack of lamb": "eggplant",
    "leg of lamb": "eggplant",
    "lamb chops": "eggplant",
    "chicken breasts": "tempeh",
    "chicken thighs": "tofu",
    "chicken wings": "tempeh",
    "chicken legs": "tofu",
    "chicken drumsticks": "tofu",
    "whole chicken": "seitan",
    "turkey breast": "tempeh",
    "turkey legs": "tofurkey",
    "turkey wings": "tofurkey",
    "duck breast": "portobello mushrooms",
    "duck legs": "portobello mushrooms",
    "rabbit legs": "eggplant",
    "boar chops": "portobello mushrooms",
    "boar tenderloin": "grilled tofu",
    "elk chops": "portobello mushrooms",
    "elk tenderloin": "grilled tofu",
    "bison burgers": "tofu burgers",
    "bison ribeye": "portobello mushrooms",
    "bison tenderloin": "grilled tofu",
    "kangaroo burgers": "tofu burgers",
    "kangaroo loin": "portobello mushrooms",
    "buffalo burgers": "tofu burgers",
    "buffalo ribeye": "portobello mushrooms",
    "buffalo tenderloin": "grilled tofu"
}

VEGETARIAN_INGREDIENTS = ['mushrooms', 'jackfruit', 'tofu', 'seitan', 'eggplant', 'tempeh', 'soy ham', 'tempeh bacon', 
                          'veggie sausage', 'soyrizo', 'vegetarian prosciutto', 'veggie salami', 'vegetarian pastrami',
                         'veggie corned beef', 'textured vegetable protein', 'tofu jerky', 'smoked tofu', 'eggplant',
                         'tofurkey', 'tofu burgers', 'grilled tofu']
    
NON_VEGETARIAN_SUBSTITUTIONS = {
    'mushrooms': ['beef', 'duck', 'goose', 'boar', 'elk', 'oxtail', 'picanha', 'pork chops', 'boar chops'],
    'jackfruit': ['pork'],
    'tofu': ['chicken', 'quail', 'veal', 'short ribs', 'chicken legs', 'chicken drumsticks', 'turkey breast', 'rabbit legs', 'kangaroo loin', 'chicken breasts', 'chicken thighs', 'turkey legs', 'turkey wings', 'pork tenderloin'],
    'seitan': ['lamb', 'flank steak', 'brisket', 'whole chicken', 'boar tenderloin', 'bison tenderloin', 'elk tenderloin'],
    'eggplant': ['venison', 'rack of lamb', 'leg of lamb', 'lamb chops', 'duck breast', 'duck legs'],
    'tempeh': ['turkey', 'chicken wings', 'bison burgers'],
    'soy ham': ['ham'],
    'tempeh bacon': ['bacon'],
    'veggie sausage': ['sausage'],
    'soyrizo': ['chorizo'],
    'vegetarian prosciutto': ['prosciutto'],
    'veggie salami': ['salami'],
    'vegetarian pastrami': ['pastrami'],
    'veggie corned beef': ['corned beef'],
    'textured vegetable protein': ['ground beef', 'ground pork', 'ground chicken', 'ground turkey', 'ground lamb', 'ground venison', 'ground bison', 'ground elk', 'ground kangaroo', 'ground buffalo'],
    'tofu jerky': ['beef jerky'],
    'smoked tofu': ['pork belly'],
    'grilled tofu': ['filet mignon', 'bison tenderloin', 'elk tenderloin', 'boar tenderloin'],
    'tofurkey': ['turkey legs', 'turkey wings'],
    'tofu burgers': ['bison burgers', 'kangaroo burgers', 'buffalo burgers'],
    'portobello mushrooms': ['rabbit', 'ribeye', 'sirloin', 'pork tenderloin', 'duck breast', 'duck legs', 'boar chops', 'elk chops', 'buffalo ribeye']
}

HEALTHY_SUBSTITUTIONS = {
    "Butter": ["Coconut oil", "olive oil", "avocado oil", "ghee"],
    "Sugar": ["Honey", "maple syrup", "agave nectar", "stevia"],
    "White flour": ["Almond flour", "coconut flour", "oat flour", "whole wheat flour"],
    "Sour cream": ["Greek yogurt", "plain yogurt", "silken tofu"],
    "Heavy cream": ["Coconut cream", "cashew cream", "silken tofu"],
    "Cream cheese": ["Vegan cream cheese", "cashew cream", "silken tofu"],
    "Mayonnaise": ["Greek yogurt", "avocado", "hummus"],
    "Breadcrumbs": ["Almond meal", "crushed cornflakes", "panko breadcrumbs"],
    "White rice": ["Brown rice", "quinoa", "cauliflower rice"],
    "Potatoes": ["Sweet potatoes", "cauliflower", "parsnips"],
    "Pasta": ["Zucchini noodles", "spaghetti squash", "brown rice noodles"],
    "Milk": ["Almond milk", "coconut milk", "oat milk", "soy milk"],
    "Cheese": ["Nutritional yeast", "vegan cheese", "tofu"],
    "Beef": ["Turkey", "chicken", "tempeh", "portobello mushrooms"],
    "Pork": ["Turkey", "chicken", "tempeh", "portobello mushrooms"],
    "Chicken": ["Turkey", "tofu", "tempeh"],
    "Lamb": ["Grilled eggplant", "tempeh"],
    "Fish": ["Tofu", "tempeh"],
    "Shrimp": ["Tofu", "tempeh"],
    "Bacon": ["Turkey bacon", "tempeh bacon", "coconut bacon"],
    "Sausage": ["Veggie sausage", "tempeh sausage"],
    "Hot dogs": ["Veggie dogs", "tofu dogs"],
    "Ground beef": ["Lentils", "black beans", "mushrooms", "textured vegetable protein"],
    "Eggs": ["Tofu", "chickpea flour"],
    "Vegetable oil": ["Coconut oil", "avocado oil"],
    "Canola oil": ["Coconut oil", "avocado oil"],
    "Salt": ["Sea salt", "pink Himalayan salt", "herbs and spices"]
}

UNHEALTHY_SUBSTITUTIONS = {
    "Coconut oil": ["Butter", "Vegetable oil", "Canola oil"],
    "olive oil": ["Butter"],
    "avocado oil": ["Butter", "Vegetable oil", "Canola oil"],
    "ghee": ["Butter"],
    "Honey": ["Sugar"],
    "maple syrup": ["Sugar"],
    "agave nectar": ["Sugar"],
    "stevia": ["Sugar"],
    "Almond flour": ["White flour"],
    "coconut flour": ["White flour"],
    "oat flour": ["White flour"],
    "whole wheat flour": ["White flour"],
    "Greek yogurt": ["Sour cream"],
    "plain yogurt": ["Sour cream"],
    "silken tofu": ["Sour cream", "Heavy cream", "Cream cheese"],
    "Coconut cream": ["Heavy cream"],
    "cashew cream": ["Heavy cream", "Cream cheese"],
    "avocado": ["Mayonnaise"],
    "hummus": ["Mayonnaise"],
    "Almond meal": ["Breadcrumbs"],
    "crushed cornflakes": ["Breadcrumbs"],
    "panko breadcrumbs": ["Breadcrumbs"],
    "Brown rice": ["White rice"],
    "quinoa": ["White rice"],
    "cauliflower rice": ["White rice"],
    "Sweet potatoes": ["Potatoes"],
    "cauliflower": ["Potatoes"],
    "parsnips": ["Potatoes"],
    "Zucchini noodles": ["Pasta"],
    "spaghetti squash": ["Pasta"],
    "brown rice noodles": ["Pasta"],
    "Almond milk": ["Milk"],
    "coconut milk": ["Milk"],
    "oat milk": ["Milk"],
    "soy milk": ["Milk"],
    "Nutritional yeast": ["Cheese"],
    "vegan cheese": ["Cheese"],
    "tofu": ["Cheese", "Chicken", "Fish", "Shrimp"],
    "Turkey": ["Beef", "Pork", "Bacon"],
    "chicken": ["Beef", "Pork", "Turkey"],
    "tempeh": ["Beef", "Pork", "Chicken", "Lamb", "Fish", "Shrimp", "Bacon", "Sausage"],
    "portobello mushrooms": ["Beef", "Pork"],
    "Grilled eggplant": ["Lamb"],
    "Tofu": ["Fish", "Shrimp", "Eggs"],
    "Turkey bacon": ["Bacon"],
    "tempeh bacon": ["Bacon"],
    "coconut bacon": ["Bacon"],
    "Veggie sausage": ["Sausage"],
    "tempeh sausage": ["Sausage"],
    "Veggie dogs": ["Hot dogs"],
    "tofu dogs": ["Hot dogs"],
    "Lentils": ["Ground beef"],
    "black beans": ["Ground beef"],
    "mushrooms": ["Ground beef"],
    "textured vegetable protein": ["Ground beef"],
    "chickpea flour": ["Eggs"],
    "Sea salt": ["Salt"],
    "pink Himalayan salt": ["Salt"],
    "herbs and spices": ["Salt"]
}

MEXICAN_SUBSTITUTIONS = {
    "Butter": ["Lard"],
    "Sugar": ["Piloncillo", "honey", "agave nectar"],
    "White flour": ["Masa harina", "all-purpose flour"],
    "Sour cream": ["Crema Mexicana"],
    "Heavy cream": ["Crema Mexicana", "evaporated milk"],
    "Cream cheese": ["Queso fresco"],
    "Mayonnaise": ["Sour cream"],
    "Breadcrumbs": ["Tortilla chips", "cornmeal"],
    "White rice": ["Spanish rice", "Mexican-style rice"],
    "Potatoes": ["Sweet potatoes", "yuca"],
    "Pasta": ["Nopales", "rice noodles"],
    "Milk": ["Evaporated milk"],
    "Cheese": ["Queso fresco", "Cotija cheese", "Oaxaca cheese"],
    "Beef": ["Carne asada", "ground beef"],
    "Pork": ["Carnitas", "chorizo"],
    "Chicken": ["Pollo asado", "shredded chicken"],
    "Lamb": ["Barbacoa"],
    "Fish": ["Tilapia", "red snapper"],
    "Shrimp": ["Camarones al ajillo"],
    "Bacon": ["Chorizo"],
    "Sausage": ["Chorizo"],
    "Hot dogs": ["Chorizo"],
    "Ground beef": ["Picadillo"],
    "Eggs": ["Huevos rancheros"],
    "Canola oil": ["Lard", "vegetable oil"],
    "Salt": ["Sea salt", "pink Himalayan salt", "cilantro", "cumin"]
}



GENERAL_INGREDIENTS = [
    "beef", "pork", "lamb", "chicken", "turkey", "duck", "salmon",
    "cod", "tuna", "shrimp", "crab", "lobster", "tofu", "tempeh",
    "onion", "garlic", "ginger", "carrot", "celery", "potato", "sweet potato",
    "broccoli", "cauliflower", "spinach", "kale", "arugula", "lettuce",
    "tomato", "cucumber", "bell pepper", "chili pepper", "mushroom",
    "rice", "quinoa", "pasta", "bread", "flour", "sugar", "salt", "pepper",
    "olive oil", "vegetable oil", "coconut oil", "sesame oil", "peanut oil",
    "soy sauce", "teriyaki sauce", "fish sauce", "oyster sauce", "hoisin sauce",
    "honey", "maple syrup", "agave syrup", "molasses", "brown sugar",
    "mustard", "ketchup", "mayonnaise", "sour cream", "cream cheese", "butter",
    "cheddar cheese", "parmesan cheese", "feta cheese", "mozzarella cheese",
    "milk", "yogurt", "egg", "baking powder", "baking soda", "yeast",
    "cumin", "coriander", "paprika", "cinnamon", "nutmeg", "cloves",
    "chili powder", "curry powder", "garam masala", "turmeric", "bay leaves",
    "thyme", "rosemary", "basil", "oregano", "parsley", "cilantro",
    "lemon", "lime", "orange", "grapefruit", "apple", "banana", "avocado",
    "pineapple", "mango", "peach", "pear", "plum", "coconut", "raisins",
    "almonds", "cashews", "walnuts", "peanuts", "pistachios", "sunflower seeds",
    "pumpkin seeds", "flaxseed", "chia seeds", "oats", "granola", "chocolate chips",
    "cocoa powder", "vanilla extract", "red wine", "white wine", "beer", "rum",
    "whiskey", "vodka", "gin", "tequila", "brandy", "campari", "aperol",
    "lemon juice", "lime juice", "orange juice", "cranberry juice", "grape juice",
    "apple cider vinegar", "balsamic vinegar", "red wine vinegar", "white wine vinegar"
]

SUBSTITUTIONS = {
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
    'milk': ['soy milk', 'almond milk', 'coconut milk'],
    'mustard': ['wasabi'],
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
    'tomato sauce': ['salsa', 'marinara sauce'],
    'shallot': ['onion', 'garlic', 'chives'],
    'shrimp': ['prawns', 'scallops', 'crab'],
    'sour cream': ['greek yogurt', 'creme fraiche'],
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
                if word in TOOLS:
                    temp = tools.get(i, set())
                    temp.add(word)
                    tools[i] = temp
                elif word in VERB_TO_TOOL:
                    temp = tools.get(i, set())
                    for tool in VERB_TO_TOOL[word]:
                        temp.add(tool)
                    tools[i] = temp
            for ing in self.ingredients:
                #print(ing)
                if ing in step:
                    temp = ingredients.get(i, set())
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
        found = False
        for j in GENERAL_INGREDIENTS:
            if j in i.lower():
                found = True
                rep = j
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
            if found:
                outdict[rep] = match1.group(1)
            else:
                outdict[match1.group(2)] = match1.group(1)
        elif match2:
            if found:
                outdict[rep] = match2.group(1)
            else:
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
            if found:
                outdict[rep] = match4.group(1)
            else:
                outdict[match4.group(2)] = match4.group(1)
        elif match5:
            if found:
                outdict[rep] = match5.group(1)
            else:
                outdict[match5.group(2)] = match5.group(1)
        elif match6:
            parts = i.split()
            # Convert the first two parts to floats and add them together
            total = float(parts[0]) + float(parts[1])
            # Combine the total with the rest of the string
            i = f"{total} {' '.join(parts[2:])}"
            newmatch = pattern5.match(i)
            if found:
                outdict[rep] = newmatch.group(1) 
            else:
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
    return "This link should help: " + link

def generate_google(command):
    command_words = command.split(' ')
    link = "https://www.google.com/search?q="
    for word in command_words:
        link = link + "+" + str(word)
    return "This link should help: " + link

def generate_substitute(ingredient):
    if ingredient in SUBSTITUTIONS:
        for i in SUBSTITUTIONS[ingredient]:
            print(i)
    else:
        print(generate_google('what is a substitute for ' + str(ingredient)))

def remy(rec):
    r = rec
    cooking_methods, ingredients, tools = r.parse_steps(r)
    while r.index < len(r.steps) - 1:
        step = r.steps[r.index]
        print(step)
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
            if mat:
                n = int(mat.group(1))
                if n>=len(r.steps):
                    print('This is not a valid step number')
                else:
                    r.index = n
            else:
                print('If you are trying to skip to a step, please have the step number in numeric form.')
        elif 'how' in command:
            temp = True
            if 'much' in command or 'many' in command:
                for key, val in r.ingredients.items():
                    if key in step:
                        print(val,'of',key)
                        temp = False
                        continue
                if temp:
                    print(generate_google(str(command)+' to '+str(step.lower())))
            elif 'long' in command:
                print(getTime(step))
            else:
                print(generate_youtube('how do i ' + str(step.lower())))
        elif 'when' in command:
            print(getTime(step))
        elif 'what' in command:
            if 'do' in command and not 'to' in command:
                print(", ".join(cooking_methods.get(r.index, get_methods(step))))
                continue
            elif 'ingredient' in command or 'using' in command or 'with' in command or 'to ' in command:
                print(", ".join(ingredients.get(r.index, ingredients.get(r.index - 1, [generate_google(str(command)+ ' ' + str(step))]))))
            elif 'use' in command:
                print(", ".join(tools.get(r.index, tools.get(r.index - 1, ["Use what you have"]))))
            elif 'temperature' in command:
                print(getTemperature(step))
            elif 'what is' in command:
                print(generate_google(command))
            else:
                continue
        elif 'substitut' in command:
            notfound = True
            for i in r.ingredients:
                if i in command:
                    notfound = False
                    if i in SUBSTITUTIONS:
                        subs = ", ".join(SUBSTITUTIONS[i])
                        print('You can substitute', subs, 'for', i)
                    else:
                        print(generate_google('substitute ingredient for '+i))
            if notfound:
                print(generate_google(command))
        else:
            print('I\'m not really sure what you are trying to say')
            print('Perhaps you would find the following links useful')
            print(generate_google(command))
            print(generate_youtube(command))

    print("Bon Apetit my child! :)")

def RecipeDaddy():
    print('Hi I\'m Recipe Daddy! :)')
    url = input('Please enter the URL of the recipe you would like help with: ')
    r = generate_recipe(url)
    print('Looks like we are making',r.name)
    valid = True
    while valid:
        print('Would you like to [1] go over the ingredients or [2] jump right into the cooking steps or [3] transform the recipe?')
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

        elif choice == '3':
            transformRecipe(r)

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
    for i,k in r.ingredients.items():
        print(i, ':', k)
    print()
    print()

def getTime(text1):
    text = text1.lower()
    pat = re.compile(r'.* (\d+) (minutes?|hours?|seconds?)')
    mat = pat.match(text)
    if mat:
        out = str(mat.group(1)) +' '+ str(mat.group(2))
    else:
        out = generate_google('how long to '+str(text))
    return out

def getTemperature(text1):
    text = text1.lower()
    pat = re.compile(r'.* (\d+ degrees .).*')
    match = pat.match(text)
    if match:
        return match.group(1)
    else:
        return generate_google('what temperature should i '+str(text))

def vegTransform(rec):
    r = rec
    ingreds = list(r.ingredients.keys())
    changed_ingredients = {}
    meat_change = []
    for i in ingreds:
        if i in MEAT_INGREDIENTS:
            name = VEGETARIAN_SUBSTITUTIONS[i]
            changed_ingredients[name] = r.ingredients[i]
            meat_change.append(i)
        else:
            changed_ingredients[i] = r.ingredients[i]

    steps = r.steps
    newsteps = []
    for i in steps:
        curr = i
        for ing in meat_change:
            if ing in i:
                veg = VEGETARIAN_SUBSTITUTIONS[ing]
                curr = i.lower().replace(ing,veg)
        newsteps.append(curr)
    r.ingredients = changed_ingredients
    r.steps = newsteps
    return r

def nonvegTransform(rec):
    r = rec
    ingreds = list(r.ingredients.keys())
    changed_ingredients = {}
    meat_change = []
    sub = {}
    for i in ingreds:
        if i in VEGETARIAN_INGREDIENTS:
            name = NON_VEGETARIAN_SUBSTITUTIONS[i]
            print('Found the following substitutions for',i)
            print(name)
            c = input('Which would you like to use? ')
            changed_ingredients[c] = r.ingredients[i]
            meat_change.append(i)
            sub[i] = c
        else:
            changed_ingredients[i] = r.ingredients[i]

    steps = r.steps
    newsteps = []
    for i in steps:
        curr = i
        for ing in meat_change:
            if ing in i:
                veg = sub[ing]
                curr = i.lower().replace(ing,veg)
        newsteps.append(curr)
    r.ingredients = changed_ingredients
    r.steps = newsteps
    return r 

choiceToTransformation = {'1' : ''}

    
def transformRecipe(r):
    print("How would you like to transform this recipe? [1] to vegetarian, [2] from vegetarian, [3] to healthy, [4] to unhealthy, [5] to Mexican, [6] Lactose-free, [7] Gluten-free")
    choice = input()

    if choice == '1':


    print("Recipe transformed to ")

rec = generate_recipe('https://www.allrecipes.com/recipe/244716/shirataki-meatless-meat-pad-thai/')
rec = nonvegTransform(rec)
rec.printinfo(rec)
# RecipeDaddy()